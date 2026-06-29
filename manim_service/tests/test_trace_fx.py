"""Unit tests for the pure (render-free) core of trace_fx.

These exercise only the geometry/colour helpers — no manim ``play`` calls — so
they run fast without a render pipeline. The animating primitives are covered by
the render-smoke steps of the plan.
"""
from __future__ import annotations

from manim_service.trace_scenes import trace_common as C
from manim_service.trace_scenes import trace_fx as fx


def test_sign_color_positive_is_reward():
    assert fx.sign_color(0.4) == C.REWARD
    assert fx.sign_color(0.0) == C.REWARD
    assert fx.sign_color(-1.0) == C.PENALTY


def test_fan_layout_marks_chosen_and_scales_by_value():
    rows = fx.fan_layout([("L", 0.1), ("R", 0.9)], chosen_idx=1, cell_w=1.0)
    assert len(rows) == 2
    assert rows[1]["chosen"] is True and rows[0]["chosen"] is False
    # longer arrow for the larger value
    assert rows[1]["length"] > rows[0]["length"]


def test_fan_layout_handles_all_zero_without_div0():
    rows = fx.fan_layout([("L", 0.0), ("R", 0.0)], chosen_idx=0, cell_w=1.0)
    assert all(r["length"] >= 0 for r in rows)


def test_fan_layout_negative_values_scale_by_magnitude():
    # CliffWalking/Taxi Q-values are negative; the strongest (least negative)
    # should still be the longest arrow and the chosen flag must follow the idx.
    rows = fx.fan_layout([("U", -5.0), ("R", -1.0), ("D", -9.0)], chosen_idx=1, cell_w=1.2)
    assert rows[1]["chosen"] is True
    assert rows[1]["length"] >= rows[0]["length"] >= rows[2]["length"]
