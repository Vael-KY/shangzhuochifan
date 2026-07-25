#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""30 轮 stress test：每个 game 跑一遍完整 day 流程找异常
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _testutil  # noqa
import market_data  # noqa
import market_engine  # noqa
from market_engine import MarketGame


def main():
    errs = []
    for i in range(30):
        try:
            _testutil.reset()
            g = MarketGame()
            g.cmd("菜场")
            g.budget = 200
            for stall in ["veg_1", "veg_2", "veg_3", "meat_1", "fish_1", "egg_1"]:
                g.cmd(f"去 {stall}")
                for item in ["小白菜", "五花肉", "鸡蛋"]:
                    g.cmd(f"买 {item}")
            g.cmd("回家")
            for step in ["洗 小白菜", "切 小白菜", "加盐", "出锅", "端"]:
                g.cmd(step)
            g.cmd("新局 明天")
            g.cmd("去 root_1")
            g.cmd("买 白萝卜")
        except Exception as e:
            errs.append((i, type(e).__name__, str(e)[:200]))
    print(f"\n总轮次 30, 异常 {len(errs)}")
    for i, t, msg in errs:
        print(f"  round {i}: {t}: {msg}")


if __name__ == "__main__":
    main()