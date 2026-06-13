[app]
# 应用基本信息
title = 刷题软件
package.name = exampractice
package.domain = org.exampractice

# 版本号
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc,otf,db
version = 1.0

# 使用 Python3 (python-for-android)
requirements = python3, kivy==2.3.0, docutils, python-docx==1.1.0, pillow

# 屏幕方向
orientation = portrait

# 全屏显示
fullscreen = 0

# 最低 Android SDK
android.minapi = 21
android.api = 33
android.archs = arm64-v8a, armeabi-v7a

# Android 权限（仅读取存储，用于导入题库）
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 应用图标（可选，若不存在会用默认图标）
# icon.filename = %(source.dir)s/data/icon.png
# icon.filename = %(source.dir)s/data/icon.png

# 启动图
# presplash.filename = %(source.dir)s/data/presplash.png

# 应用启动入口
entrypoint = main.py

[buildozer]
# 日志等级
log_level = 2
warn_on_root = 1

# 构建输出目录
bin_dir = bin
build_dir = .buildozer
