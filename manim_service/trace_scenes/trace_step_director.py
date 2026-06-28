"""Per-step DIRECTOR — plays out each trace step as a deliberately paced beat
sequence so a learner can actually follow the decomposition.

The earlier renderer flashed the finished numbers in ~0.3s. This module instead
"sits in the agent's seat" and acts out the interaction that makes up one step:

  * DP / value iteration — focus the state, then for the chosen action look up
    each neighbour V(s') (flashed on the board) and SUBSTITUTE the real numbers
    into ``p·(r + γV(s'))`` term by term, sum to Q(s,a), compare actions, take
    the max, and only then commit V(s) and show Δ.
  * TD — sample/observe the action, move the agent, look up the bootstrap
    Q(s', ·), substitute ``r + γB`` into numbers, form δ, and nudge Q.
  * MC — read the hand, take the action, accrue the return, average to V(S).

Each beat reveals one line and holds, so nothing whips past. Pacing is tuned to
be graspable without being scrub-bait (≈4–6 s per step).
"""
from __future__ import annotations

from manim import (
    DOWN, LEFT, RIGHT, Circle, FadeIn, FadeOut, Line, MathTex,
    ReplacementTransform, RoundedRectangle, SurroundingRectangle, Text, VGroup,
    Write,
)

from . import trace_common as C
from . import trace_fx as fx

# ---- pacing knobs (seconds) ------------------------------------------------
# Deliberate but not bloated: enough to read and follow each beat, not so long
# the viewer reaches for the scrubber.
BEAT = 0.45   # hold after a meaningful reveal
HOLD = 0.28   # hold after a supporting reveal
QUICK = 0.18  # brief pause mid-substitution
REVEAL_RT = 0.38


def _tex(s: str, *, size=24, color=C.TEXT) -> MathTex:
    return MathTex(s, font_size=size, color=color)


class StepCard:
    """A fixed panel that lines are revealed into, top-down, with deliberate
    pacing and in-place formula→numbers substitutions."""

    def __init__(self, scene, title, accent, *, pos, width, height):
        self.scene = scene
        self.accent = accent
        self.width = width
        self.inner = width - 0.6
        self.box = RoundedRectangle(
            width=width, height=height, corner_radius=0.18,
            fill_color=C.PANEL, fill_opacity=1.0,
            stroke_color=accent, stroke_width=1.8).move_to(pos)
        self.left = self.box.get_left()[0] + 0.32
        self.title = Text(title, font_size=20, color=accent)
        self.title.move_to([self.left + self.title.width / 2,
                            self.box.get_top()[1] - 0.34, 0.0])
        self.cursor = self.title.get_bottom()[1] - 0.16
        self.parts: list = [self.box, self.title]

    def show(self):
        self.scene.play(FadeIn(self.box), FadeIn(self.title), run_time=0.4)

    def _fit(self, mob):
        if mob.width > self.inner:
            mob.scale_to_fit_width(self.inner)
        return mob

    def _place(self, mob, gap):
        self._fit(mob)
        mob.move_to([self.left + mob.width / 2,
                     self.cursor - gap - mob.height / 2, 0.0])
        return mob

    def reveal(self, mob, *, wait=BEAT, gap=0.18, anim=FadeIn, rt=REVEAL_RT):
        self._place(mob, gap)
        self.scene.play(anim(mob), run_time=rt)
        self.cursor = mob.get_bottom()[1]
        self.parts.append(mob)
        if wait:
            self.scene.wait(wait)
        return mob

    def substitute(self, symbolic: MathTex, numeric: MathTex, *, wait=BEAT, gap=0.18):
        """Show the symbolic line, hold, then morph it IN PLACE into the line
        with the real numbers plugged in — 'here's the formula, now the numbers'."""
        self._place(numeric, gap)
        self._fit(symbolic)
        symbolic.move_to(numeric).align_to(numeric, LEFT)
        self.scene.play(Write(symbolic), run_time=0.4)
        self.scene.wait(QUICK)
        self.scene.play(ReplacementTransform(symbolic, numeric), run_time=0.45)
        self.cursor = numeric.get_bottom()[1]
        self.parts.append(numeric)
        if wait:
            self.scene.wait(wait)
        return numeric

    def fade(self):
        self.scene.play(FadeOut(VGroup(*self.parts)), run_time=0.4)


