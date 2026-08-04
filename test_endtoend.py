#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""end-to-end 完整游戏流程，找隐藏 bug"""
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
section("完整 day: 砍价 + 买 + 做饭 + 端")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.budget = 100
g.cmd("去 meat_1")
# 砍价
g.cmd("便宜点")
# 买
r = g.cmd("买 五花肉")
print(f"  buy 五花肉 reply: {r[:100]!r}")
# 回家
g.cmd("回家")
# 做饭
g.cmd("洗 五花肉")
g.cmd("切 五花肉")
g.cmd("出锅")
g.cmd("端")
check("完整五花肉 day 走通", g.plate is not None)


# ============================================================
section("DISASTER 价格调整 + 买")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# 强制设置灾难
g._today_disaster = {"id": "rain_short", "name": "急雨"}
g._disaster_price_mod = 0.7
g._disaster_quality_mod = 0
g.cmd("去 veg_1")
g.budget = 100
# 应该 30% off（因为 quality_mod=0 不降品）
g.cmd("买 小白菜")
items = [i for i in g.basket if i["name"] == "小白菜" and not i.get("_free")]
if items:
    print(f"  disaster buy price: {items[0]['price']}")


# ============================================================
section("多日菜品 popularity（老婆口味学习）")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.cmd("买 小白菜")
g.cmd("回家")
g.cmd("洗 小白菜")
g.cmd("切 小白菜")
g.cmd("加 盐")
g.cmd("出锅")
g.cmd("端")
# 看 palate 是否更新
palate = g.palate
print(f"  after 1st 端: palate.dislikes={palate.get('dislikes', {})}, loves={palate.get('loves', {})}")
# 再做一次
g.cmd("新局 明天")
g.cmd("去 veg_1")
g.cmd("买 小白菜")
g.cmd("回家")
g.cmd("洗 小白菜")
g.cmd("切 小白菜")
g.cmd("加 盐")
g.cmd("出锅")
g.cmd("端")
print(f"  after 2nd 端: palate.dislikes={palate.get('dislikes', {})}, loves={palate.get('loves', {})}")
check("palate 是 dict", isinstance(palate, dict))


# ============================================================
section("连续新局 day 推进")
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
day_after_first = g.day

# 连续新局
for i in range(5):
    g.cmd("新局 明天")
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    g.cmd("回家")
    g.cmd("洗 小白菜")
    g.cmd("切 小白菜")
    g.cmd("出锅")
    g.cmd("端")
    if g.day != day_after_first + i + 1:
        print(f"  [WARN] day {i+1}: expected {day_after_first + i + 1}, got {g.day}")

check("连续 5 次新局 day 推进正确", g.day == day_after_first + 5,
      detail=f"day={g.day}, expected={day_after_first + 5}")


# ============================================================
section("Bargain streak")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.budget = 100
# 多次砍价 + 购买
for i in range(3):
    g.cmd("便宜点")
    r = g.cmd("买 小白菜")
print(f"  after 3 cycles: bargain_streak={g.stats.get('bargain_streak')}")
check("bargain_streak 是数字", isinstance(g.stats.get('bargain_streak'), int))


# ============================================================
section("质量分布统计")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.budget = 100
qualities = []
for _ in range(5):
    g.cmd("买 小白菜")
    paid = [i for i in g.basket if i["name"] == "小白菜" and not i.get("_free")]
    if paid:
        qualities.append(paid[-1]["quality"])
print(f"  5 次买 quality: {qualities}")
check("买出非空 quality", len(qualities) > 0 and all(q in ("great", "good", "ok", "bad", "trap") for q in qualities))


print("\n=== end-to-end 测试完成 ===")