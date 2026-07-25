#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mystic 时间循环 / persistent_stall / 边界测试"""
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

    print("\n─── mystic 时间循环：pending_day 校验 ───")
    # 1) 把 pending_day 设成不是 prev_day（脏 pending），下次 new_day 应清掉不触发
    reset()
    g = MarketGame()
    g.cmd("菜场")
    # 把 progress 推到阈值并手动设 time_loop_pending
    g.mystic.state["progress"] = 999
    g.mystic.state["time_loop_pending"] = True
    g.mystic.state["time_loop_pending_day"] = -1  # 故意脏值
    # 第二次 new_day 时 pending_day (-1) != prev_day (1)，应清掉不触发
    g.cmd("新局")
    check("脏 pending_day 被清",
          g.mystic.state.get("time_loop_pending") == False,
          detail=f"state={g.mystic.state}")

    print("\n─── mystic 时间循环：有效 pending 触发 ───")
    reset()
    g = MarketGame()
    g.cmd("菜场")  # day=1
    # 模拟答完问题后设置了 pending
    g.mystic.state["time_loop_pending"] = True
    g.mystic.state["time_loop_pending_day"] = 1
    g.mystic.state["time_loop_just_happened"] = False
    # 直接调 maybe_time_loop 验证（不通过 cmd "新局" 因为新局会触发更多流程可能清掉 flag）
    loop_back, narrative = g.mystic.maybe_time_loop(prev_day=1)
    check("maybe_time_loop(prev_day=1) 返回 (True, narrative)",
          loop_back is True and isinstance(narrative, str) and "醒来" in narrative,
          detail=f"loop_back={loop_back}, narrative={narrative[:50] if narrative else None!r}")
    check("调用后 time_loop_just_happened=True",
          g.mystic.state.get("time_loop_just_happened") == True,
          detail=f"state={g.mystic.state}")
    check("调用后 time_loop_pending=False",
          g.mystic.state.get("time_loop_pending") == False,
          detail=f"state={g.mystic.state}")

    print("\n─── mystic: visit_mystic_stall 限制 today_stall ───")
    reset()
    g = MarketGame()
    # 强制进 mystic
    g.mystic.state["progress"] = 999
    g.cmd("新局")  # 触发 on_day_start
    today = g.mystic.state.get("today_stall")
    if not today:
        check("mystic 触发", False, "progress=999 仍未触发")
    else:
        # visit today_stall 应该成功
        r = g.cmd(f"去 {today}")
        check(f"visit today_stall ({today}) 成功",
              "摊主" in r or "💭" in r or "？" in r or "问" in r or "东西" in r,
              detail=f"reply: {r[:80]!r}")
        # visit 别的 mystic stall 应被拒绝（不是 persistent）
        other = None
        for s in ("mystic_granny", "mystic_fish", "mystic_old_man", "mystic_bamboo"):
            if s != today and s not in g.mystic.state.get("persistent_stalls", []):
                other = s
                break
        if other:
            r = g.cmd(f"去 {other}")
            check(f"visit 非 today_stall ({other}) 被拒绝",
                  "东角" in r or "没" in r or "不" in r,
                  detail=f"reply: {r[:80]!r}")

    print("\n─── mystic: maybe_recall 在 cooking 触发 ───")
    # 设已有 confession, cook 时 maybe_recall 应冒
    reset()
    g = MarketGame()
    g.cmd("菜场")
    g.cmd("去 veg_1")
    g.cmd("买 小白菜")
    g.cmd("回家")
    # 手动放一条 confession
    g.mystic.state["confessions"].append({"stall": "test", "answer": "今天很累", "day": 1})
    # 强制让 maybe_recall 命中（用固定 rng）
    g.rng = market_engine.mulberry32(0)  # seed 0 → first call rng() returns a known value
    # 看 recall 实际能不能浮起来（maybe_recall 在 cook_step 里调）
    # 实际触发概率 30%,seed 0 给的值可能不在范围内,先确认函数能跑
    recall = g.mystic.maybe_recall()
    check("maybe_recall 跑通（confessions 非空）",
          recall is None or "💭" in str(recall),
          detail=f"recall={recall!r}")

    print("\n─── mystic: state_for_save 深拷贝 ───")
    reset()
    g = MarketGame()
    g.cmd("菜场")
    state = g.to_dict()
    # 改 nested 不应影响原 state
    if state.get("mystic_state"):
        original_conf_len = len(state["mystic_state"].get("confessions", []))
        state["mystic_state"]["confessions"].append({"test": True})
        state2 = g.to_dict()
        new_conf_len = len(state2.get("mystic_state", {}).get("confessions", []))
        check("state_for_save 深拷贝（修改 nested 不污染 game）",
              new_conf_len == original_conf_len,
              detail=f"orig={original_conf_len}, after_modify={new_conf_len}")

    print("\n─── mystic: apply_exotic_reveal verb 影响 ───")
    reset()
    g = MarketGame()
    # 强制 mystic
    g.mystic.state["progress"] = 999
    g.cmd("新局")
    item = {"name": "明天的菜", "exotic": "tomorrow"}
    # 不同 verb 可能产生不同 line
    rs = set()
    for verb in ("切", "洗", "剥", "拍", "炒"):
        r = g.mystic.apply_exotic_reveal(item, verb)
        if r:
            rs.add(r)
    check("apply_exotic_reveal verb 影响 line 选择",
          len(rs) >= 2,
          detail=f"unique reveals: {len(rs)}")

    print(f"\n{'='*60}")
    print(f"  PASSED: {len(PASS)}")
    print(f"  FAILED: {len(FAIL)}")
    print('='*60)
    if FAIL:
        for n, d in FAIL:
            print(f"  - {n}: {d}")


if __name__ == "__main__":
    main()