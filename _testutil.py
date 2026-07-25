#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试公共工具：在 import market_engine 之前用临时 save 文件，
避免污染玩家的 market_save.json。
"""
import os
import sys
import tempfile

# 设置临时 save 文件（在所有 import 之前）
_TEST_SAVE = os.path.join(tempfile.gettempdir(), "market_save_test.json")
os.environ["MARKET_SAVE_FILE"] = _TEST_SAVE


def reset():
    """清掉测试用的临时 save。"""
    if os.path.exists(_TEST_SAVE):
        os.remove(_TEST_SAVE)


def save_path():
    return _TEST_SAVE


# 现在才 import 引擎（这样 SAVE_FILE 已经是临时路径）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_data  # noqa
import market_engine  # noqa
from market_engine import MarketGame  # noqa