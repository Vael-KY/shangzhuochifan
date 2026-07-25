#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""save/load 边界测试"""
import os
import sys
import _testutil
import json

from market_engine import MarketGame


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

    print("\n─── save 文件手动写损坏 JSON ───")
    _testutil.reset()
    g = MarketGame()
    g.cmd("菜场")
    g.save()
    # 手动改坏 save
    with open(_testutil.save_path(), "w", encoding="utf-8") as f:
        f.write("{not json")
    try:
        g.load()
        check("损坏 JSON load 不崩", True)
    except Exception as e:
        check("损坏 JSON load 不崩", False, detail=str(e))

    print("\n─── save 文件缺失字段 load 不崩 ───")
    _testutil.reset()
    g = MarketGame()
    g.cmd("菜场")
    with open(_testutil.save_path(), "w", encoding="utf-8") as f:
        json.dump({"day": 5, "season": "夏"}, f)
    try:
        g2 = MarketGame()
        check("save 缺字段 load 不崩", True)
    except Exception as e:
        check("save 缺字段 load 不崩", False, detail=str(e))

    print("\n─── save 文件有未知字段 ───")
    _testutil.reset()
    g = MarketGame()
    g.cmd("菜场")
    state = g.to_dict()
    state["unknown_future_field"] = {"foo": "bar"}
    state["day"] = 7
    with open(_testutil.save_path(), "w", encoding="utf-8") as f:
        json.dump(state, f)
    try:
        g3 = MarketGame()
        check("未知字段 load 不崩（向后兼容）", True)
    except Exception as e:
        check("未知字段 load 不崩", False, detail=str(e))

    print("\n─── from_dict(None) 不崩 ───")
    _testutil.reset()
    g = MarketGame()
    try:
        g.from_dict(None)
        check("from_dict(None) 不崩", True)
    except Exception as e:
        check("from_dict(None) 不崩", False, detail=str(e))

    print("\n─── from_dict({}) 不崩 ───")
    _testutil.reset()
    g = MarketGame()
    try:
        g.from_dict({})
        check("from_dict({}) 不崩", True)
    except Exception as e:
        check("from_dict({}) 不崩", False, detail=str(e))

    print("\n─── 跨 save/load RNG 确定性 ───")
    _testutil.reset()
    g1 = MarketGame()
    g1.cmd("菜场")
    # 烧掉一批 rng 来更接近真实游戏
    [g1.rng() for _ in range(50)]
    state = g1.to_dict()
    g2 = MarketGame()
    g2.from_dict(state)
    # 验证：g2 从恢复点继续，输出和 g1 后续输出应该一致
    seq_continue = [g1.rng() for _ in range(30)]
    seq_resumed = [g2.rng() for _ in range(30)]
    check("跨 save/load RNG 连续性（恢复后输出 = g1 后续）",
          seq_resumed == seq_continue,
          detail=f"first 3: {seq_resumed[:3]} vs {seq_continue[:3]}")

    print("\n─── 重复 from_dict 多次不崩 ───")
    _testutil.reset()
    g = MarketGame()
    g.cmd("菜场")
    state = g.to_dict()
    for _ in range(5):
        try:
            g.from_dict(state)
        except Exception as e:
            check("重复 from_dict 5 次不崩", False, detail=str(e))
            break
    else:
        check("重复 from_dict 5 次不崩", True)

    print(f"\n{'='*60}")
    print(f"  PASSED: {len(PASS)}")
    print(f"  FAILED: {len(FAIL)}")
    print('='*60)
    if FAIL:
        for n, d in FAIL:
            print(f"  - {n}: {d}")


if __name__ == "__main__":
    main()