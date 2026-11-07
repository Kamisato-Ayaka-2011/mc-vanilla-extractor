ZH：

# MC 纯原版实例提取器

从任意 Minecraft Java 版实例（Fabric / Forge / 整合包）中，剥离出一份干净的纯原版实例副本。**只读原实例，不修改、不删除任何文件。**

## 为什么需要它

第三方启动器的实例下载功能受限后，新玩家想拿到一份干净的原版实例变得麻烦。这个工具不依赖任何在线下载源，只从你本地已有的实例里提取原版文件。

# 使用方式

#### GUI 版（推荐）

下载 Release 里的 `extract\\\\\\\_vanilla\\\\\\\_gui.exe`，双击运行：

1. 选择 `.minecraft` 目录
2. 从下拉框选一个实例
3. 选输出目录，点“开始提取”

#### 命令行版

python extract\_vanilla.py --minecraft-dir "你的.minecraft路径" --version "实例版本名" --output "输出目录" --with-libs

## 解压后怎么用（重要）

解压 zip 后，**不要直接把整个文件夹丢进 .minecraft**。
进入解压出的 `versions` 文件夹，把里面的实例文件夹整个拖进 `.minecraft/versions/`。
如果勾选了“带 libraries”，再把解压出的 `libraries` 合并到 `.minecraft/libraries`。

## 你手里那份就是种子

这个工具不储存资源，只储存“从现有资源里提取原版”的能力。如果你手里有能跑的原版实例，别删——你手里那份就是种子。复制给下一个人，链条就不会断。

## 免责声明

输出仅含原版文件，不含任何模组。仅供学习交流。

# License

本项目基于 MIT License 开源。



EN：

# MC Vanilla Instance Extractor

Extract a clean vanilla Minecraft Java Edition instance from any existing instance — Fabric, Forge, or a modpack — without downloading anything.

**The original instance is only read. It is never modified or deleted.**

## Why this exists

In mainland China, some third-party Minecraft launchers have had their instance download features restricted. For new players, getting a clean vanilla instance has become unnecessarily difficult.

This tool does not rely on any online download source. It works entirely with files already on your disk: it follows the instance's `inheritsFrom` chain, finds the root vanilla version, and copies only the vanilla jar and metadata into a new, standalone instance.

Players outside mainland China usually don't need this — the official launcher can provide a vanilla instance directly. However, the tool still works if you need to strip a modpack down to a clean vanilla instance.

## What it does

* Reads an existing instance under `.minecraft/versions/`
* Follows `inheritsFrom` until it reaches the root vanilla version
* Copies the root vanilla `.jar` and `.json` into a new instance folder
* Rewrites the new version JSON with a new `id` and no inheritance
* Optionally copies vanilla `libraries` and `assets`
* Packages the result as a zip

## What it does not do

* It does not download Minecraft files
* It does not include mods, configs, resource packs, or saves
* It cannot recover a vanilla instance if the root vanilla jar is missing from your `.minecraft`
* It does not modify or delete your original instance

## Requirements

* **GUI EXE**: Windows, no Python required
* **Python source**: Python 3.10+
* A local `.minecraft` directory containing the instance you want to extract
* The root vanilla jar must still exist locally, e.g. `.minecraft/versions/1.20.1/1.20.1.jar`

## Usage

### GUI (recommended)

Download `extract\_vanilla\_gui.exe` from the Releases page and run it:

1. Select your `.minecraft` directory
2. Choose an instance from the dropdown
3. Choose an output directory
4. Click **Start Extraction**

The GUI also shows the post-extraction steps directly in the window.

Command line
python extract\_vanilla.py --minecraft-dir "C:\\path\\to\\.minecraft" --version "your-instance-name" --output "C:\\path\\to\\output" --with-libs
After extracting (important)
Do not unzip the whole archive directly into .minecraft.
1.Unzip the generated zip
2.Open the extracted versions folder
3.Move the instance folder inside it into .minecraft/versions/
4.If you selected Include libraries, merge the extracted libraries folder into .minecraft/libraries
HMCL and similar launchers scan direct subfolders of .minecraft/versions/, so the instance folder must sit directly there.
Your copy is a seed
This tool does not store Minecraft files. It stores the ability to extract a clean vanilla instance from files you already have.
If you have a working vanilla instance, keep it. That copy is a seed. Copy it to the next person, and the chain does not break.
Tested
A 1.21.1 vanilla instance was extracted and launched successfully in HMCL

1.20.1 Fabric modpack instance also tested
Fabric / Forge modpack instances are supported in principle, as long as the root vanilla jar still exists locally
Notes
The GUI EXE is built with PyInstaller. Windows Defender may occasionally flag it as a false positive; add it to your trusted list if needed.
The output contains only vanilla files. No mods are included.
This project is not affiliated with Mojang, Microsoft, or any launcher project.
Contributing
Compatibility reports are welcome. If something fails, please include:
Launcher and version
Loader (Fabric / Forge / vanilla)
Minecraft version
Instance name
Root vanilla version found by the tool
The terminal or GUI error message
License
MIT License. See LICENSE.

