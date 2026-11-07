import argparse, json, shutil, zipfile
from pathlib import Path

def load_json(p):
    return json.loads(p.read_text(encoding='utf-8'))

def find_root(mc_dir, version):
    """沿 inheritsFrom 链找到根原版版本"""
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

def extract(mc_dir, version, out_dir, new_name, with_libs=False, with_assets=False):
    root_id, root_dir, root_json = find_root(mc_dir, version)
    root_jar = root_dir / f"{root_id}.jar"
    if not root_jar.exists():
        raise FileNotFoundError(
            f"根版本 {root_id} 的 jar 不存在: {root_jar}\n"
            f"该实例缺少原版 jar，无法恢复纯原版。"
        )

    out_ver = out_dir / "versions" / new_name
    out_ver.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root_jar, out_ver / f"{new_name}.jar")

    # 改写 json：新 id，确保没有 inheritsFrom
    new_json = dict(root_json)
    new_json["id"] = new_name
    new_json.pop("inheritsFrom", None)
    (out_ver / f"{new_name}.json").write_text(
        json.dumps(new_json, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    if with_libs:
        for lib in root_json.get("libraries", []):
            art = lib.get("downloads", {}).get("artifact", {})
            rel = art.get("path")
            if not rel:
                continue
            src = mc_dir / "libraries" / rel
            if src.exists():
                dst = out_dir / "libraries" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    if with_assets:
        idx = root_json.get("assetIndex", {}).get("id")
        if idx:
            idx_src = mc_dir / "assets" / "indexes" / f"{idx}.json"
            if idx_src.exists():
                idx_dst = out_dir / "assets" / "indexes" / f"{idx}.json"
                idx_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(idx_src, idx_dst)
                objects = load_json(idx_src).get("objects", {})
                for obj in objects.values():
                    h = obj["hash"]
                    src = mc_dir / "assets" / "objects" / h[:2] / h
                    if src.exists():
                        dst = out_dir / "assets" / "objects" / h[:2] / h
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)

    # 打包
    zip_path = out_dir.parent / f"{new_name}_vanilla.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in out_dir.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(out_dir))
    return root_id, zip_path

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--minecraft-dir", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--with-libs", action="store_true")
    ap.add_argument("--with-assets", action="store_true")
    a = ap.parse_args()
    out = Path(a.output)
    new_name = a.name or f"{a.version}-vanilla"
    root, z = extract(Path(a.minecraft_dir), a.version, out, new_name,
                      a.with_libs, a.with_assets)
    print(f"根原版版本: {root}\n输出: {z}")