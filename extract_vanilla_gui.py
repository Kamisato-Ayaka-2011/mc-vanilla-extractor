import json
import shutil
import tempfile
import threading
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def find_root(mc_dir, version):
    cur = version
    seen = set()
    while True:
        if cur in seen:
            raise RuntimeError(f"继承链出现循环: {cur}")
        seen.add(cur)
        vdir = mc_dir / "versions" / cur
        vjson = vdir / f"{cur}.json"
        if not vjson.exists():
            raise FileNotFoundError(f"找不到版本 json: {vjson}")
        data = load_json(vjson)
        parent = data.get("inheritsFrom")
        if not parent:
            return cur, vdir, data
        cur = parent


def extract(mc_dir, version, out_dir, new_name,
            with_libs=False, with_assets=False, log=print):
    mc_dir = Path(mc_dir)
    out_dir = Path(out_dir)

    log(f"实例: {version}")
    root_id, root_dir, root_json = find_root(mc_dir, version)
    log(f"根原版版本: {root_id}")

    root_jar = root_dir / f"{root_id}.jar"
    if not root_jar.exists():
        raise FileNotFoundError(
            f"根版本 {root_id} 的 jar 不存在: {root_jar}\n"
            f"该实例缺少原版 jar，无法恢复纯原版。"
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        out_ver = tmp / "versions" / new_name
        out_ver.mkdir(parents=True)
        shutil.copy2(root_jar, out_ver / f"{new_name}.jar")
        log("已复制原版 jar")

        new_json = dict(root_json)
        new_json["id"] = new_name
        new_json.pop("inheritsFrom", None)
        (out_ver / f"{new_name}.json").write_text(
            json.dumps(new_json, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log("已写入版本 json")

        if with_libs:
            log("复制 libraries...")
            n = 0
            for lib in root_json.get("libraries", []):
                art = lib.get("downloads", {}).get("artifact", {})
                rel = art.get("path")
                if not rel:
                    continue
                src = mc_dir / "libraries" / rel
                if src.exists():
                    dst = tmp / "libraries" / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    n += 1
            log(f"已复制 {n} 个 library 文件")

        if with_assets:
            log("复制 assets（可能较大，请稍候）...")
            idx = root_json.get("assetIndex", {}).get("id")
            if idx:
                idx_src = mc_dir / "assets" / "indexes" / f"{idx}.json"
                if idx_src.exists():
                    idx_dst = tmp / "assets" / "indexes" / f"{idx}.json"
                    idx_dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(idx_src, idx_dst)
                    objects = load_json(idx_src).get("objects", {})
                    n = 0
                    for obj in objects.values():
                        h = obj["hash"]
                        src = mc_dir / "assets" / "objects" / h[:2] / h
                        if src.exists():
                            dst = tmp / "assets" / "objects" / h[:2] / h
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src, dst)
                            n += 1
                    log(f"已复制 {n} 个 asset 文件")

        zip_path = out_dir / f"{new_name}_vanilla.zip"
        log("打包中...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in tmp.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(tmp))
        log(f"完成: {zip_path}")
        return zip_path


class App:
    def __init__(self, root):
        self.root = root
        root.title("MC原版实例提取器1.0")
        root.geometry("760x560")

        self.mc_dir = tk.StringVar()
        self.version = tk.StringVar()
        self.out_dir = tk.StringVar()
        self.new_name = tk.StringVar()
        self.with_libs = tk.BooleanVar(value=True)
        self.with_assets = tk.BooleanVar(value=False)

        frm = ttk.Frame(root, padding=10)
        frm.pack(fill="both", expand=True)

        # .minecraft 目录
        ttk.Label(frm, text=".minecraft 目录").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.mc_dir).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(frm, text="浏览", command=self.pick_mc).grid(row=0, column=2)

        # 实例版本
        ttk.Label(frm, text="实例版本").grid(row=1, column=0, sticky="w", pady=4)
        self.ver_box = ttk.Combobox(frm, textvariable=self.version, state="readonly")
        self.ver_box.grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Button(frm, text="刷新", command=self.refresh_versions).grid(row=1, column=2)

        # 输出目录
        ttk.Label(frm, text="输出目录").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.out_dir).grid(row=2, column=1, sticky="ew", padx=4)
        ttk.Button(frm, text="浏览", command=self.pick_out).grid(row=2, column=2)

        # 新版本名
        ttk.Label(frm, text="新版本名（可空）").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.new_name).grid(row=3, column=1, sticky="ew", padx=4)

        # 选项
        opt = ttk.Frame(frm)
        opt.grid(row=4, column=0, columnspan=3, sticky="w", pady=6)
        ttk.Checkbutton(opt, text="带 libraries（推荐）", variable=self.with_libs).pack(side="left", padx=(0, 16))
        ttk.Checkbutton(opt, text="带 assets（体积大）", variable=self.with_assets).pack(side="left")

        # 开始按钮
        self.run_btn = ttk.Button(frm, text="开始提取", command=self.start)
        self.run_btn.grid(row=5, column=0, columnspan=3, sticky="ew", pady=8)

        # 解压说明
        hint = ttk.Label(
            frm,
            text="Tips：解压后，进入解压出的 versions 文件夹，把里面的实例文件夹整个拖进 .minecraft/versions/ 即可被启动器识别。\n"
                 "         如果勾选了“带 libraries”，再把解压出的 libraries 文件夹合并到 .minecraft/libraries。",
            foreground="#666666",
            wraplength=700,
            justify="left",
        )
        hint.grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 6))

        # 日志
        self.text = tk.Text(frm, height=14, wrap="word")
        self.text.grid(row=7, column=0, columnspan=3, sticky="nsew")
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

    def log(self, msg):
        self.root.after(0, self._append_log, msg)

    def _append_log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def pick_mc(self):
        d = filedialog.askdirectory(title="选择 .minecraft 目录")
        if d:
            self.mc_dir.set(d)
            self.refresh_versions()

    def pick_out(self):
        d = filedialog.askdirectory(title="选择输出目录")
        if d:
            self.out_dir.set(d)

    def refresh_versions(self):
        mc = Path(self.mc_dir.get())
        versions_dir = mc / "versions"
        if not versions_dir.is_dir():
            self.ver_box["values"] = []
            return
        names = sorted(p.name for p in versions_dir.iterdir() if p.is_dir())
        self.ver_box["values"] = names
        if names and self.version.get() not in names:
            self.version.set(names[0])

    def start(self):
        mc, ver, out = self.mc_dir.get(), self.version.get(), self.out_dir.get()
        if not mc or not ver or not out:
            messagebox.showwarning("缺少信息", "请选择 .minecraft 目录、实例版本和输出目录。")
            return
        name = self.new_name.get().strip() or f"{ver}-vanilla"

        self.run_btn.config(state="disabled")
        self.text.delete("1.0", tk.END)
        self.log("开始...")

        def worker():
            try:
                zip_path = extract(
                    Path(mc), ver, Path(out), name,
                    with_libs=self.with_libs.get(),
                    with_assets=self.with_assets.get(),
                    log=self.log,
                )
                self.root.after(0, lambda: messagebox.showinfo("完成", f"已生成:\n{zip_path}"))
            except Exception as e:
                self.log(f"错误: {e}")
                self.root.after(0, lambda: messagebox.showerror("失败", str(e)))
            finally:
                self.root.after(0, lambda: self.run_btn.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()