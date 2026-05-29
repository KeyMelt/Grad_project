"""rl_intro — What Is Reinforcement Learning?

Concept video: Series Video 1 of 15.
Scene class: RLIntroConcept

No MathTex, no CodeStepper, no ValueHeatmap, no ActionBarChart,
no BackupDiagram, no PolicyArrowGrid, no SynchronizedFocusGroup.

Phase structure (7 phases, concrete-to-abstract):
  Phase 1 — FrozenLake motivation: elf walks, fails (×2), succeeds
  Phase 2 — Three-way ML contrast diagram
  Phase 3 — Abstract RL loop diagram (agent box + env box + 3 arrows)
  Phase 4 — Loop cycle animation × 2
  Phase 5 — Reward signal and cumulative goal (path contrast)
  Phase 6 — Named RL features: Trial-and-Error + Delayed Reward
  Phase 7 — Takeaway + closing connection to mdp_framework

Technical Validator confirmed facts (hardcoded):
  Hole states: {5, 7, 11, 12}
  Success path: 0→4→8→9→10→14→15
  Goal reward = 1.0 fires on ARRIVAL at state 15
"""
from __future__ import annotations

import sys
from math import pi
from pathlib import Path

# Allow running from project root: python -m manim -ql ... RLIntroConcept
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from manim import (
    BOLD,
    AnimationGroup,
    CurvedArrow,
    DOWN,
    DashedLine,
    FadeIn,
    FadeOut,
    Flash,
    Group,
    ImageMobject,
    Indicate,
    LEFT,
    LaggedStart,
    ORIGIN,
    RIGHT,
    Rectangle,
    RoundedRectangle,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
)

try:
    from manim import GREY_A
except ImportError:
    GREY_A = "#BBBBBB"

