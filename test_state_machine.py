#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""深度边界：多次 save/load、wife_state、节气、affection 复杂路径"""
import _testutil
from market_engine import MarketGame


def check(name, cond, detail=""):
    if cond:
        print(f"  [OK] {name}")
    else:
        print(f"  [FAIL] {name}: {detail}")


def section(t):
    print(f"\n─── {t} ───")


# ============================================================
section("5 次 save/load 完整一致")
# ============================================================
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
original_state = g.to_dict()
state_keys = sorted(original_state.keys())

for i in range(5):
    g2 = MarketGame()
    g2.from_dict(original_state)
    state2 = g2.to_dict()
    if sorted(state2.keys()) != state_keys:
        check(f"第 {i+1} 次 save/load key 一致", False,
              detail=f"keys diff: {set(state_keys) ^ set(state2.keys())}")
        break
else:
    check("5 次 save/load 后 keys 集一致", True)


# ============================================================
section("wife_state 跨天")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.wife_state = "大姨妈来了"
g.save()  # 手动存档，让新一天的 load 能读到
g.cmd("新局 明天")
check("wife_state 跨天保留", g.wife_state == "大姨妈来了",
      detail=f"state: {g.wife_state}")


# ============================================================
section("雨天 / 节气 effects")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 强制设置天气
g.weather = "雨"
g.cmd("去 veg_1")
g.cmd("买 小白菜")
g.cmd("回家")
# 雨天 + 节气不影响基本流程
check("雨天买 + 回家不崩", g.basket is not None)


# ============================================================
section("reputation 跨天")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.reputation = {"kind": 5, "generous": 3, "honest": 2, "regular": 1}
g.save()
g.cmd("新局 明天")
check("reputation 跨天保留",
      g.reputation == {"kind": 5, "generous": 3, "honest": 2, "regular": 1},
      detail=f"rep: {g.reputation}")


# ============================================================
section("enemies / chain_flags / found_clues 跨天")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.chain_flags.add("test_flag")
g.found_clues.add("test_clue")
g.unlocked_combos.add("test_combo")
g.save()
g.cmd("新局 明天")
check("chain_flags 跨天保留", "test_flag" in g.chain_flags)
check("found_clues 跨天保留", "test_clue" in g.found_clues)
check("unlocked_combos 跨天保留", "test_combo" in g.unlocked_combos)


# ============================================================
section("market_time 重置（每局重置）")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 把 market_time 用光
for _ in range(10):
    g.cmd("去 veg_1") if not g._market_closed else None
# 新一天应该重置
g.cmd("新局 明天")
check("新一天 market_time 重置", g.market_time > 0,
      detail=f"market_time={g.market_time}, market_closed={g._market_closed}")


# ============================================================
section("厨房状态跨天清")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.cmd("买 小白菜")
g.cmd("回家")
g.cmd("洗 小白菜")
# 不做完直接跨天
g.cmd("新局 明天")
check("新一天 kitchen_state 应该是 None 或重置",
      g.kitchen_state is None or (isinstance(g.kitchen_state, dict) and not g.kitchen_state.get("steps")),
      detail=f"kitchen_state: {g.kitchen_state!r}"[:100])


# ============================================================
section("从大 day 跨到大 day RNG 一致")
# ============================================================
_testutil.reset()
g1 = MarketGame()
g1.cmd("菜场")
# 跑很多 rng 调用
for _ in range(100):
    g1.rng()
state1 = g1.to_dict()
g2 = MarketGame()
g2.from_dict(state1)
seq1 = [g1.rng() for _ in range(50)]
seq2 = [g2.rng() for _ in range(50)]
check("100 次 rng 后 save/load 仍确定性", seq1 == seq2)


# ============================================================
section("MarketGame 大量操作不崩")
# ============================================================
_testutil.reset()
g = MarketGame()
crash = False
try:
    g.cmd("菜场")
    for stall in ("veg_1", "veg_2", "veg_3", "root_1", "root_2", "meat_1", "meat_2",
                  "fish_1", "fish_2", "egg_1", "mushroom_1", "tofu_1", "dry_1",
                  "melon_1", "melon_2", "bean_1"):
        g.cmd(f"去 {stall}")
    # 看看菜场
    g.cmd("菜场")
    # 看自己
    g.cmd("声望")
    g.cmd("冰箱")
    g.cmd("技能")
    g.cmd("菜谱")
    g.cmd("状态")
    g.cmd("记录")
except Exception as e:
    crash = True
    print(f"  CRASH: {type(e).__name__}: {e}")
check("逛遍所有摊 + 各种 stat cmd 不崩", not crash)


print("\n=== 状态机深度测试完成 ===")