def _board_flash(board, scene, state):
    if hasattr(board, "flash") and isinstance(state, int):
        try:
            board.flash(scene, state)
        except Exception:  # noqa: BLE001
            pass


# ============================================================ DP director
def _play_dp(scene, board, step, env, *, pos, width):
    p = C.dp_pieces(step) or {}
    state = step.get("state")
    kind = p.get("kind")
    if kind == "value_iteration":
        title, rule = f"Value iteration · state {state}", \
            r"V(s)\leftarrow \max_a \sum_{s'} p\,[\,r+\gamma V(s')\,]"
    elif kind == "policy_improvement":
        title, rule = f"Policy improvement · state {state}", \
            r"\pi(s)\leftarrow \arg\max_a \sum_{s'} p\,[\,r+\gamma V(s')\,]"
    else:
        title, rule = f"Policy evaluation · state {state}", \
            r"V(s)\leftarrow \sum_a \pi(a|s)\sum_{s'} p\,[\,r+\gamma V(s')\,]"

    if hasattr(board, "focus"):
        board.focus(scene, state)
    card = StepCard(scene, title, C.STATE, pos=pos, width=width, height=6.3)
    card.show()
    card.reveal(_tex(rule, size=21), wait=BEAT)

    backups = p.get("action_backups") or []
    sel_label = p.get("selected_action_label")
    sel = next((b for b in backups if b.get("action_label") == sel_label),
               backups[0] if backups else None)

    fx_mobs: list = []
    spatial = hasattr(board, "center") and isinstance(state, int)
    cell_w = getattr(getattr(board, "hm", None), "_cell_w", None) or 1.0

    if sel is not None:
        lab = C.tex_escape(sel.get("action_label", ""))
        # Show the generic backup term ONCE, then plug in each real lookup.
        card.reveal(_tex(rf"\text{{look ahead from }}{lab}:\;\;p\,(r+\gamma V(s'))",
                         size=20, color=C.ACTION), wait=QUICK)
        terms = sel.get("transition_terms") or []
        for t in terms[:3]:
            ns = t.get("next_state")
            prob, rwd = C.fmt(t.get("probability")), C.signed(t.get("reward"))
            fv, contrib = C.fmt(t.get("future_value")), C.fmt(t.get("contribution"))
            term_line = card.reveal(
                _tex(rf"\;\;{prob}\,({rwd}+\gamma\!\cdot\!{fv})={contrib}",
                     size=20, color=C.TEXT), wait=QUICK)
            # GRID: value flows from the neighbour s' BACK INTO the focal state s,
            # carrying its contribution number — the backtracking the card narrates.
            if spatial and isinstance(ns, int):
                cval = C.as_float(t.get("contribution")) or 0.0
                arrow = fx.value_flow_arrow(scene, board.center(ns), board.center(state),
                                            contrib, color=fx.sign_color(cval))
                fx.bind_pulse(scene, term_line, arrow)
                fx_mobs.append(arrow)
                if (C.as_float(t.get("reward")) or 0.0) > 0:
                    fx.reward_pulse(scene, board.center(ns), C.signed(t.get("reward")),
                                    color=C.REWARD)
            scene.wait(HOLD)
        exp = C.fmt(sel.get("expected_return"))
        card.reveal(_tex(rf"Q(s,{lab})=\textstyle\sum={exp}", size=23, color=C.TEAL),
                    wait=BEAT)

    if len(backups) > 1:
        card.reveal(_action_compare(backups, sel_label), wait=BEAT)
        # GRID: the candidate action-values as a fan from the focal cell, the
        # argmax spoke winning — the decision made visible ON the world.
        if spatial:
            dir_values = [(b.get("action_label", ""),
                           C.as_float(b.get("expected_return")) or 0.0) for b in backups]
            chosen_idx = next((i for i, b in enumerate(backups)
                               if b.get("action_label") == sel_label), 0)
            fx_mobs.append(fx.action_fan(scene, board.center(state), dir_values,
                                         chosen_idx, cell_w=cell_w))

    if kind == "policy_improvement":
        card.reveal(_tex(rf"\pi(s)\leftarrow \text{{{C.tex_escape(sel_label or '')}}}",
                         size=26, color=C.REWARD), wait=BEAT)
    else:
        card.reveal(_tex(rf"V(s)={C.fmt(p.get('backup'))}", size=27, color=C.REWARD),
                    wait=QUICK)
        if hasattr(board, "commit"):
            board.commit(scene, step)
        scene.wait(0.2)
        if p.get("delta") is not None:
            card.reveal(_tex(rf"\Delta={C.fmt(p['delta'])}", size=21, color=C.VALUE),
                        wait=HOLD)
    # Clear this step's transient grid arrows/fan so the next backup starts clean
    # (the committed value fill stays on the board).
    if fx_mobs:
        scene.play(*[FadeOut(m) for m in fx_mobs], run_time=0.3)
    return card


