#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""砍价 / 老婆反馈 / DISASTER / 食材保鲜 / 故事线 / 成就综合测试"""
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
section("砍价流程")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.budget = 200

for cmd in ("便宜点", "便宜", "便宜点吧", "能不能便宜点",
            "便宜一点", "减一点", "再便宜点", "再减点",
            "让点价", "抹零", "送点葱", "不要葱", "抹个零头"):
    r = g.cmd(cmd)
    if not isinstance(r, str):
        check(f"砍价 cmd={cmd!r} 不崩", False, detail=f"reply 非 str: {type(r)}")
        break
else:
    check("所有砍价指令不崩", True)


_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.budget = 200
g.cmd("便宜点")
g.cmd("买 小白菜")
items = [i for i in g.basket if i["name"] == "小白菜" and not i.get("_free")]
check("砍价后能买", len(items) > 0, detail=f"basket: {g.basket}")


# ============================================================
section("DISASTER 触发")
# ============================================================
_testutil.reset()
g = MarketGame()
g._today_disaster = {"id": "test_disaster", "name": "测试灾难"}
g._disaster_price_mod = 0.5
g._disaster_quality_mod = -1
state = g.to_dict()
check("disaster id 序列化", state.get("_today_disaster_id") == "test_disaster",
      detail=f"state: {state.get('_today_disaster_id')}")
check("disaster price_mod 序列化", state.get("_disaster_price_mod") == 0.5,
      detail=f"state: {state.get('_disaster_price_mod')}")


# ============================================================
section("食材保鲜")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.cmd("去 veg_1")
g.cmd("买 小白菜")
g.cmd("回家")
g.cmd("新局 明天")
g.cmd("新局 明天")
g.cmd("新局 明天")
g.cmd("新局 明天")
check("跨多天后 fridge/basket 不崩", isinstance(g.fridge, list) and isinstance(g.basket, list))


# ============================================================
section("老婆反馈 (palate / dish_feedback)")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.dish_feedback["番茄炒蛋"] = [{"text": "好吃", "day": 1, "score": 10}]
g.dish_history["番茄炒蛋"] = {"count": 1, "last": 1}
state = g.to_dict()
check("dish_feedback 序列化", state.get("dish_feedback") is not None)
check("dish_history 序列化", state.get("dish_history") is not None)


# ============================================================
section("storyline")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
# save/load 后再设，模拟"上一局的故事线跨档保留"场景
g.storyline_state["veg_1"] = {"arc": "test_arc", "day": 1}
state = g.to_dict()
g2 = MarketGame()
g2.from_dict(state)
check("storyline_state 跨 save/load 保留",
      g2.storyline_state.get("veg_1", {}).get("arc") == "test_arc",
      detail=f"g2.state: {g2.storyline_state}")


# ============================================================
section("achievement / stats")
# ============================================================
_testutil.reset()
g = MarketGame()
g.cmd("菜场")
g.stats["bargain_streak"] = 5
g.stats["unique_dishes"].add("番茄炒蛋")
state = g.to_dict()
check("stats bargain_streak 序列化", state.get("stats_bargain_streak") == 5)
check("stats unique_dishes 序列化",
      "番茄炒蛋" in state.get("stats_unique_dishes", []))


# ============================================================
section("重复 cmd")
# ============================================================
_testutil.reset()
g = MarketGame()
r = None
for _ in range(5):
    r = g.cmd("菜场")
check("重复 5 次菜场不崩", isinstance(r, str))


print("\n=== 测试完成 ===")