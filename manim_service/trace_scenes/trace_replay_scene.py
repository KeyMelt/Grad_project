"""Standalone Manim scene for RL trace replay.

Invoke as:
    python -m manim -ql --media_dir <dir> trace_replay_scene.py TraceReplayScene

The scene reads its data from a JSON file whose path is given by the
``TRACE_DATA_PATH`` environment variable.  The JSON must be a list of step
dicts as produced by the trace-log pipeline.

Layout (4-panel):
    ┌─────────────────────┬───────────────────┐
    │                     │   Equation panel  │
    │  EnvironmentValue   ├───────────────────┤
    │  Heatmap (left)     │   Backup panel    │
    │  with elf agent     ├───────────────────┤
    │                     │   Update panel    │
    ├─────────────────────┴───────────────────┤
    │           Step caption (bottom)         │
    └─────────────────────────────────────────┘
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure manim_service is importable when the file is run directly by Manim
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from manim import (
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    MathTex,
    ReplacementTransform,
    RIGHT,
    RoundedRectangle,
    Scene,
    Text,
    UP,
    VGroup,
    Write,
)

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
BG = "#020617"
PANEL_FILL = "#0F172A"
ACCENT = "#38bdf8"
MATH = "#facc15"
UPDATE = "#34d399"
TEXT = "#f8fafc"
MUTED = "#94a3b8"

# ---------------------------------------------------------------------------
# FrozenLake action → direction string
# ---------------------------------------------------------------------------
ACTION_DIR: dict[int, str] = {0: "left", 1: "down", 2: "right", 3: "up"}

# ---------------------------------------------------------------------------
# Environment data path from env var
# ---------------------------------------------------------------------------
DATA_PATH = os.environ.get("TRACE_DATA_PATH", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _panel_box(
    width: float,
    height: float,
    stroke: str = ACCENT,
    fill: str = PANEL_FILL,
) -> RoundedRectangle:
    return RoundedRectangle(
        corner_radius=0.16,
        width=width,
        height=height,
        stroke_color=stroke,
        stroke_width=1.4,
        fill_color=fill,
        fill_opacity=0.92,
    )


def _fit_inside(mob, width: float, height: float):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    if mob.height > height:
        mob.scale_to_fit_height(height)
    return mob


def _fmt(value) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "0.000"


def _safe_tex(value: object) -> str:
    return str(value).replace("_", r"\_")


def _parse_updated_values(raw) -> dict[int, float]:
    """Convert updated_values dict like {'V(3)': 0.5} → {3: 0.5}."""
    if not isinstance(raw, dict):
        return {}
    result: dict[int, float] = {}
    for k, v in raw.items():
        # Accept "V(3)", "3", or integer keys
        key_str = str(k).strip()
        # Strip surrounding V(...) notation
        if key_str.startswith("V(") and key_str.endswith(")"):
            key_str = key_str[2:-1]
        try:
            state_idx = int(key_str)
            result[state_idx] = float(v)
        except (ValueError, TypeError):
            pass
    return result


def _build_equation_panel(step: dict) -> VGroup:
    equation = step.get("math_equation") or r"V(s) \leftarrow \text{update}"
    eq_mob = MathTex(equation, font_size=30, color=TEXT)
    _fit_inside(eq_mob, 4.65, 0.72)

    # Code focus line
    code_focus: str = ""
    eq_update = step.get("equation_update") or {}
    if isinstance(eq_update, dict):
        code_focus = eq_update.get("code_focus", "")
    if not code_focus:
        code_lines = step.get("code_lines") or []
        code_focus = code_lines[-1] if code_lines else "update value from target"

    code_mob = Text(code_focus, font_size=15, color=ACCENT, font="Courier")
    _fit_inside(code_mob, 4.65, 0.38)

    title_mob = Text("Equation", font_size=20, color=MATH)
    content = VGroup(title_mob, eq_mob, code_mob).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    box = _panel_box(5.1, 1.60, stroke=MATH)
    content.move_to(box.get_center())
    return VGroup(box, content)


def _build_backup_panel(step: dict) -> VGroup:
    eq_update = step.get("equation_update") or {}
    if isinstance(eq_update, dict) and eq_update:
        reward = _fmt(eq_update.get("reward", 0))
        gamma = _fmt(eq_update.get("gamma", 0))
        bootstrap = _fmt(eq_update.get("bootstrap_value", 0))
        target = _fmt(eq_update.get("td_target", 0))
        label = _safe_tex(eq_update.get("bootstrap_label", "B"))
        lines = VGroup(
            MathTex(r"\text{target}=r+\gamma B", font_size=26, color=TEXT),
            MathTex(
                rf"\text{{target}}={reward}+{gamma}\cdot {bootstrap}",
                font_size=26,
                color=TEXT,
            ),
            MathTex(rf"\text{{target}}={target}", font_size=30, color=MATH),
            Text(f"B = {label}", font_size=16, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    else:
        math_lines = step.get("math_lines") or []
        if math_lines:
            rows = [Text(line, font_size=18, color=TEXT) for line in math_lines[:3]]
        else:
            rows = [Text("Numeric backup", font_size=18, color=MUTED)]
        lines = VGroup(
            Text("Backup", font_size=20, color=MATH),
            *rows,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    _fit_inside(lines, 4.65, 1.78)
    box = _panel_box(5.1, 2.10, stroke=MATH, fill="#0d1f2d")
    lines.move_to(box.get_center())
    return VGroup(box, lines)


def _build_update_panel(step: dict) -> VGroup:
    eq_update = step.get("equation_update") or {}
    if isinstance(eq_update, dict) and eq_update:
        lhs = _safe_tex(eq_update.get("lhs", "V(s)"))
        if eq_update.get("kind") == "policy_improvement":
            rows = VGroup(
                MathTex(
                    rf"{lhs}\leftarrow \text{{greedy}}(V)",
                    font_size=28,
                    color=TEXT,
                ),
                MathTex(
                    rf"{lhs} = \text{{{_safe_tex(eq_update.get('new_value', 'action'))}}}",
                    font_size=32,
                    color=UPDATE,
                ),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        else:
            old = _fmt(eq_update.get("old_value", 0))
            alpha = _fmt(eq_update.get("alpha", 0))
            target = _fmt(eq_update.get("td_target", 0))
            new = _fmt(eq_update.get("new_value", 0))
            rows = VGroup(
                MathTex(
                    rf"{lhs}\leftarrow {old}+{alpha}({target}-{old})",
                    font_size=27,
                    color=TEXT,
                ),
                MathTex(rf"{lhs}={new}", font_size=32, color=UPDATE),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    else:
        updated_values = step.get("updated_values") or {}
        entries = list(updated_values.items())[:3] if isinstance(updated_values, dict) else []
        if entries:
            item_mobs = [Text(f"{k} = {v}", font_size=20, color=UPDATE) for k, v in entries]
        else:
            item_mobs = [Text("No value update recorded", font_size=18, color=MUTED)]
        rows = VGroup(*item_mobs).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    _fit_inside(rows, 4.65, 1.30)
    box = _panel_box(5.1, 1.65, stroke=UPDATE, fill="#052e2b")
    rows.move_to(box.get_center())
    return VGroup(box, rows)


def _build_caption(step: dict, index: int, total: int) -> Text:
    agent_caption = step.get("agent_caption", "")
    raw = f"Step {index}/{total}: {agent_caption}" if agent_caption else f"Step {index}/{total}"
    cap = Text(raw, font_size=20, color=TEXT)
    _fit_inside(cap, 11.8, 0.42)
    return cap


# ---------------------------------------------------------------------------
# State-hash helpers (detect which panels actually changed)
# ---------------------------------------------------------------------------

def _eq_hash(step: dict):
    eq_update = step.get("equation_update") or {}
    code_focus = eq_update.get("code_focus", "") if isinstance(eq_update, dict) else ""
    if not code_focus:
        code_lines = step.get("code_lines") or []
        code_focus = code_lines[-1] if code_lines else ""
    return (step.get("math_equation"), code_focus)


def _bk_hash(step: dict):
    eq_update = step.get("equation_update") or {}
    if isinstance(eq_update, dict) and eq_update:
        return (
            eq_update.get("reward"),
            eq_update.get("gamma"),
            eq_update.get("bootstrap_value"),
            eq_update.get("td_target"),
        )
    return tuple((step.get("math_lines") or [])[:3])


def _up_hash(step: dict):
    eq_update = step.get("equation_update") or {}
    if isinstance(eq_update, dict) and eq_update:
        return (
            eq_update.get("lhs"),
            eq_update.get("old_value"),
            eq_update.get("alpha"),
            eq_update.get("td_target"),
            eq_update.get("new_value"),
        )
    updated = step.get("updated_values") or {}
    return tuple(sorted(updated.items())) if isinstance(updated, dict) else ()


def _env_hash(step: dict):
    return (step.get("state"), step.get("action"), step.get("next_state"))


# ---------------------------------------------------------------------------
# Main scene
# ---------------------------------------------------------------------------

class TraceReplayScene(Scene):
    """Manim scene that replays an RL agent trace step-by-step.

    Data is loaded from the JSON file at TRACE_DATA_PATH.  Each step dict
    may contain:
        state, action, next_state, updated_values, math_equation,
        equation_update, math_lines, code_lines, agent_caption
    """

    def construct(self) -> None:
        self.camera.background_color = BG

        # ------------------------------------------------------------------
        # Load trace data
        # ------------------------------------------------------------------
        if not DATA_PATH:
            self._show_error("TRACE_DATA_PATH environment variable is not set.")
            return

        try:
            with open(DATA_PATH, "r", encoding="utf-8") as fh:
                steps: list[dict] = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            self._show_error(f"Could not load trace data: {exc}")
            return

        if not steps:
            self._show_error("No replay trace available.")
            return

        # ------------------------------------------------------------------
        # Build EnvironmentValueHeatmap (with fallback to ValueHeatmap)
        # ------------------------------------------------------------------
        heatmap = self._build_heatmap(steps[0])
        # Position heatmap on the left
        heatmap.move_to(LEFT * 3.2 + UP * 0.2)

        # ------------------------------------------------------------------
        # Scene title
        # ------------------------------------------------------------------
        title = Text("Agent Step → Bellman Update", font_size=28, color=TEXT)
        title.to_edge(UP, buff=0.22)
        self.play(FadeIn(title), run_time=0.4)

        # ------------------------------------------------------------------
        # Right-column anchor positions (relative to scene origin)
        # ------------------------------------------------------------------
        EQUATION_POS = RIGHT * 2.85 + UP * 2.15
        BACKUP_POS   = RIGHT * 2.85 + UP * 0.15
        UPDATE_POS   = RIGHT * 2.85 + DOWN * 1.88
        CAPTION_POS  = DOWN * 3.45

        # Build initial panels
        eq_panel  = _build_equation_panel(steps[0]).move_to(EQUATION_POS)
        bk_panel  = _build_backup_panel(steps[0]).move_to(BACKUP_POS)
        up_panel  = _build_update_panel(steps[0]).move_to(UPDATE_POS)
        caption   = _build_caption(steps[0], 1, len(steps)).move_to(CAPTION_POS)

        prev_eq_hash = _eq_hash(steps[0])
        prev_bk_hash = _bk_hash(steps[0])
        prev_up_hash = _up_hash(steps[0])
        prev_env_hash = _env_hash(steps[0])

        # Initial fade-in (heatmap, all panels, caption)
        self.play(
            FadeIn(heatmap),
            FadeIn(eq_panel),
            FadeIn(bk_panel),
            FadeIn(up_panel),
            FadeIn(caption),
            run_time=0.8,
        )

        # Place agent at initial state
        initial_state = steps[0].get("state", 0)
        if isinstance(initial_state, int):
            try:
                if hasattr(heatmap, "place_agent"):
                    heatmap.place_agent(
                        self,
                        initial_state,
                        direction=ACTION_DIR.get(steps[0].get("action", 1), "down"),
                    )
            except Exception:  # noqa: BLE001
                pass

        self.wait(0.5)

        # ------------------------------------------------------------------
        # Step loop
        # ------------------------------------------------------------------
        total = len(steps)
        for idx, step in enumerate(steps[1:], start=2):
            anims = []

            # -- Environment panel (heatmap update + agent move) -----------
            new_env_hash = _env_hash(step)
            if new_env_hash != prev_env_hash:
                # Update heatmap values if present
                updated_values_raw = step.get("updated_values")
                if updated_values_raw and hasattr(heatmap, "sweep_update"):
                    parsed = _parse_updated_values(updated_values_raw)
                    if parsed:
                        try:
                            # Convert int-keyed dict to list for the heatmap
                            # EnvironmentValueHeatmap._normalize_values handles both
                            heatmap.sweep_update(self, parsed)
                        except Exception:  # noqa: BLE001
                            pass

                # Move agent
                next_state = step.get("next_state")
                action = step.get("action")
                direction = ACTION_DIR.get(action, "down") if isinstance(action, int) else "down"
                if isinstance(next_state, int) and hasattr(heatmap, "move_agent"):
                    try:
                        heatmap.move_agent(self, next_state, direction=direction)
                    except Exception:  # noqa: BLE001
                        pass
                prev_env_hash = new_env_hash

            # -- Equation panel --------------------------------------------
            new_eq_hash = _eq_hash(step)
            if new_eq_hash != prev_eq_hash:
                next_eq = _build_equation_panel(step).move_to(EQUATION_POS)
                anims.append(ReplacementTransform(eq_panel, next_eq))
                eq_panel = next_eq
                prev_eq_hash = new_eq_hash

            # -- Backup panel ----------------------------------------------
            new_bk_hash = _bk_hash(step)
            if new_bk_hash != prev_bk_hash:
                next_bk = _build_backup_panel(step).move_to(BACKUP_POS)
                anims.append(ReplacementTransform(bk_panel, next_bk))
                bk_panel = next_bk
                prev_bk_hash = new_bk_hash

            # -- Update panel ----------------------------------------------
            new_up_hash = _up_hash(step)
            if new_up_hash != prev_up_hash:
                next_up = _build_update_panel(step).move_to(UPDATE_POS)
                anims.append(ReplacementTransform(up_panel, next_up))
                up_panel = next_up
                prev_up_hash = new_up_hash

            # -- Caption (always refresh) ----------------------------------
            next_caption = _build_caption(step, idx, total).move_to(CAPTION_POS)
            anims.append(ReplacementTransform(caption, next_caption))
            caption = next_caption

            if anims:
                self.play(*anims, run_time=0.75)

            self.wait(0.35)

        self.wait(1.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _show_error(self, message: str) -> None:
        """Display an error message and exit gracefully (no exception)."""
        mob = Text(message, font_size=28, color=TEXT)
        self.play(FadeIn(mob))
        self.wait(1.5)

    def _build_heatmap(self, first_step: dict):
        """Build EnvironmentValueHeatmap; fall back to ValueHeatmap on any error."""
        # Try to parse initial values from the first step
        initial_values = None
        raw_uv = first_step.get("updated_values")
        if raw_uv:
            parsed = _parse_updated_values(raw_uv)
            if parsed:
                # Build a 16-element list (None for missing)
                arr = [None] * 16
                for state_idx, v in parsed.items():
                    if 0 <= state_idx < 16:
                        arr[state_idx] = v
                initial_values = arr

        # Attempt to import and construct EnvironmentValueHeatmap
        try:
            from manim_service.scenes.rl_visuals import EnvironmentValueHeatmap
            heatmap = EnvironmentValueHeatmap(
                rows=4,
                cols=4,
                values=initial_values,
                width=5.2,
            )
            return heatmap
        except Exception:  # noqa: BLE001
            pass

        # Fallback to ValueHeatmap (no sprites, pure geometric heatmap)
        try:
            from manim_service.scenes.rl_visuals import ValueHeatmap
            heatmap = ValueHeatmap(
                rows=4,
                cols=4,
                values=initial_values,
                width=5.2,
            )
            return heatmap
        except Exception:  # noqa: BLE001
            pass

        # Ultimate fallback: a plain labeled rectangle
        from manim import Rectangle
        box = Rectangle(width=5.2, height=5.2, fill_color="#0F172A", fill_opacity=0.9)
        label = Text("FrozenLake 4x4", font_size=22, color=TEXT)
        label.move_to(box.get_center())
        return VGroup(box, label)