def _action_compare(backups, sel_label):
    chips = []
    for b in backups[:4]:
        lab = C.tex_escape(b.get("action_label", ""))
        val = C.fmt(b.get("expected_return"))
        is_sel = b.get("action_label") == sel_label
        chip = MathTex(rf"\text{{{lab}}}\,{val}", font_size=18,
                       color=C.REWARD if is_sel else C.MUTED)
        if is_sel:
            chip = VGroup(chip, SurroundingRectangle(
                chip, color=C.REWARD, buff=0.06, stroke_width=1.4))
        chips.append(chip)
    return VGroup(*chips).arrange(RIGHT, buff=0.3)


# ============================================================ TD director
def _play_td(scene, board, step, env, *, pos, width, first):
    p = C.td_pieces(step) or {}
    on = p.get("on_policy")
    kind = p.get("kind")
    title = ("SARSA · on-policy" if on
             else "Q-learning · off-policy" if kind == "q_learning"
             else "TD(0) prediction")

    t = C.transition(step, env)
    s, a, r, ns = t["state"], C.tex_escape(t["action_label"]), C.signed(t["reward"]), \
        t["next_state"]

    # Agent acts: place on first step, then walk s -> s'.
    if first and hasattr(board, "place"):
        board.place(scene, step, run_time=0.4)
        scene.wait(0.2)
    if hasattr(board, "step"):
        board.step(scene, step, run_time=0.55)

    card = StepCard(scene, title, C.VALUE, pos=pos, width=width, height=3.15)
    card.show()
    card.reveal(_tex(rf"s\,{s}\;\xrightarrow{{\;{a}\,\mid\,r\,{r}\;}}\;s'\,{ns}",
                     size=23, color=C.STATE), wait=HOLD)

    boot = C.fmt(p.get("bootstrap_value"))
    blabel = C.tex_escape(p.get("bootstrap_label") or "Q(s',a')")
    _board_flash(board, scene, ns)
    card.reveal(_tex(rf"B={blabel}={boot}", size=22, color=C.TEAL), wait=HOLD)

    reward, gamma, target = C.fmt(p.get("reward")), C.fmt(p.get("gamma")), \
        C.fmt(p.get("target"))
    card.substitute(
        _tex(r"\text{target}=r+\gamma B", size=22),
        _tex(rf"\text{{target}}={reward}+{gamma}\!\cdot\!{boot}={target}", size=22),
        wait=HOLD)
    card.reveal(_tex(rf"\delta=\text{{target}}-Q={C.signed(p.get('error'))}",
                     size=22, color=C.VALUE), wait=HOLD)
    nudge = _nudge_row(p.get("old"), p.get("target"), p.get("new"))
    card.reveal(VGroup(
        _tex(rf"Q:\ {C.fmt(p.get('old'))}\rightarrow {C.fmt(p.get('new'))}",
             size=24, color=C.REWARD),
        nudge).arrange(RIGHT, buff=0.4), wait=BEAT)
    return card


