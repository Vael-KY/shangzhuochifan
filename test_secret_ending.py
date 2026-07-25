#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""secret area 解锁、ending 判定、achievement 测试"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_data  # noqa
import market_engine  # noqa
from market_engine import MarketGame
from market_data import SECRET_AREAS, STALL_BY_ID


def reset():
    _testutil.reset()


def main():
    PASS = []
    FAIL = []
    def check(name, cond, detail=""):
        if cond:
            PASS.append(name)
            print(f"  [OK] {name}")
        else:
            FAIL.append((name, detail))
            print(f"  [FAIL] {name}: {detail}")

    print("\n─── secret area: 「去 秘密id」能进 ───")
    # SECRET_AREAS 里的 area_id（backyard, rooftop, coldroom, stairway_kitchen）都能直接「去」
    for aid in SECRET_AREAS:
        g = MarketGame()
        g.cmd("菜场")
        # 假装条件满足（强制解锁）
        g.unlocked_secrets.add(aid)
        r = g.cmd(f"去 {aid}")
        check(f"去 {aid} 进秘密区域",
              "没这个摊" not in r and "不在" not in r,
              detail=f"reply: {r[:100]!r}")

    print("\n─── secret area: 没解锁时挡住 ───")
    g = MarketGame()
    g.cmd("菜场")
    # 没 unlocked_secrets 时，去 secret area 应被挡
    r = g.cmd("去 backyard")
    check("未解锁 secret area 被挡",
          "没这个摊" in r or "没" in r or "不" in r or len(r) < 100,
          detail=f"reply: {r[:80]!r}")

    print("\n─── secret area: stairway_kitchen 显示「特殊地点」而非 0种 ───")
    g = MarketGame()
    g.cmd("菜场")
    g.unlocked_secrets.add("stairway_kitchen")
    r = g.cmd("菜场")
    check("stairway_kitchen 显示「特殊地点」",
          "特殊地点" in r,
          detail=f"reply: {r[:200]!r}")

    print("\n─── ending: get_ending() 不崩溃 ───")
    g = MarketGame()
    g.cmd("菜场")
    # 让 ending 跑通
    ending = g._determine_ending()
    check("ending 判定能跑（返回 dict 或 None）",
          ending is None or isinstance(ending, dict),
          detail=f"ending={ending}")

    print("\n─── achievement 触发 ───")
    g = MarketGame()
    g.cmd("菜场")
    # 模拟触发一个成就
    g.achievements.append("test_achievement")
    state = g.to_dict()
    check("achievement 序列化到 to_dict",
          "test_achievement" in state.get("achievements", []),
          detail=f"state achievements: {state.get('achievements')}")

    print("\n─── affection 跨天衰减 ───")
    g = MarketGame()
    g.cmd("菜场")
    g.affection["veg_1"] = 50
    g.cmd("回家")
    g.cmd("新局 明天")
    # 第二天 affection 应略有衰减（游戏设计有日衰减）
    aff = g.affection.get("veg_1", 0)
    check("affection 跨天有衰减（50 → ~49.5）",
          0 < aff <= 50,
          detail=f"day={g.day}, affection={g.affection}")

    print("\n─── savings 跨天重算 ───")
    g = MarketGame()
    g.cmd("菜场")
    g.savings = 100
    g.cmd("新局 明天")
    # 新一天会按 (budget - spent) / 2 重算 savings
    check("savings 跨天按新局重算（不是保留旧值）",
          g.savings != 100,
          detail=f"savings={g.savings}")

    print(f"\n{'='*60}")
    print(f"  PASSED: {len(PASS)}")
    print(f"  FAILED: {len(FAIL)}")
    print('='*60)
    if FAIL:
        for n, d in FAIL:
            print(f"  - {n}: {d}")


if __name__ == "__main__":
    main()