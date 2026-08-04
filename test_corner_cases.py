#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""未测过的代码路径：wanderer / 看 verb / 帮工 / 中文菜谱"""
import _testutil
from market_engine import MarketGame
from market_data import STALLS, WANDERING_STALLS, HIDDEN_RECIPES
from market_recipes import RECIPES


def check(name, cond, detail=""):
    if cond:
        print(f"  [OK] {name}")
    else:
        print(f"  [FAIL] {name}: {detail}")


def section(t):
    print(f"\n─── {t} ───")


# ============================================================
section("流动摊 (Wandering stalls)")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 逛菜场看是否包含流动摊
r = g.cmd("菜场")
# 流动摊有时段限制，尝试去 wander_ 开头的
wander_ids = [s["id"] for s in WANDERING_STALLS]
print(f"  流动摊 ids: {wander_ids[:3]}")
# 不一定都存在当日，但至少 cmd 不崩
for wid in wander_ids:
    r = g.cmd(f"去 {wid}")
    # 不崩就行
check("去任意流动摊不崩", True)


# ============================================================
section("看 verb 各种变体")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
# 各种"看"
for cmd in ("看", "看看", "细看", "看 小白菜", "细看 小白菜",
            "细看 摊主", "细看 秤", "细看 西红柿",
            "看 小白菜 大白菜", "细看 我不知道什么"):
    r = g.cmd(cmd)
    if not isinstance(r, str):
        check(f"看 cmd={cmd!r}", False, detail=f"reply 非 str: {type(r)}")
        break
else:
    check("所有看 verb 不崩", True)


# ============================================================
section("帮工事件触发")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.budget = 100
# 帮工 cmd 是数字选择
g.cmd("去 meat_1")
r = g.cmd("1")  # 选第一个 option
check("帮工选 1 不崩", isinstance(r, str))


# ============================================================
section("菜谱可见")
# ============================================================
print(f"  RECIPES count: {len(RECIPES)}")
print(f"  HIDDEN_RECIPES count: {len(HIDDEN_RECIPES)}")
check("至少有一些公开菜谱", len(RECIPES) > 0)
check("至少有一些隐藏菜谱", len(HIDDEN_RECIPES) > 0)


# ============================================================
section("多日 wanderer 时段切换")
# ============================================================
_testutil.reset()
g = MarketGame()
for day in range(5):
    g.cmd("菜场")
    # 逛菜场看流动摊是否出现
    r = g.cmd("菜场")
    # 检查 reply 中是否提到流动摊（关键字符：流动 / wander）
    print(f"  day={g.day}: 菜场 reply 长度={len(r)}, 含'流动'={('流动' in r or '老农' in r or '外' in r)}")
check("5 天逛菜场不崩", isinstance(r, str))


# ============================================================
section("inspect 各种 item")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
# 各种 inspect 命令
for item in ("小白菜", "大白菜", "番茄", "五花肉", "豆腐", "鲫鱼", "香菇"):
    r = g.cmd(f"看 {item}")
    if not isinstance(r, str):
        check(f"看 {item}", False, detail=f"reply 非 str")
        break
else:
    check("看各种 item 不崩", True)


# ============================================================
section("各种 stat cmd")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
for cmd in ("状态", "声望", "冰箱", "技能", "记录", "时间", "钱",
            "看老婆", "看心情", "看看菜谱", "看 一切", "全部",
            "进度", "概览", "成就"):
    r = g.cmd(cmd)
    if not isinstance(r, str):
        check(f"cmd {cmd!r}", False, detail=f"reply 非 str")
        break
else:
    check("所有 stat cmd 不崩", True)


# ============================================================
section("极端 cmd")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
extreme_cmds = [
    "买 9999999 9999999",  # 大数字
    "买 0",  # 0 数量
    "买 0.5",  # 半斤
    "买 -1",  # 负数
    "做 不存在的菜",
    "选择 ABCDE",
    "答 x",  # 短答
    "答 ",  # 空答
    "答 " + "x" * 500,  # 长答
]
for cmd in extreme_cmds:
    r = g.cmd(cmd)
    if not isinstance(r, str):
        check(f"extreme cmd {cmd[:30]!r}", False, detail=f"非 str reply: {type(r)}")
        break
else:
    check("所有极端 cmd 不崩", True)


# ============================================================
section("去 + stall name / owner")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 用 owner 名试
for owner_keyword in ("王姐", "刘姐", "胖哥", "何大爷", "陈大爷"):
    r = g.cmd(f"去 {owner_keyword}")
    if not isinstance(r, str):
        check(f"去 {owner_keyword}", False, detail=f"非 str")
        break
else:
    check("用 owner 名去摊位不崩", True)


# ============================================================
section("save 各种 edge cases")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 连续 save/load
for _ in range(10):
    state = g.to_dict()
    g2 = MarketGame()
    g2.from_dict(state)
    state2 = g2.to_dict()
    if state.get("seed") != state2.get("seed"):
        check("10 次 save/load 后 seed 一致", False)
        break
else:
    check("10 次 save/load seed 一致", True)


print("\n=== corner cases 完成 ===")