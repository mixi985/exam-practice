# 刷题软件 - 手机版 (Android APK)

## 项目结构

```
mobile_app/
├── main.py              # 主程序入口（Kivy 应用）
├── config.py            # 配置（颜色、路径）
├── database.py          # SQLite 数据库层
├── parser.py            # 题库文件解析（TXT/DOCX）
├── samples.py           # 首次启动示例题库（10道驾考示例题）
├── buildozer.spec       # Buildozer APK 打包配置
├── ui/
│   ├── theme.py         # 主题 / 通用组件（RoundedCard / 按钮）
│   ├── home_screen.py   # 首页（统计卡片 + 功能入口）
│   ├── practice_screen.py  # 刷题页（单选 / 判断 / 解析）
│   ├── list_screens.py  # 错题本 / 收藏题目列表
│   └── manage_screens.py   # 导入题库 / 分类管理
└── data/                # 运行时数据库文件（自动生成）
```

## 在 PC 上预览（推荐快速验证）

```bash
pip install kivy==2.3.0 python-docx pillow
cd mobile_app
python main.py
```

启动后会弹出一个 360x640 的窗口模拟手机界面。

## 打包为 Android APK（推荐在 Linux 环境执行）

Buildozer 是 Kivy 官方的打包工具，它会自动下载 Android SDK/NDK、
编译 Python 解释器、打包你的代码为 APK。

### 准备环境（Ubuntu 20.04 推荐）

```bash
sudo apt update
sudo apt install -y python3-pip openjdk-17-jdk unzip zip wget
pip3 install --user buildozer cython

# 在构建前先让 Buildozer 自动下载 SDK/NDK（首次耗时较长，需 ~10GB 磁盘）
cd mobile_app
buildozer android debug
```

构建完成后，APK 会生成在 `mobile_app/bin/` 目录，文件名类似：

```
bin/exampractice-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Windows 用户

Windows 上 Buildozer 需要 WSL（推荐 Ubuntu on WSL2）：

```powershell
wsl --install
# 进入 WSL 后，按上面的 Ubuntu 步骤安装并执行
```

### 安装 APK 到手机

构建出 debug APK 后：

```bash
# 方法1：adb 安装（需要手机开启 USB 调试）
adb install bin/exampractice-1.0-arm64-v8a_armeabi-v7a-debug.apk

# 方法2：直接把 APK 传到手机，在手机文件管理器中点击安装
```

### 发布版 APK（发布到应用商店）

```bash
buildozer android release
```

发布版需要为 APK 签名。可在 `buildozer.spec` 中配置：

```
# Android 签名
android.sign = True
android.keystore = /path/to/your.keystore
android.keystore.password = your_password
android.key.alias = your_alias
android.key.password = your_key_password
```

## 功能说明

| 功能 | 说明 |
|------|------|
| 顺序刷题 | 按顺序练习全部题目 |
| 随机刷题 | 随机抽取题目练习 |
| 错题本 | 自动收集做错过的题目，可回看练习 |
| 收藏题目 | 可随时收藏某道题 |
| 导入题库 | 支持 TXT / DOCX 题库文件，可选择分类 |
| 题库管理 | 新增分类、删除分类、按分类练习 |

## 题库文件格式示例

```
1. 在道路上驾驶机动车，应当遵守什么原则？
A. 左侧通行
B. 右侧通行
C. 中间通行
D. 随意通行
答案：B
解析：根据道路交通安全法，机动车应当右侧通行。

2. 饮酒后驾驶机动车的，一次记多少分？
A. 3分
B. 6分
C. 9分
D. 12分
答案：D
```

判断题可以使用“对/错”或“TRUE/FALSE”作为选项。
