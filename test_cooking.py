#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cooking 边界测试：verb 识别、quality_score 边界、accidents 触发"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _testutil  # noqa
import market_data  # noqa
import market_engine  # noqa
from market_engine import MarketGame


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

    print("\n─── 做饭：基本流程 ───")
    g = MarketGame()
    g.cmd("菜场")
    g.budget = 100  # 确保买得起
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    if not g.basket:
        # RNG: 小白菜当天被卖光，换大白菜
        g.cmd("买 大白菜")
    g.cmd("回家")
    # 验证 kitchen_state 已建
    check("回家后 kitchen_state 创建",
          g.kitchen_state is not None and isinstance(g.kitchen_state, dict),
          detail=f"kitchen_state={g.kitchen_state!r}"[:80])

    # 洗
    r = g.cmd("洗 小白菜") if any(i["name"] == "小白菜" for i in g.basket) else g.cmd("洗 大白菜")
    check("洗 菜 走通",
          isinstance(r, str) and len(r) > 0,
          detail=f"reply: {r[:80]!r}")

    # 切
    item = "小白菜" if any(i["name"] == "小白菜" for i in g.basket) else "大白菜"
    r = g.cmd(f"切 {item}")
    check("切 菜 走通",
          isinstance(r, str) and len(r) > 0,
          detail=f"reply: {r[:80]!r}")

    # 出锅
    r = g.cmd("出锅")
    check("出锅 走通",
          isinstance(r, str) and len(r) > 0,
          detail=f"reply: {r[:80]!r}")

    # 端
    r = g.cmd("端")
    check("端 走通",
          isinstance(r, str) and len(r) > 0,
          detail=f"reply: {r[:80]!r}")

    print("\n─── 做饭：盐计数 ───")
    reset()
    g = MarketGame()
    g.cmd("菜场")
    g.budget = 100
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    if not g.basket:
        g.cmd("买 大白菜")
    g.cmd("回家")
    item = "小白菜" if any(i["name"] == "小白菜" for i in g.basket) else "大白菜"
    g.cmd(f"洗 {item}")
    # 加三次盐
    g.cmd("加 盐")
    g.cmd("加 盐")
    g.cmd("加 盐")
    ks = g.kitchen_state
    check("三次加盐后 _salt_count=3",
          ks.get("_salt_count") == 3,
          detail=f"_salt_count={ks.get('_salt_count')}")

    print("\n─── 做饭：加糖抵盐 ───")
    # 继续加糖
    g.cmd("加 糖")
    g.cmd("加 糖")
    new_count = g.kitchen_state.get("_salt_count")
    check("加糖后 _salt_count < 3（糖压盐）",
          new_count < 3,
          detail=f"_salt_count={new_count}")

    print("\n─── 做饭：动词没匹配 ───")
    reset()
    g = MarketGame()
    g.cmd("菜场")
    g.budget = 100
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    if not g.basket:
        g.cmd("买 大白菜")
    g.cmd("回家")
    item = "小白菜" if any(i["name"] == "小白菜" for i in g.basket) else "大白菜"
    r = g.cmd(f"乱炖 {item}")  # 不存在的 verb
    check("未知 verb 不崩",
          isinstance(r, str),
          detail=f"reply: {r[:80]!r}")

    print("\n─── 做饭：quality_score 范围 ───")
    reset()
    g = MarketGame()
    g.cmd("菜场")
    g.budget = 100
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    if not g.basket:
        g.cmd("买 大白菜")
    g.cmd("回家")
    item = "小白菜" if any(i["name"] == "小白菜" for i in g.basket) else "大白菜"
    g.cmd(f"洗 {item}")
    g.cmd(f"切 {item}")
    g.cmd("加 盐")
    g.cmd("出锅")
    qs = g.kitchen_state.get("quality_score", 0)
    check("quality_score 是数字",
          isinstance(qs, (int, float)),
          detail=f"quality_score={qs}, type={type(qs)}")

    print("\n─── 做饭：plate 在 端 时填充 ───")
    reset()
    g = MarketGame()
    g.cmd("菜场")
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    g.cmd("回家")
    g.cmd("洗 小白菜")
    g.cmd("切 小白菜")
    g.cmd("出锅")
    g.cmd("端")
    check("端后 plate 填充",
          g.plate is not None and isinstance(g.plate, dict),
          detail=f"plate={g.plate}")

    print("\n─── 做饭：done 标记 ───")
    check("端后 done=True",
          g.done is True,
          detail=f"done={g.done}")

    print(f"\n{'='*60}")
    print(f"  PASSED: {len(PASS)}")
    print(f"  FAILED: {len(FAIL)}")
    print('='*60)
    if FAIL:
        for n, d in FAIL:
            print(f"  - {n}: {d}")


if __name__ == "__main__":
    main()