"""The per-step 'update card': the actual arithmetic of one update, built from the run
data. Kind-aware — TD (target / error / nudge), DP (backup / best action), MC (return /
mean). Built fresh each step and ReplacementTransform'd by the scene loop, so it stays
crisp and fast for a real-time replay.
"""
from __future__ import annotations

from manim import (
    MathTex, RoundedRectangle, Text, VGroup, Line, Circle, DOWN, LEFT, RIGHT,
)

from . import trace_common as C

CARD_W = 5.9


def _eqrow(tex: str, *, size=26, color=C.TEXT):
    return MathTex(tex, font_size=size, color=color)


def _panel(title: str, rows: VGroup, accent: str, *, width=CARD_W, height=None) -> VGroup:
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    if rows.width > width - 0.5:
        rows.scale_to_fit_width(width - 0.5)
    head = Text(title, font_size=20, color=accent)
    content = VGroup(head, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    h = height or max(content.height + 0.5, 1.6)
    box = RoundedRectangle(width=width, height=h, corner_radius=0.16,
                           fill_color=C.PANEL, fill_opacity=1.0,
                           stroke_color=accent, stroke_width=1.6)
    content.move_to(box.get_center())
    return VGroup(box, content)


def _transition_tex(step: dict, env: str) -> str:
    t = C.transition(step, env)
    s, a, r, ns = t["state"], t["action_label"], C.signed(t["reward"]), t["next_state"]
    return rf"s\,{s}\;\xrightarrow{{\;\text{{{C.tex_escape(a)}}}\,\mid\,r\,{r}\;}}\;s'\,{ns}"


# ----------------------------------------------------------------- TD card
def _td_card(step: dict, env: str) -> VGroup:
    p = C.td_pieces(step)
    title = ("SARSA · on-policy" if p["on_policy"]
             else "Q-learning · off-policy" if p["kind"] == "q_learning"
             else "TD(0) prediction")
    reward, gamma = C.fmt(p["reward"]), C.fmt(p["gamma"])
    boot = C.fmt(p["bootstrap_value"])
    target, error = C.fmt(p["target"]), C.signed(p["error"])
    old, new = C.fmt(p["old"]), C.fmt(p["new"])
    blabel = C.tex_escape(p["bootstrap_label"] or "Q(s',a')")
    rows = VGroup(
        _eqrow(_transition_tex(step, env), size=24, color=C.STATE),
        _eqrow(rf"\text{{bootstrap }}={blabel}={boot}", size=24, color=C.TEAL),
        _eqrow(rf"\text{{target}}=r+\gamma B={reward}+{gamma}\cdot {boot}={target}",
               size=24, color=C.TEXT),
        _eqrow(rf"\delta=\text{{target}}-Q={error}", size=26, color=C.VALUE),
        _eqrow(rf"Q:\ {old}\rightarrow {new}", size=28, color=C.REWARD),
        _nudge_bar(p["old"], p["target"], p["new"]),
    )
    return _panel(title, rows, C.VALUE)


def _nudge_bar(old, target, new):
    o, t, n = C.as_float(old), C.as_float(target), C.as_float(new)
    w = 4.6
    track = Line(LEFT * w / 2, RIGHT * w / 2, color=C.MUTED, stroke_width=3).set_opacity(0.5)
    if None in (o, t, n) or abs(t - o) < 1e-9:
        return VGroup(track)
    frac = max(0.0, min(1.0, (n - o) / (t - o)))
    od = Circle(radius=0.06, color=C.MUTED, fill_opacity=1).move_to(LEFT * w / 2)
    td = Circle(radius=0.06, color=C.TEAL, fill_opacity=1).move_to(RIGHT * w / 2)
    nd = Circle(radius=0.07, color=C.VALUE, fill_opacity=1).move_to(
        LEFT * w / 2 + RIGHT * w * frac)
    return VGroup(track, od, td, nd)


# ----------------------------------------------------------------- DP card
def _dp_card(step: dict, env: str) -> VGroup:
    p = C.dp_pieces(step)
    state = step.get("state")
    if p["kind"] == "value_iteration":
        title = f"Value iteration · state {state}"
        op = r"\max_a"
    elif p["kind"] == "policy_improvement":
        title = f"Policy improvement · state {state}"
        op = r"\arg\max_a"
    else:
        title = f"Policy evaluation · state {state}"
        op = r"\sum_a \pi(a|s)"
    rows = VGroup(
        _eqrow(rf"{C.tex_escape(p['lhs'])}\leftarrow {op}\sum_{{s',r}}p\,[\,r+\gamma V(s')\,]",
               size=22, color=C.TEXT),
    )
    # top action backups
    backups = p["action_backups"][:4] if isinstance(p["action_backups"], list) else []
    for b in backups:
        lab = C.tex_escape(b.get("action_label", b.get("action", "")))
        val = C.fmt(b.get("weighted_contribution", b.get("expected_return")))
        sel = (b.get("action_label") == p["selected_action_label"])
        rows.add(_eqrow(rf"\;{lab}:\ {val}", size=22,
                        color=C.REWARD if sel else C.MUTED))
    if p["kind"] == "policy_improvement":
        rows.add(_eqrow(rf"\pi({state})\leftarrow \text{{{C.tex_escape(p['selected_action_label'])}}}",
                        size=26, color=C.REWARD))
    else:
        backup = C.fmt(p["backup"])
        rows.add(_eqrow(rf"{C.tex_escape(p['lhs'])}={backup}", size=28, color=C.REWARD))
        if p["delta"] is not None:
            rows.add(_eqrow(rf"\Delta={C.fmt(p['delta'])}", size=22, color=C.VALUE))
    return _panel(title, rows, C.STATE)


# ----------------------------------------------------------------- MC card
def _mc_card(step: dict, env: str) -> VGroup:
    p = C.mc_pieces(step)
    title = "Monte Carlo · first-visit" if p["is_return_update"] else "Monte Carlo · sample"
    obs = p["observation_label"] or (
        f"({p['player_sum']}, {p['dealer_card']}, {'ace' if p['usable_ace'] else 'no ace'})")
    rows = VGroup(
        _eqrow(rf"S=\text{{{C.tex_escape(obs)}}}", size=24, color=C.STATE),
        _eqrow(rf"\text{{action }}\;{C.tex_escape(p['action_label'] or '-')}\quad r\,{C.signed(p['reward'])}",
               size=24, color=C.ACTION),
    )
    if p["is_return_update"]:
        rows.add(_eqrow(rf"\text{{return }}G={C.signed(p['return_value'])}", size=26, color=C.VALUE))
        hist = p["returns_history"]
        if isinstance(hist, list) and hist:
            mean = sum(C.as_float(x) or 0 for x in hist) / len(hist)
            rows.add(_eqrow(rf"V(S)\leftarrow \operatorname{{mean}}=\,{C.fmt(mean)}",
                            size=26, color=C.REWARD))
    if p["terminated"]:
        rows.add(_eqrow(r"\text{episode ends}", size=20, color=C.PENALTY))
    return _panel(title, rows, C.REWARD)


def make_update_card(step: dict, env: str) -> VGroup:
    fam = C.family(step)
    try:
        if fam == "td":
            return _td_card(step, env)
        if fam == "dp":
            return _dp_card(step, env)
        if fam == "mc":
            return _mc_card(step, env)
    except Exception:
        pass
    # fallback: math_equation + caption
    rows = VGroup(
        _eqrow(step.get("math_equation") or r"\text{update}", size=22, color=C.TEXT),
    )
    return _panel("Update", rows, C.STATE)
