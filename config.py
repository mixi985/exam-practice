# -*- coding: utf-8 -*-
"""手机版 - 配置文件"""
import os
import sys
from pathlib import Path

# 判断是否运行环境（桌面 / Android）
if getattr(sys, 'frozen', False):
    # PyInstaller打包
    APP_ROOT = Path(sys.executable).parent
elif 'ANDROID_ARGUMENT' in os.environ:
    # Android 环境：使用用户可写目录
    APP_ROOT = Path(os.environ.get('ANDROID_ARGUMENT', '.'))
else:
    APP_ROOT = Path(__file__).parent

# 数据库路径
DATA_DIR = APP_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = str(DATA_DIR / "exam_practice.db")

APP_NAME = "刷题软件"
APP_VERSION = "1.0.0"

# 题型
QUESTION_TYPES = {
    "single": "单选题",
    "multiple": "多选题",
    "judgment": "判断题"
}

DEFAULT_CATEGORY = "默认分类"

# ============ 色彩 ====================
PRIMARY_COLOR = (0.365, 0.620, 0.886, 1)  # #5dade2
PRIMARY_HOVER = (0.204, 0.596, 0.859, 1)   # #3498db
PRIMARY_LIGHT = (0.922, 0.961, 0.984, 1)  # #ebf5fb

SUCCESS_COLOR = (0.345, 0.839, 0.553, 1)     # #58d68d
SUCCESS_LIGHT = (0.918, 0.980, 0.945, 1)   # #eafaf1
ERROR_COLOR = (0.925, 0.439, 0.388, 1)       # #ec7063
ERROR_LIGHT = (0.992, 0.929, 0.925, 1)        # #fdedec
WARNING_COLOR = (0.961, 0.690, 0.255, 1)    # #f5b041

BG_PRIMARY = (1, 1, 1, 1)
BG_SECONDARY = (0.973, 0.976, 0.980, 1)
BG_DARK_HOVER = (0.910, 0.957, 0.988, 1)

TEXT_PRIMARY = (0.204, 0.286, 0.369, 1)
TEXT_SECONDARY = (0.498, 0.549, 0.553, 1)
TEXT_LIGHT = (1, 1, 1, 1)
TEXT_MUTED = (0.667, 0.718, 0.722, 1)

BORDER_COLOR = (0.894, 0.910, 0.922, 1)