def _nudge_row(old, target, new):
    o, t, n = C.as_float(old), C.as_float(target), C.as_float(new)
    w = 2.6
    track = Line(LEFT * w / 2, RIGHT * w / 2, color=C.MUTED, stroke_width=3).set_opacity(0.5)
    if None in (o, t, n) or abs(t - o) < 1e-9:
        return VGroup(track)
    frac = max(0.0, min(1.0, (n - o) / (t - o)))
    od = Circle(radius=0.06, color=C.MUTED, fill_opacity=1).move_to(LEFT * w / 2)
    td = Circle(radius=0.06, color=C.TEAL, fill_opacity=1).move_to(RIGHT * w / 2)
    nd = Circle(radius=0.07, color=C.VALUE, fill_opacity=1).move_to(
        LEFT * w / 2 + RIGHT * w * frac)
    return VGroup(track, od, td, nd)


# ============================================================ MC director
def _play_mc(scene, board, step, env, *, pos, width, first):
    p = C.mc_pieces(step) or {}
    title = "Monte Carlo · first-visit" if p.get("is_return_update") else "Monte Carlo · sample"

    if hasattr(board, "step"):
        board.step(scene, step, run_time=0.5)

    obs = p.get("observation_label") or (
        f"({p.get('player_sum')}, {p.get('dealer_card')}, "
        f"{'ace' if p.get('usable_ace') else 'no ace'})")
    card = StepCard(scene, title, C.REWARD, pos=pos, width=width, height=4.7)
    card.show()
    card.reveal(_tex(rf"S=\text{{{C.tex_escape(obs)}}}", size=23, color=C.STATE), wait=HOLD)
    action_line = rf"\text{{action }}{C.tex_escape(p.get('action_label') or '-')}"
    if p.get("reward") is not None:
        action_line += rf"\quad r\,{C.signed(p.get('reward'))}"
    card.reveal(_tex(action_line, size=22, color=C.ACTION), wait=HOLD)

    if p.get("is_return_update"):
        card.reveal(_tex(rf"\text{{return }}G={C.signed(p.get('return_value'))}",
                         size=24, color=C.VALUE), wait=BEAT)
        hist = p.get("returns_history") or []
        if isinstance(hist, list) and hist:
            mean = sum(C.as_float(x) or 0 for x in hist) / len(hist)
            card.substitute(
                _tex(r"V(S)\leftarrow \operatorname{mean}(\text{returns})", size=22),
                _tex(rf"V(S)\leftarrow \operatorname{{mean}}={C.fmt(mean)}", size=22,
                     color=C.REWARD),
                wait=BEAT)
    if p.get("terminated"):
        card.reveal(_tex(r"\text{episode ends}", size=20, color=C.PENALTY), wait=HOLD)
    return card


# ============================================================ greedy/transition replay
def _eval_action_values(step):
    """Compact action-value row Q(s,·) for the current state, with the action
    the policy actually took boxed — so a greedy replay SHOWS the decision, not
    just the move. Returns a VGroup or None when the Q-row isn't available."""
    tb = step.get("tables") or {}
    after = tb.get("after")
    labels = tb.get("action_labels") or []
    chosen = (tb.get("active_cell") or {}).get("column")
    state = step.get("state")
    if not (isinstance(after, list) and isinstance(state, int)
            and 0 <= state < len(after) and isinstance(after[state], list)):
        return None
    row = after[state]
    if not row:
        return None
    chips = []
    for i, v in enumerate(row):
        lab = C.tex_escape((labels[i][0] if i < len(labels) and labels[i] else str(i)))
        is_sel = (i == chosen)
        chip = MathTex(rf"{lab}\,{C.fmt(v)}", font_size=18,
                       color=C.VALUE if is_sel else C.MUTED)
        if is_sel:
            chip = VGroup(chip, SurroundingRectangle(
                chip, color=C.VALUE, buff=0.05, stroke_width=1.4))
        chips.append(chip)
    return VGroup(*chips).arrange(RIGHT, buff=0.24)