from manim_service.scenes import (
    ACTION_COLOR,
    BG_PANEL,
    CODE_ACCENT,
    OPACITY_SECONDARY,
    PENALTY_COLOR,
    POLICY_COLOR,
    REWARD_COLOR,
    STATE_COLOR,
    BaseConceptScene,
    frozenlake_frame,
    zoom_reset,
    zoom_to,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# 4×4 FrozenLake layout (row-major, 0-indexed)
# Row 0: 0  1  2  3
# Row 1: 4  5  6  7
# Row 2: 8  9 10 11
# Row 3: 12 13 14 15
_HOLES = {5, 7, 11, 12}
_GOAL = 15
_START = 0

# Success path (Technical Validator confirmed — hole-free)
_SUCCESS_PATH = [0, 4, 8, 9, 10, 14, 15]

# Attempt 1 failure path (hits hole 7)
_FAIL_PATH_1 = [0, 1, 2, 6, 7]

# Attempt 2 failure path (hits hole 12)
_FAIL_PATH_2 = [0, 4, 8, 12]

# Gymnasium asset directory
_GYM_ASSET_DIR: Path | None = None
try:
    import gymnasium.envs.toy_text.frozen_lake as _fl
    _GYM_ASSET_DIR = Path(_fl.__file__).resolve().parent / "img"
except ImportError:
    pass

# Grid layout constants
_CELL_SIZE = 0.72         # each tile is 0.72 units square
_GRID_COLS = 4
_GRID_ROWS = 4
_SPRITE_HEIGHT = 0.58     # elf sprite height inside a cell


def _tile_center(state: int, grid_origin: np.ndarray) -> np.ndarray:
    """Return world-space center of a grid tile given the grid's top-left origin."""
    row = state // _GRID_COLS
    col = state % _GRID_COLS
    x = grid_origin[0] + (col + 0.5) * _CELL_SIZE
    y = grid_origin[1] - (row + 0.5) * _CELL_SIZE
    return np.array([x, y, 0.0])


def _grid_origin(grid_center: np.ndarray) -> np.ndarray:
    """Compute top-left corner from grid center."""
    half = _GRID_COLS * _CELL_SIZE / 2.0
    return np.array([
        grid_center[0] - half,
        grid_center[1] + half,
        0.0,
    ])


# ---------------------------------------------------------------------------
# Grid builder — builds a 4×4 FrozenLake grid from individual tile images
# ---------------------------------------------------------------------------

def _load_sprite(name: str, height: float) -> ImageMobject | Rectangle:
    """Load a sprite from the Gym asset directory, or return a colored rect."""
    if _GYM_ASSET_DIR is not None:
        p = _GYM_ASSET_DIR / name
        if p.exists():
            img = ImageMobject(str(p))
            img.set_height(height)
            return img
    # Fallback rectangle
    colors = {
        "ice.png": BG_PANEL,
        "stool.png": STATE_COLOR,
        "hole.png": PENALTY_COLOR,
        "goal.png": REWARD_COLOR,
        "cracked_hole.png": PENALTY_COLOR,
        "elf_right.png": POLICY_COLOR,
        "elf_down.png": POLICY_COLOR,
        "elf_up.png": POLICY_COLOR,
        "elf_left.png": POLICY_COLOR,
    }
    rect = Rectangle(
        width=height,
        height=height,
        fill_color=colors.get(name, BG_PANEL),
        fill_opacity=0.85,
        stroke_width=0,
    )
    return rect


def _build_grid(center: np.ndarray, scale: float = 1.0) -> tuple[Group, np.ndarray, list]:
    """Build a 4×4 FrozenLake grid VGroup, return (grid_group, grid_origin, tile_centers).

    Returns:
        grid_group: Group containing all tile images
        origin: top-left corner position
        tile_centers: list of 16 world-space center points
    """
    cs = _CELL_SIZE * scale
    total = _GRID_COLS * cs
    origin = np.array([center[0] - total / 2, center[1] + total / 2, 0.0])

    tiles = []
    for state in range(16):
        row = state // _GRID_COLS
        col = state % _GRID_COLS
        cx = origin[0] + (col + 0.5) * cs
        cy = origin[1] - (row + 0.5) * cs

        if state == _START:
            img = _load_sprite("stool.png", cs * 0.92)
        elif state in _HOLES:
            img = _load_sprite("hole.png", cs * 0.92)
        elif state == _GOAL:
            img = _load_sprite("goal.png", cs * 0.92)
        else:
            img = _load_sprite("ice.png", cs * 0.92)

        img.move_to([cx, cy, 0.0])
        tiles.append(img)

    # Background grid border
    border = RoundedRectangle(
        width=total + 0.14,
        height=total + 0.14,
        corner_radius=0.14,
        fill_color=BG_PANEL,
        fill_opacity=1.0,
        stroke_color=STATE_COLOR,
        stroke_width=1.4,
    )
    border.set_stroke(opacity=0.55)
    border.move_to(center)

    # Cell borders
    cell_borders = []
    for state in range(16):
        row = state // _GRID_COLS
        col = state % _GRID_COLS
        cx = origin[0] + (col + 0.5) * cs
        cy = origin[1] - (row + 0.5) * cs
        stroke_col = PENALTY_COLOR if state in _HOLES else (REWARD_COLOR if state == _GOAL else STATE_COLOR)
        cb = Rectangle(
            width=cs - 0.03,
            height=cs - 0.03,
            fill_opacity=0.0,
            stroke_color=stroke_col,
            stroke_width=1.0,
        )
        cb.move_to([cx, cy, 0.0])
        cell_borders.append(cb)

    grid_group = Group(border, *cell_borders, *tiles)

    tile_centers = []
    for state in range(16):
        row = state // _GRID_COLS
        col = state % _GRID_COLS
        cx = origin[0] + (col + 0.5) * cs
        cy = origin[1] - (row + 0.5) * cs
        tile_centers.append(np.array([cx, cy, 0.0]))

    return grid_group, origin, tile_centers


# ---------------------------------------------------------------------------
# Main scene
# ---------------------------------------------------------------------------

class RLIntroConcept(BaseConceptScene):
    """Video 1 of 15 — What Is Reinforcement Learning?"""

    def construct(self) -> None:
        self._phase1_frozenlake_motivation()
        self._phase2_ml_contrast()
        self._phase3_loop_diagram()
        self._phase4_cycle_animation()
        self._phase5_path_contrast()
        self._phase6_named_features()
        self._phase7_takeaway()

    # ==========================================================================
    # PHASE 1 — FrozenLake Motivation
    # ==========================================================================

    def _phase1_frozenlake_motivation(self) -> None:
        self.mark_phase("geometry_entry")

        # ── 1a: Header + Grid Introduction ────────────────────────────────────
        self._header = self.show_header(
            "What Is Reinforcement Learning?",
            subtitle="Learning by interacting with an environment",
        )

        # Build full 4×4 grid centered on screen
        grid_center = ORIGIN
        self._grid, self._grid_origin, self._tile_centers = _build_grid(
            np.array([0.0, 0.0, 0.0])
        )

        # Fade in all tiles with LaggedStart
        all_tiles = list(self._grid)  # Group supports iteration
        self.play(
            LaggedStart(*[FadeIn(t) for t in all_tiles], lag_ratio=0.05),
            run_time=1.5,
        )

        # Pulse goal tile and hole tile borders to call out key locations
        goal_tile = all_tiles[2 + 15]  # offset 2 (border+cell_borders skip) not reliable
        # Use grid_group directly — indicate the border of goal cell (index 2+15=17) and holes
        # More reliable: use the cell_border VGroup items directly
        # cell_borders are indices 1..16 of the Group, tiles are 17..32
        goal_border_idx = 1 + _GOAL  # 1 border + _GOAL offset in cell_borders
        self.play(
            Indicate(self._grid[goal_border_idx], color=REWARD_COLOR, scale_factor=1.08, run_time=0.8),
        )
        # Indicate all hole borders
        hole_indicates = [
            Indicate(self._grid[1 + h], color=PENALTY_COLOR, scale_factor=1.05, run_time=0.8)
            for h in sorted(_HOLES)
        ]
        self.play(LaggedStart(*hole_indicates, lag_ratio=0.15), run_time=0.8)

        # Place elf sprite at start tile (state 0) with elf_right.png
        # Caption and elf appear together per choreo §5 Phase 1a row 4.7s/5.0s
        self._caption = self.place_caption(
            "The elf wants to reach the goal — but the ice is slippery and there are holes."
        )
        self._elf_sprite = _load_sprite("elf_right.png", _SPRITE_HEIGHT)
        self._elf_sprite.move_to(self._tile_centers[_START])
        self._current_sprite_file = "elf_right.png"
        self.play(FadeIn(self._elf_sprite), FadeIn(self._caption))

        # First geometry reveal minimum wait (STYLE_BIBLE §6)
        self.wait(3.5)

        # ── 1b: Attempt 1 — Elf fails at hole 7 ──────────────────────────────
        self.mark_phase("attempt_1_failure")
        new_cap = self.place_caption(
            "The elf doesn't know the rules of the ice — it only sees what happens after each step."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # Path: 0→1→2→6→7
        # Step 0→1 (RIGHT, elf_right already)
        self._walk_step(0, 1, "elf_right.png")
        # Step 1→2 (RIGHT)
        self._walk_step(1, 2, "elf_right.png")
        # Step 2→6 (DOWN)
        self._walk_step(2, 6, "elf_down.png")
        # Step 6→7 (DOWN) — hits hole
        self._walk_step(6, 7, "elf_down.png")

        # Hole flash
        self.play(
            Flash(
                self._get_tile_rect(7),
                color=PENALTY_COLOR,
                flash_radius=0.4,
                run_time=0.5,
            )
        )
        self.play(FadeOut(self._elf_sprite, run_time=0.4))

        # Reset elf to start (track sprite file to avoid spurious swaps)
        self._elf_sprite = _load_sprite("elf_right.png", _SPRITE_HEIGHT)
        self._elf_sprite.move_to(self._tile_centers[_START])
        self._current_sprite_file = "elf_right.png"
        self.play(FadeIn(self._elf_sprite, run_time=0.4))

        self.wait(3.5)

        # ── 1c: Attempt 2 — Elf fails at hole 12 ─────────────────────────────
        self.mark_phase("attempt_2_failure")
        new_cap = self.place_caption("No one tells it the right moves — it has to figure them out.")
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # Path: 0→4→8→12
        self._walk_step(0, 4, "elf_down.png")
        self._walk_step(4, 8, "elf_down.png")
        self._walk_step(8, 12, "elf_down.png")

        # Hole flash
        self.play(
            Flash(
                self._get_tile_rect(12),
                color=PENALTY_COLOR,
                flash_radius=0.4,
                run_time=0.5,
            )
        )
        self.play(FadeOut(self._elf_sprite, run_time=0.4))

        # Reset elf to start
        self._elf_sprite = _load_sprite("elf_down.png", _SPRITE_HEIGHT)
        self._elf_sprite.move_to(self._tile_centers[_START])
        self._current_sprite_file = "elf_down.png"
        self.play(FadeIn(self._elf_sprite, run_time=0.4))

        self.wait(3.0)

        # ── 1d: Attempt 3 — Elf succeeds (0→4→8→9→10→14→15) ────────────────
        self.mark_phase("attempt_3_success")
        new_cap = self.place_caption(
            "When the elf reaches the goal, it receives a reward — a single number that says 'that was good.'"
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # Path: 0→4→8→9→10→14→15
        self._walk_step(0, 4, "elf_down.png")
        self._walk_step(4, 8, "elf_down.png")
        self._walk_step(8, 9, "elf_right.png")
        self._walk_step(9, 10, "elf_right.png")
        self._walk_step(10, 14, "elf_down.png")
        self._walk_step(14, 15, "elf_right.png")

        # Goal flash + reward label
        self.play(
            Flash(
                self._get_tile_rect(15),
                color=REWARD_COLOR,
                flash_radius=0.6,
                run_time=0.6,
            )
        )
        reward_label = Text("+1", font_size=22, color=REWARD_COLOR)
        reward_label.move_to(self._tile_centers[15] + UP * 0.55)
        self.play(FadeIn(reward_label))
        self.wait(2.0)
        self.play(FadeOut(reward_label, run_time=0.5))
        self.wait(3.5)

        # ── 1e: Closing + FadeOut ──────────────────────────────────────────────
        self.mark_phase("phase1_close")
        self.play(FadeOut(self._elf_sprite, run_time=0.5))
        new_cap = self.place_caption(
            "This is the reinforcement learning problem: learn to act by interacting, with no labels — only rewards."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap
        self.wait(3.0)

        # zoom_reset before FadeOut (camera may have panned)
        zoom_reset(self, run_time=1.6)
        self.ingestion_wait(2.5)

        self.play(FadeOut(self._grid), FadeOut(self._caption, run_time=1.0))
        self.ingestion_wait(2.5)

    # ── Helper: walk one step with sprite swap ──────────────────────────────
    def _walk_step(self, from_state: int, to_state: int, sprite_file: str) -> None:
        """Swap sprite direction and smooth_move_to the target tile center."""
        # Swap sprite if direction changed
        current_file = getattr(self, "_current_sprite_file", None)
        if current_file != sprite_file:
            new_sprite = _load_sprite(sprite_file, _SPRITE_HEIGHT)
            new_sprite.move_to(self._elf_sprite.get_center())
            self.play(
                FadeOut(self._elf_sprite, run_time=0.15),
                FadeIn(new_sprite, run_time=0.15),
                run_time=0.15,
            )
            self._elf_sprite = new_sprite
            self._current_sprite_file = sprite_file

        # Move to target tile
        target = self._tile_centers[to_state]
        self.smooth_move_to(self._elf_sprite, target, run_time=1.0, min_run_time=1.0)

    def _get_tile_rect(self, state: int) -> Rectangle:
        """Return a rectangle covering the tile for use in Flash."""
        cs = _CELL_SIZE
        rect = Rectangle(
            width=cs * 0.85,
            height=cs * 0.85,
            fill_opacity=0.0,
            stroke_width=0,
        )
        rect.move_to(self._tile_centers[state])
        return rect

    # ==========================================================================
    # PHASE 2 — Three-Way ML Contrast
    # ==========================================================================

    def _phase2_ml_contrast(self) -> None:
        self.mark_phase("ml_contrast")

        intro_cap = self.place_caption("Machine learning has three distinct paradigms.")
        self.play(FadeIn(intro_cap))
        self._caption = intro_cap

        # Build three panels
        supervised_panel = self._build_ml_panel(
            "Supervised Learning",
            "Learns from labeled examples",
            "(input  →  correct label)",
            "A supervisor knows the right answer",
            stroke_color=CODE_ACCENT,
        )
        unsupervised_panel = self._build_ml_panel(
            "Unsupervised Learning",
            "Finds hidden structure in data",
            "(no labels, no feedback)",
            "No labels, no rewards",
            stroke_color=CODE_ACCENT,
        )
        rl_panel = self._build_ml_panel(
            "Reinforcement Learning",
            "Learns by trial and error",
            "No labels — just rewards",
            "No supervisor, no dataset",
            stroke_color=REWARD_COLOR,
            title_color=REWARD_COLOR,
            body_color=WHITE,
        )

        # Arrange horizontally — total width ~8.5 units
        panels_group = VGroup(supervised_panel, unsupervised_panel, rl_panel)
        panels_group.arrange(RIGHT, buff=0.28)
        panels_group.move_to(ORIGIN)

        # Staggered reveal: supervised first, then unsupervised, then rl
        # As each new panel enters, dim prior ones to SECONDARY
        self.play(
            LaggedStart(
                FadeIn(supervised_panel),
                AnimationGroup(
                    FadeIn(unsupervised_panel),
                    supervised_panel.animate.set_opacity(OPACITY_SECONDARY),
                ),
                AnimationGroup(
                    FadeIn(rl_panel),
                    unsupervised_panel.animate.set_opacity(OPACITY_SECONDARY),
                    supervised_panel.animate.set_opacity(OPACITY_SECONDARY),
                ),
                lag_ratio=0.5,
            )
        )

        # First geometry reveal wait
        self.wait(3.5)

        # Question mark float above rl_panel
        question_mark = Text("?", font_size=32, color=POLICY_COLOR)
        question_mark.next_to(rl_panel, UP, buff=0.28)
        self.play(FadeIn(question_mark))

        # Ingestion wait after rl_panel FadeIn (structural change)
        self.ingestion_wait(2.5)

        new_cap = self.place_caption(
            "RL is a third paradigm — no labeled examples, no supervisor, just a reward signal."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # Question mark fades, reward arrow icon appears
        self.play(FadeOut(question_mark, run_time=0.4))

        # Small reward color arrow icon on rl_panel
        rl_arrow_icon = Text("→", font_size=22, color=REWARD_COLOR)
        rl_arrow_icon.next_to(rl_panel, UP, buff=0.18)
        self.play(FadeIn(rl_arrow_icon, run_time=0.4))

        # Indicate rl_panel border
        self.play(
            Indicate(rl_panel[0], color=REWARD_COLOR, scale_factor=1.08, run_time=0.7)
        )
        self.wait(3.5)

        new_cap2 = self.place_caption(
            "The agent must discover which actions are good — the supervisor does not exist."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap2))
        self._caption = new_cap2
        self.wait(3.5)

        # Fade out all panels
        self.play(
            FadeOut(supervised_panel),
            FadeOut(unsupervised_panel),
            FadeOut(rl_panel),
            FadeOut(rl_arrow_icon),
            FadeOut(self._caption),
            run_time=1.0,
        )
        self.ingestion_wait(2.5)

    def _build_ml_panel(
        self,
        title: str,
        body_main: str,
        body_sub: str,
        body_bottom: str,
        stroke_color: str = CODE_ACCENT,
        title_color: str = WHITE,
        body_color: str = CODE_ACCENT,
    ) -> VGroup:
        """Build a single ML contrast panel."""
        title_mob = Text(title, font_size=19, color=title_color)
        body_main_mob = Text(body_main, font_size=17, color=body_color)
        body_sub_mob = Text(body_sub, font_size=15, color=CODE_ACCENT)
        body_bottom_mob = Text(body_bottom, font_size=15, color=CODE_ACCENT)

        content = VGroup(title_mob, body_main_mob, body_sub_mob, body_bottom_mob)
        content.arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        panel_w = max(content.get_width() + 0.5, 2.7)
        panel_h = max(content.get_height() + 0.45, 3.1)

        bg = RoundedRectangle(
            width=panel_w,
            height=panel_h,
            corner_radius=0.14,
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=stroke_color,
            stroke_width=1.5,
        )
        content.move_to(bg.get_center())
        return VGroup(bg, content)

    # ==========================================================================
    # PHASE 3 — Abstract RL Loop Diagram
    # ==========================================================================

    def _phase3_loop_diagram(self) -> None:
        self.mark_phase("loop_diagram")

        # ── 3a: Agent box ─────────────────────────────────────────────────────
        cap_3a = self.place_caption("The Agent — the decision-maker.")
        self.play(FadeIn(cap_3a))
        self._caption = cap_3a

        self._agent_box = self._build_loop_box("Agent", POLICY_COLOR, ORIGIN + LEFT * 2.2)
        self.play(FadeIn(self._agent_box))
        self.wait(2.5)

        # ── 3b: Environment box ───────────────────────────────────────────────
        new_cap = self.place_caption("The Environment — everything the agent interacts with.")
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        self._env_box = self._build_loop_box("Environment", STATE_COLOR, ORIGIN + RIGHT * 2.2)
        self.play(
            FadeIn(self._env_box),
            self._agent_box.animate.set_opacity(OPACITY_SECONDARY),
            run_time=0.8,
        )
        self.wait(3.0)
        self.ingestion_wait(2.5)  # Second box FadeIn = structural change

        # ── 3c: Action arrow (Agent → Env, curves below) ──────────────────────
        new_cap = self.place_caption("The Agent chooses an Action.")
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # CurvedArrow from agent bottom-right to env bottom-left, curving downward
        agent_bottom_right = self._agent_box.get_bottom() + RIGHT * 0.4
        env_bottom_left = self._env_box.get_bottom() + LEFT * 0.4
        self._action_arrow = CurvedArrow(
            agent_bottom_right,
            env_bottom_left,
            angle=pi / 3,  # curves downward
            color=ACTION_COLOR,
            stroke_width=2.5,
        )
        action_label = Text("Action", font_size=20, color=ACTION_COLOR)
        action_label.next_to(self._action_arrow.get_center(), DOWN, buff=0.22)
        self._action_label = action_label

        self.play(
            FadeIn(self._action_arrow),
            FadeIn(action_label),
            self._agent_box.animate.set_opacity(OPACITY_SECONDARY),
            self._env_box.animate.set_opacity(OPACITY_SECONDARY),
            run_time=0.8,
        )
        self.wait(2.5)

        # ── 3d: State/Observation arrow (Env → Agent, outer upper arc) ─────────
        new_cap = self.place_caption("The Environment sends back the State — what the agent perceives.")
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # CurvedArrow from env top-left to agent top-right, angle=-PI/3 (outer arc)
        env_top_left = self._env_box.get_top() + LEFT * 0.4
        agent_top_right = self._agent_box.get_top() + RIGHT * 0.4
        self._state_obs_arrow = CurvedArrow(
            env_top_left,
            agent_top_right,
            angle=-pi / 3,
            color=STATE_COLOR,
            stroke_width=2.5,
        )
        # Two-line label: "State" + "/ Observation"
        state_label_top = Text("State", font_size=20, color=STATE_COLOR)
        state_label_bot = Text("/ Observation", font_size=16, color=STATE_COLOR)
        state_label_bot.set_opacity(0.7)
        state_label_vgroup = VGroup(state_label_top, state_label_bot)
        state_label_vgroup.arrange(DOWN, buff=0.05)
        state_label_vgroup.next_to(self._state_obs_arrow.get_center(), UP, buff=0.22)
        self._state_obs_label = state_label_vgroup

        self.play(
            FadeIn(self._state_obs_arrow),
            FadeIn(state_label_vgroup),
            self._action_arrow.animate.set_opacity(OPACITY_SECONDARY),
            self._action_label.animate.set_opacity(OPACITY_SECONDARY),
            run_time=0.8,
        )
        self.wait(3.0)
        self.ingestion_wait(2.5)  # State arrow FadeIn = structural change

        # ── 3e: Reward arrow (Env → Agent, inner upper arc) ──────────────────
        new_cap = self.place_caption("The Environment also sends a Reward — a single number.")
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # CurvedArrow from env top-left (slightly offset) to agent top-right, angle=-PI/4
        env_top_inner = self._env_box.get_top() + LEFT * 0.8
        agent_top_inner = self._agent_box.get_top() + RIGHT * 0.8
        self._reward_arrow = CurvedArrow(
            env_top_inner,
            agent_top_inner,
            angle=-pi / 4,
            color=REWARD_COLOR,
            stroke_width=2.5,
        )
        reward_label = Text("Reward", font_size=20, color=REWARD_COLOR)
        reward_label.next_to(self._reward_arrow.get_center(), UP, buff=0.18)
        reward_label.shift(RIGHT * 0.3)  # shift right to clear State label
        self._reward_label = reward_label

        self.play(
            FadeIn(self._reward_arrow),
            FadeIn(reward_label),
            self._state_obs_arrow.animate.set_opacity(OPACITY_SECONDARY),
            self._state_obs_label.animate.set_opacity(OPACITY_SECONDARY),
            run_time=0.8,
        )
        self.wait(3.0)
        self.ingestion_wait(2.5)  # Loop diagram complete = structural change

        # ── 3f: Full loop revealed ────────────────────────────────────────────
        new_cap = self.place_caption(
            "In FrozenLake, the elf sees its exact state — not always the case in RL."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap
        self.wait(4.5)  # Full loop first geometry reveal minimum

        # Store loop diagram as a group for Phase 4 operations
        self._loop_diagram = VGroup(
            self._agent_box,
            self._env_box,
            self._action_arrow,
            self._action_label,
            self._state_obs_arrow,
            self._state_obs_label,
            self._reward_arrow,
            self._reward_label,
        )

    def _build_loop_box(self, label: str, color: str, position) -> VGroup:
        """Build a labeled loop diagram box."""
        bg = RoundedRectangle(
            width=2.8,
            height=1.6,
            corner_radius=0.18,
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=color,
            stroke_width=2.0,
        )
        label_mob = Text(label, font_size=24, color=color)
        label_mob.move_to(bg.get_center())
        box = VGroup(bg, label_mob)
        box.move_to(position)
        return box

    # ==========================================================================
    # PHASE 4 — Loop Cycle Animation × 2
    # ==========================================================================

    def _phase4_cycle_animation(self) -> None:
        self.mark_phase("cycle_animation")

        # Dim all loop elements before cycle begins (they were partially dimmed already)
        self.play(
            self._loop_diagram.animate.set_opacity(OPACITY_SECONDARY),
            run_time=0.5,
        )

        # Zoom in on loop diagram for cycle animation
        zoom_to(self, self._loop_diagram, scale=0.75, run_time=1.5)
        self.ingestion_wait(2.5)  # zoom_to = major structural morph

        new_cap = self.place_caption(
            "At every time step: observe state, choose action, receive reward."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap))
        self._caption = new_cap

        # Cycle 1 (run_time=0.6 per node)
        cycle_nodes = [
            (self._agent_box, POLICY_COLOR),
            (self._action_arrow, ACTION_COLOR),
            (self._env_box, STATE_COLOR),
            (self._state_obs_arrow, STATE_COLOR),
            (self._reward_arrow, REWARD_COLOR),
            (self._agent_box, POLICY_COLOR),  # loop closes
        ]
        for node, color in cycle_nodes:
            self.play(
                Indicate(node, color=color, scale_factor=1.1, run_time=0.6)
            )
            self.wait(0.7)

        self.wait(3.0)

        # Cycle 2 (run_time=0.5, faster to reinforce rhythm)
        new_cap2 = self.place_caption("This repeats on every time step.")
        self.play(FadeOut(self._caption), FadeIn(new_cap2))
        self._caption = new_cap2

        for node, color in cycle_nodes:
            self.play(
                Indicate(node, color=color, scale_factor=1.1, run_time=0.5)
            )
            self.wait(0.7)

        self.wait(3.0)
        self.ingestion_wait(2.5)  # End of cycle sequence

        # Zoom reset before Phase 5
        zoom_reset(self, run_time=1.6)
        self.ingestion_wait(2.5)  # zoom_reset = major structural morph

        # FadeOut full loop diagram
        self.play(
            FadeOut(self._loop_diagram),
            FadeOut(self._caption),
            run_time=1.0,
        )
        self.ingestion_wait(2.5)  # Diagram FadeOut = structural change

    # ==========================================================================
    # PHASE 5 — Path Contrast (Reward Signal + Cumulative Goal)
    # ==========================================================================

    def _phase5_path_contrast(self) -> None:
        self.mark_phase("path_contrast")

        new_cap = self.place_caption(
            "The agent wants to accumulate reward over the whole episode — not just survive the next step."
        )
        self.play(FadeIn(new_cap))
        self._caption = new_cap

        # Build Phase 5 FrozenLake grid at 85% scale, centered
        self._grid5, self._grid5_origin, self._tile_centers5 = _build_grid(
            np.array([0.0, 0.0, 0.0]),
            scale=0.85,
        )
        self.play(FadeIn(self._grid5))

        # Draw success path trail (REWARD_COLOR dashed lines)
        path_A_segments = self._build_path_trail(
            _SUCCESS_PATH, REWARD_COLOR, self._tile_centers5
        )
        # Draw failure path trail (PENALTY_COLOR dashed lines)
        path_B_segments = self._build_path_trail(
            _FAIL_PATH_1, PENALTY_COLOR, self._tile_centers5
        )

        self.play(
            LaggedStart(
                *[Write(seg) for seg in path_A_segments],
                lag_ratio=0.2,
            ),
            run_time=1.5,
        )
        self.play(
            LaggedStart(
                *[Write(seg) for seg in path_B_segments],
                lag_ratio=0.2,
            ),
            run_time=1.2,
        )

        # Outcome labels
        reward_label_A = Text("+1", font_size=18, color=REWARD_COLOR)
        reward_label_A.move_to(self._tile_centers5[15] + UP * 0.45)

        reward_label_B = Text("0", font_size=18, color=CODE_ACCENT)
        reward_label_B.move_to(self._tile_centers5[7] + UP * 0.45)

        x_mark = Text("×", font_size=20, color=PENALTY_COLOR)
        x_mark.move_to(self._tile_centers5[7] + RIGHT * 0.0 + DOWN * 0.1)

        self.play(
            LaggedStart(
                FadeIn(reward_label_A),
                FadeIn(reward_label_B),
                FadeIn(x_mark),
                lag_ratio=0.15,
            )
        )

        # First geometry reveal of path contrast (STYLE_BIBLE §6)
        self.wait(4.0)

        new_cap2 = self.place_caption(
            "Rewards can be positive, zero, or negative — the exact values depend on the environment."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap2))
        self._caption = new_cap2
        self.wait(3.0)

        new_cap3 = self.place_caption("The goal: more total reward over time.")
        self.play(FadeOut(self._caption), FadeIn(new_cap3))
        self._caption = new_cap3
        self.wait(3.0)

        # FadeOut everything from Phase 5
        path_A_group = VGroup(*path_A_segments)
        path_B_group = VGroup(*path_B_segments)
        self.play(
            FadeOut(self._grid5),
            FadeOut(path_A_group),
            FadeOut(path_B_group),
            FadeOut(reward_label_A),
            FadeOut(reward_label_B),
            FadeOut(x_mark),
            FadeOut(self._caption),
            run_time=1.0,
        )
        self.ingestion_wait(2.5)

    def _build_path_trail(
        self, path: list[int], color: str, tile_centers: list
    ) -> list[DashedLine]:
        """Build a list of DashedLine segments connecting tile centers."""
        segments = []
        for i in range(len(path) - 1):
            start = tile_centers[path[i]]
            end = tile_centers[path[i + 1]]
            seg = DashedLine(
                start,
                end,
                color=color,
                stroke_width=3.0,
                dash_length=0.08,
            )
            segments.append(seg)
        return segments

    # ==========================================================================
    # PHASE 6 — Named RL Features
    # ==========================================================================

    def _phase6_named_features(self) -> None:
        self.mark_phase("named_features")

        # Card 1 — Trial-and-Error Search
        card_1 = self._build_feature_card(
            "Trial-and-Error Search",
            "The agent must explore — no supervisor labels which action is correct.",
        )
        card_2 = self._build_feature_card(
            "Delayed Reward",
            "An action now may affect rewards many steps later.",
        )

        cards = VGroup(card_1, card_2)
        cards.arrange(DOWN, buff=0.3)
        cards.move_to(ORIGIN)

        new_cap = self.place_caption(
            "RL's first distinguishing feature: the agent discovers good actions by trying them."
        )
        self.play(FadeIn(new_cap))
        self._caption = new_cap

        self.play(FadeIn(card_1))
        self.wait(4.0)

        new_cap2 = self.place_caption(
            "RL's second distinguishing feature: reward may arrive long after the action that caused it."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap2))
        self._caption = new_cap2

        self.play(
            FadeIn(card_2),
            card_1.animate.set_opacity(OPACITY_SECONDARY),
        )
        self.wait(4.0)

        # Both cards now visible; structural composition complete
        self.ingestion_wait(2.5)

        new_cap3 = self.place_caption(
            "The agent also faces a challenge: try known good actions, or explore new ones — a tension we will return to."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap3))
        self._caption = new_cap3
        self.wait(3.5)

        self.play(
            FadeOut(card_1),
            FadeOut(card_2),
            FadeOut(self._caption),
            run_time=1.0,
        )
        self.ingestion_wait(2.5)

    def _build_feature_card(self, title: str, body: str) -> VGroup:
        """Build a feature label card."""
        title_mob = Text(title, font_size=26, color=WHITE, weight=BOLD)
        body_mob = Text(body, font_size=17, color=CODE_ACCENT)
        content = VGroup(title_mob, body_mob)
        content.arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        card_w = max(content.get_width() + 0.55, 5.0)
        card_h = max(content.get_height() + 0.45, 1.8)

        bg = RoundedRectangle(
            width=card_w,
            height=card_h,
            corner_radius=0.14,
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=CODE_ACCENT,
            stroke_width=1.2,
        )
        content.move_to(bg.get_center())
        return VGroup(bg, content)

    # ==========================================================================
    # PHASE 7 — Takeaway + Closing Connection
    # ==========================================================================

    def _phase7_takeaway(self) -> None:
        self.mark_phase("takeaway")

        new_cap = self.place_caption(
            "The agent, the environment, the loop — that is reinforcement learning."
        )
        self.play(FadeIn(new_cap))
        self._caption = new_cap

        # Two-line takeaway text
        takeaway_line1 = Text(
            "Reinforcement learning is the science of learning to act",
            font_size=24,
            color=WHITE,
        )
        takeaway_line2 = Text(
            "by trial and error — no labels, just rewards.",
            font_size=24,
            color=REWARD_COLOR,
        )
        takeaway_vgroup = VGroup(takeaway_line1, takeaway_line2)
        takeaway_vgroup.arrange(DOWN, buff=0.2)
        takeaway_vgroup.move_to(ORIGIN).shift(UP * 0.8)

        self.play(
            LaggedStart(
                Write(takeaway_line1),
                Write(takeaway_line2),
                lag_ratio=0.3,
            )
        )
        self.wait(4.0)

        # FrozenLake ghost at LEFT at OPACITY_SECONDARY
        frozenlake_ghost = frozenlake_frame(state=15)
        frozenlake_ghost.scale(0.65)
        self.place_left_panel(frozenlake_ghost)
        self.play(FadeIn(frozenlake_ghost, run_time=0.8))
        self.play(frozenlake_ghost.animate.set_opacity(OPACITY_SECONDARY), run_time=0.3)

        # Closing connection text
        closing_line1 = Text(
            "Next: the Markov Decision Process",
            font_size=22,
            color=STATE_COLOR,
        )
        closing_line2 = Text(
            "We give this loop a precise mathematical home.",
            font_size=17,
            color=CODE_ACCENT,
        )
        closing_vgroup = VGroup(closing_line1, closing_line2)
        closing_vgroup.arrange(DOWN, buff=0.15)
        closing_vgroup.next_to(takeaway_vgroup, DOWN, buff=0.45)

        self.play(FadeIn(closing_vgroup))

        new_cap2 = self.place_caption(
            "In the next video, we formalize the loop — the Markov Decision Process."
        )
        self.play(FadeOut(self._caption), FadeIn(new_cap2))
        self._caption = new_cap2

        # Final hold (STYLE_BIBLE §6 — mandatory 2.5 s; extended to match narration)
        self.wait(8.0)

        # Clean scene end
        self.play(
            FadeOut(takeaway_vgroup),
            FadeOut(frozenlake_ghost),
            FadeOut(closing_vgroup),
            FadeOut(self._caption),
            FadeOut(self._header),
            run_time=1.0,
        )
