# Geinei Uploader (傻瓜版) 使用说明

这是一个专门为不懂电脑的用户设计的网站更新工具。

## 1. 准备工作 (管理员操作)

这个程序分为两个阶段。你是管理员，你需要先运行它一次来生成“钥匙”。

### 在 Windows 上打包成 EXE
如果你需要发给 Windows 用户，你需要找一台 Windows 电脑，安装 Python，然后运行：
```bash
pip install customtkinter
pyinstaller --noconsole --onefile --add-data "customtkinter;customtkinter" geinei_uploader.py
```
*(注意：`--add-data` 的语法在 Windows 上可能是 `;`，在 Linux/Mac 上是 `:`。上面的命令是针对 Windows 的)*

## 2. 第一阶段：生成钥匙 (管理员操作)

1. 运行程序 `geinei_uploader.exe` (或 .py)。
2. 因为是第一次运行，它会显示 **"第一次使用初始化"** 界面。
3. 点击 **"生成安全钥匙"**。
4. 复制显示的钥匙内容。
5. 去 GitHub 项目 -> Settings -> Deploy keys -> Add deploy key。
   - Title: `Uploader Key`
   - Key: 粘贴内容
   - **Important:** 勾选 "Allow write access" (允许写入权限)。
6. 回到软件，点击 **"我已添加，开始初始化仓库"**。
7. 如果成功，软件会进入主界面。此时，软件目录下会生成一个 `geinei_data` 文件夹。

## 3. 第二阶段：分发给小白 (用户操作)

**重要：** 你需要把生成的 `geinei_uploader.exe` **和** `geinei_data` 文件夹一起打包发给小白。
或者，你可以在小白的电脑上操作第一阶段。

小白只需要：
1. 打开软件。
2. 把更新好的网站文件（`index.html` 等）或者包含这些文件的文件夹，甚至是一个 `.zip` 压缩包，直接**拖拽**进软件窗口（或者点击中间的大图标选择）。
3. 看着进度条走完，提示“上传成功”。

## 常见问题
- **软件打不开？** 确保电脑上安装了 Git。
- **冲突怎么办？** 软件会自动强制以小白上传的文件为准，覆盖线上的旧文件（除了小白没上传的其他文件保持不变）。
