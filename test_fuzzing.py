#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fuzzing: 让 RNG 跑 N 次完整 day,看会不会 crash 或 state 异常"""
import _testutil
from market_engine import MarketGame
from market_data import STALL_BY_ID, VEGGIES


def check(name, cond, detail=""):
    if cond:
        print(f"  [OK] {name}")
    else:
        print(f"  [FAIL] {name}: {detail}")


def section(t):
    print(f"\n─── {t} ───")


# ============================================================
section("30 轮 fuzzing: 各种 cmd 组合")
# ============================================================
import random

crashes = []
weird_states = []

# 准备一批种子 RNG，用于 fuzzing
fuzz_seeds = list(range(100))

for i, seed_int in enumerate(fuzz_seeds[:30]):
    try:
        _testutil.reset()
        g = MarketGame()
        g.seed = seed_int  # 强制固定 seed（虽然 __init__ 不接受）
        g.rng = __import__('market_engine').mulberry32(seed_int)
        g.cmd("菜场")
        g.budget = 200

        # 随机选摊位 + 随机买
        stalls = ["veg_1", "veg_2", "veg_3", "root_1", "meat_1", "meat_2",
                  "fish_1", "egg_1", "mushroom_1", "tofu_1", "dry_1",
                  "melon_1", "melon_2", "bean_1"]
        items_per_stall = {
            "veg_1": ["小白菜", "大白菜", "上海青", "菠菜", "生菜"],
            "meat_1": ["瘦猪肉", "五花肉", "排骨", "肉末"],
            "fish_1": ["鲫鱼", "草鱼", "鲈鱼"],
            "egg_1": ["鸡蛋", "咸鸭蛋"],
            "mushroom_1": ["香菇", "平菇"],
        }
        for stall in random.sample(stalls, 5):
            g.cmd(f"去 {stall}")
            stall_items = items_per_stall.get(stall, ["小白菜"])
            # sample 数量不能超过 list 长度
            sample_n = min(2, len(stall_items))
            for item in random.sample(stall_items, sample_n):
                g.cmd(f"买 {item}")
        # 回家做饭
        g.cmd("回家")
        g.cmd("洗 小白菜")
        g.cmd("切 小白菜")
        g.cmd("加 盐")
        g.cmd("出锅")
        g.cmd("端")
        # 新局
        g.cmd("新局 明天")
        # 几轮 stat cmd
        for cmd in ["声望", "状态", "冰箱", "技能", "记录"]:
            r = g.cmd(cmd)
            if not isinstance(r, str):
                crashes.append((i, seed_int, f"cmd {cmd!r}: {type(r)}"))
        # 验证 state 没坏
        if g.budget < 0:
            weird_states.append((i, seed_int, f"budget={g.budget}"))
        if not isinstance(g.basket, list):
            weird_states.append((i, seed_int, f"basket type={type(g.basket)}"))
        if not isinstance(g.fridge, list):
            weird_states.append((i, seed_int, f"fridge type={type(g.fridge)}"))
    except Exception as e:
        crashes.append((i, seed_int, f"{type(e).__name__}: {e}"))


check(f"30 轮 fuzzing 无 crash", len(crashes) == 0,
      detail=f"crashes: {crashes[:3]}")
check(f"30 轮 fuzzing state 无异常", len(weird_states) == 0,
      detail=f"weird: {weird_states[:3]}")


# ============================================================
section("100 次 save/load 内存稳定性")
# ============================================================
import sys
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.cmd("买 小白菜")
g.cmd("回家")
g.cmd("洗 小白菜")
g.cmd("切 小白菜")
g.cmd("出锅")
g.cmd("端")

initial_state = g.to_dict()
for i in range(100):
    g2 = MarketGame()
    g2.from_dict(initial_state)
    g2.to_dict()  # 触发 serialize
    del g2
check("100 次 save/load 不崩", True)


# ============================================================
section("affection 大值 / 负值")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
# 极端 affection 值
for aff in (-100, -1, 0, 100, 9999):
    g.affection["veg_1"] = aff
    try:
        r = g.cmd("去 veg_1")
        if not isinstance(r, str):
            check(f"affection={aff} visit 不崩", False, detail=f"non-str reply")
            break
    except Exception as e:
        check(f"affection={aff} visit 不崩", False, detail=str(e))
        break
else:
    check("extreme affection 值 visit 不崩", True)


# ============================================================
section("multi-day affection decay 实际值")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.affection["veg_1"] = 100
g.save()
# 跨 7 天看衰减
for day in range(7):
    g.cmd("新局 明天")
    aff = g.affection.get("veg_1", 0)
    print(f"  day {g.day}: affection[veg_1] = {aff}")
check("affection 7 天后 ≥ 0", g.affection.get("veg_1", 0) >= 0)
check("affection 7 天后 ≤ 100", g.affection.get("veg_1", 0) <= 100)


# ============================================================
section("100 次 cmd dispatch 不崩")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
crashes = []
# 100 个随机 cmd
cmds = ["菜场", "去 veg_1", "买 小白菜", "回家", "洗", "切", "出锅", "端",
        "声望", "状态", "冰箱", "技能", "记录",
        "便宜点", "抹零", "送点葱", "选择 1", "答 我喜欢",
        "新局", "看菜场", "看市场", "看 veg_1",
        "去 veg_2", "去 meat_1", "去 fish_1"]
for i in range(100):
    cmd = cmds[i % len(cmds)]
    try:
        r = g.cmd(cmd)
        if not isinstance(r, str):
            crashes.append((cmd, type(r)))
            break
    except Exception as e:
        crashes.append((cmd, str(e)))
        break
check("100 个 cmd dispatch 不崩", len(crashes) == 0, detail=f"crashes: {crashes[:3]}")


# ============================================================
section("极端 game state")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 极端 budget / spent
g.budget = 99999
g.spent = 0
g.cmd("去 meat_1")
g.cmd("买 五花肉")
check("极端 budget=99999 买不崩", True)


# ============================================================
section("很多成就 / 状态叠加")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.achievements = [f"test_ach_{i}" for i in range(50)]
g.story_progress = [f"story_{i}" for i in range(30)]
state = g.to_dict()
g2 = MarketGame()
g2.from_dict(state)
check("50 个 achievements 跨 save/load",
      len(g2.achievements) == 50)
check("30 个 story_progress 跨 save/load",
      len(g2.story_progress) == 30)


print("\n=== fuzzing 完成 ===")