def _play_transition_replay(scene, board, step, env, *, pos, width, first, lite=False):
    """Steps with no update family (a greedy-evaluation rollout) still deserve to
    SHOW THE AGENT MOVING and to make the policy's decision legible. Drive the
    spatial board through the transition, then reveal an honest S-A-R-S' line and
    the action-value row Q(s,·) with the taken action boxed — no update math,
    because no learning step occurred on this rollout.

    ``lite=True`` (early/improving stages of a staged progression): play FAST and
    minimal — quick agent move + the transition line only, no action-value
    breakdown — because the message is just 'watch it flail', and to keep render
    cost bounded. The rich treatment is reserved for the converged stage."""
    move_rt = 0.32 if lite else 0.6
    if first and hasattr(board, "place"):
        board.place(scene, step, run_time=0.28 if lite else 0.4)
        scene.wait(0.08 if lite else 0.2)
    if hasattr(board, "step"):
        board.step(scene, step, run_time=move_rt)

    t = C.transition(step, env)
    s, a, r, ns = t["state"], C.tex_escape(t["action_label"]), C.signed(t["reward"]), \
        t["next_state"]
    height = 2.2 if lite else 3.3
    card = StepCard(scene, f"Replay · {env}", C.STATE, pos=pos, width=width, height=height)
    card.show()
    card.reveal(_tex(rf"s\,{s}\;\xrightarrow{{\;{a}\,\mid\,r\,{r}\;}}\;s'\,{ns}",
                     size=22 if lite else 23, color=C.STATE),
                wait=HOLD if lite else BEAT, rt=0.28 if lite else REVEAL_RT)
    if lite:
        return card
    av_row = _eval_action_values(step)
    if av_row is not None:
        card.reveal(_tex(r"Q(s,\cdot)\;\text{— the policy took the boxed action}",
                         size=17, color=C.MUTED), wait=QUICK)
        card.reveal(av_row, wait=BEAT)
    else:
        uv = step.get("updated_values") or {}
        if uv:
            key, val = next(iter(uv.items()))
            card.reveal(_tex(rf"{C.tex_escape(str(key))}={C.fmt(val)}",
                             size=21, color=C.VALUE), wait=HOLD)
    scene.wait(BEAT)
    return card


# ============================================================ dispatch
def play_step(scene, board, step, env, *, pos, width, first=False, lite=False):
    fam = C.family(step)
    try:
        # Lite stages (early/improving in a staged progression) always use the
        # fast spatial replay regardless of family — the message is "watch it
        # behave", not a per-step derivation.
        if lite and getattr(board, "is_spatial", False):
            return _play_transition_replay(scene, board, step, env,
                                           pos=pos, width=width, first=first, lite=True)
        if fam == "dp":
            return _play_dp(scene, board, step, env, pos=pos, width=width)
        if fam == "td":
            return _play_td(scene, board, step, env, pos=pos, width=width, first=first)
        if fam == "mc":
            return _play_mc(scene, board, step, env, pos=pos, width=width, first=first)
        # No update family (greedy-evaluation replay): animate the agent through
        # the trajectory on spatial boards instead of a dead static grid.
        if getattr(board, "is_spatial", False):
            return _play_transition_replay(scene, board, step, env,
                                           pos=pos, width=width, first=first, lite=lite)
    except Exception:  # noqa: BLE001 — never let one bad step kill the render
        pass
    card = StepCard(scene, "Update", C.STATE, pos=pos, width=width, height=2.2)
    card.show()
    card.reveal(_tex(step.get("math_equation") or r"\text{update}", size=22), wait=BEAT)
    return card
