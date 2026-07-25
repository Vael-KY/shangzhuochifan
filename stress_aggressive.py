#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""更激进的 stress test：边界条件、奇怪 input、多个 day 推进"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _testutil  # noqa
import market_data  # noqa
import market_engine  # noqa
from market_engine import MarketGame


def main():
    errs = []

    def run(name, fn):
        try:
            fn()
        except Exception as e:
            errs.append((name, type(e).__name__, str(e)[:200]))

    def new_game(budget=200):
        _testutil.reset()
        g = MarketGame()
        g.cmd("菜场")
        g.budget = budget
        return g

    # 测试 1：5 天推进，每天的基本操作
    def test_5_days():
        g = new_game()
        for day in range(5):
            for stall in ["veg_1", "meat_1", "fish_1"]:
                g.cmd(f"去 {stall}")
            g.cmd("买 小白菜")
            g.cmd("回家")
            g.cmd("新局 明天")
    run("5 天推进", test_5_days)

    # 测试 2：各种空 / 奇怪 input
    def test_weird_inputs():
        g = new_game()
        for cmd in ["", " ", "  ", "？", "\n", "\t",
                     "菜场菜场菜场", "买", "买 ", "去", "去 ", "去  ",
                     "细看 不存在", "细看 鲫鱼", "看 veg_1", "看 veg_2",
                     "选择 1", "选择 99", "选择 xxx",
                     "答 ", "答 我喜欢简单",
                     "声望", "冰箱", "存钱罐", "取罐",
                     "做", "快做", "端", "出锅",
                     "退出", "不玩了"]:
            try:
                r = g.cmd(cmd)
                if not isinstance(r, str):
                    errs.append((f"input {cmd!r}", "TypeError", f"reply not str: {type(r)}"))
            except Exception as e:
                errs.append((f"input {cmd!r}", type(e).__name__, str(e)[:150]))
    run("奇怪 input", test_weird_inputs)

    # 测试 3：批量买
    def test_bulk_buy():
        g = new_game(budget=500)
        g.cmd("去 veg_1")
        # 批量买多个菜
        for cmd in ["买 小白菜 2", "买 大葱 1", "买 小白菜", "买 不存在 2"]:
            r = g.cmd(cmd)
    run("批量买", test_bulk_buy)

    # 测试 4：长时间游玩（20 天）
    def test_long_play():
        g = new_game()
        for day in range(20):
            for s in ["veg_1", "meat_1"]:
                g.cmd(f"去 {s}")
                g.cmd("买 小白菜")
            g.cmd("回家")
            g.cmd("新局 明天")
    run("20 天游玩", test_long_play)

    # 测试 5：state_for_save 返回深拷贝
    def test_deep_copy():
        g = new_game()
        state = g.to_dict()
        # 修改 nested
        if "mystic_state" in state and state["mystic_state"]:
            state["mystic_state"]["confessions"].append({"test": True})
        state2 = g.to_dict()
        # 原 state 不应被污染
        for i, c in enumerate(state2.get("mystic_state", {}).get("confessions", [])):
            if c.get("test"):
                errs.append(("deep_copy", "Pollution", "state_for_save 返回 live ref"))
                break
    run("state_for_save 深拷贝", test_deep_copy)

    # 测试 6：load 空 / 损坏 / 旧版本数据
    def test_load_corruption():
        g = new_game()
        for data in [None, {}, {"save_version": 999}, {"day": -1}, {"day": 99999}]:
            g2 = MarketGame()
            try:
                g2.from_dict(data)
            except Exception as e:
                errs.append(("load corruption", type(e).__name__, f"data={data}, err={e}"))
    run("load 各种数据", test_load_corruption)

    print(f"\n总测试 {len(errs)} 个失败")
    for name, t, msg in errs:
        print(f"  - [{name}] {t}: {msg}")


if __name__ == "__main__":
    main()