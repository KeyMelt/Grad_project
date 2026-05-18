# Manim Service — Session Log

---

## Session 1 — 2026-05-18

**Completed:**
- `manim_service/` directory skeleton (api/, api/routes/, scenes/, concept_videos/docs/, jobs/, storage/)
- `manim_service/__init__.py`
- `manim_service/settings.py` (MANIM_PYTHON, SHARED_MEDIA_DIR, RENDER_QUALITY, QUEUE_BACKEND)
- `manim_service/api/main.py`, `api/routes/concept_videos.py`, `api/routes/traces.py` — stubs, marked TODO(Session 6)
- `manim_service/jobs/queue.py`, `jobs/worker.py` — stubs, marked TODO(Session 6)
- `manim_service/storage/output.py` — stub, marked TODO(Session 6)
- `manim_service/concept_videos/__init__.py`
- `manim_service/scenes/__init__.py` — full re-export of all panels symbols
- `manim_service/scenes/panels.py` — canonical panel infrastructure (see below)
- `backend/concept_videos/scenes/panels.py` — thin re-export shim pointing at manim_service
- `backend/concept_videos/scenes/__init__.py` — updated to add all panels imports

**panels.py contents:**
- Semantic color palette: STATE_COLOR, VALUE_COLOR, REWARD_COLOR, PENALTY_COLOR, POLICY_COLOR, ACTION_COLOR, BG_COLOR, BG_PANEL, BG_GRID, CODE_ACCENT + legacy aliases
- Opacity constants: OPACITY_PRIMARY/SECONDARY/BACKGROUND
- BaseConceptScene(MovingCameraScene): setup, show_header, assimilation_wait (default 1.5s), place_caption, place_left/right panel anchors
- note_stack(), panel(), code_panel(), equation_panel(), pill()
- frozenlake_frame(), environment_panel(), card_mobject(), blackjack_panel(), cliffwalking_panel()
- FormulaStepper, StatefulHighlighter, HighlightedAnimation / highlighted_animation()
- CodeStepper (three-way sync code line highlighter)
- ActionBarChart(VGroup) — ValueTracker + always_redraw bars, relative positioning to bg ref
- SynchronizedFocusGroup — dim/highlight across parallel item lists
- action_arrows_overlay() — 4-arrow VGroup with .action_idx attributes
- zoom_to() / zoom_reset() — camera frame helpers
- EnvironmentPanel (Protocol, runtime_checkable)
- _FrozenLakePanelImpl, _BlackjackPanelImpl, _CliffWalkingPanelImpl
- env_panel() factory with _ENV_PANEL_REGISTRY (prefix-match dispatch)

**Deviations from plan:**
- `panels.py` placed in `manim_service/scenes/panels.py` (canonical), NOT `backend/concept_videos/scenes/panels.py` as Step 1 of the plan states. The backend path is a thin shim. Rationale: the plan's architectural section specifies `manim_service/scenes/panels.py` as the final home; placing it there now avoids a needless move in Session 6.
- `frozenlake_frame()` resolves the asset path relative to panels.py location (3 parents up to project root), rather than hardcoding an absolute path. This is more portable.

**Next session should know:**
- Session 2 target files: `manim_service/scenes/motion.py` + `manim_service/scenes/rl_visuals.py`
- `motion.py` needs: equation_morph(), token_expand(), staggered_write(), staggered_fadein(), reactive_bar() — see plan "Layer 1 — Helper Infrastructure" table
- `rl_visuals.py` needs: BackupDiagram, PolicyArrowGrid, ValueHeatmap, QValueTable, EpisodeTrail — see plan for each
- Both files should import shared constants from `manim_service.scenes.panels` (STATE_COLOR, etc.)
- After Session 2, update `manim_service/scenes/__init__.py` to re-export the new symbols
- The ActionBarChart.update_bars() method plays animations directly via scene.play() (rather than returning them). This differs slightly from the plan's "→ AnimationGroup" spec. CodeStepper.step() and SynchronizedFocusGroup.step() return lists of animations for the caller to play.
- Import smoke test command: `/Users/ultramarine/.venvs/manim/bin/python -W error::SyntaxWarning -c "import sys; sys.path.insert(0, '.'); from manim_service.scenes.panels import BaseConceptScene, ActionBarChart"`

---

## Session 2 — 2026-05-18

**Completed:**
- `manim_service/scenes/motion.py` — 5 motion primitives
- `manim_service/scenes/rl_visuals.py` — 5 RL visualization classes
- `manim_service/scenes/__init__.py` — updated to re-export all 10 new symbols

**motion.py contents:**
- `equation_morph(scene, old_eq, new_eq, *, run_time, move_to_old)` — TransformMatchingTex wrapper
- `token_expand(scene, compact, expanded, *, run_time)` — compact → expanded form, longer default run_time
- `staggered_write(scene, mobs, *, lag_ratio, run_time)` — LaggedStart + Write
- `staggered_fadein(scene, mobs, *, lag_ratio, run_time, shift)` — LaggedStart + FadeIn with optional shift
- `reactive_bar(tracker, bottom_center, *, max_height, width, color)` — always_redraw bar at fixed bottom_center; use ActionBarChart for moving/referenced bars

**rl_visuals.py contents:**
- `BackupDiagram(VGroup)` — S&B tree: root Circle → action Dots → outcome Circles; methods: highlight_action(), highlight_outcome(), dim_all_except_action(), reset_opacity()
- `PolicyArrowGrid(VGroup)` — rows×cols grid + directional Arrow per cell; action convention 0=LEFT,1=DOWN,2=RIGHT,3=UP; update_policy(), highlight_cell()
- `ValueHeatmap(VGroup)` — grid cells colored by value (lerp BG_GRID→VALUE_COLOR; neg range toward PENALTY_COLOR); cells + labels dicts; update_values()
- `QValueTable(VGroup)` — 2D table (states×actions) with header row/col, grid lines; update_cell(), highlight_row(), highlight_cell()
- `EpisodeTrail(VGroup)` — grid + animated agent Rectangle; step_to(row,col), step_to_state(state_idx), clear_trail(), reset()

**Deviations from plan:**
- `reactive_bar()` takes a fixed `bottom_center` (numpy array captured in closure) rather than a ref mobject. This is simpler for standalone use; for moveable bars in panels use ActionBarChart. Documented in the function's docstring.
- `_lerp_hex()` internal helper used for color interpolation instead of Manim's `interpolate_color` (avoids uncertain import path).

**Next session should know:**
- Session 3 target: `manim_service/concept_videos/docs/STYLE_BIBLE.md` + rewrite of SKILL.md (`~/.claude/skills/manim-rl-animation-style-lock/SKILL.md`) + `manim_service/scenes/__init__.py` final check
- EpisodeTrail trail dots are added to the VGroup's submobjects and stored in `_trail_dots` list; clear_trail() handles FadeOut + removal cleanly
- ValueHeatmap.update_values() plays two animation phases: (1) cell recolor + old label FadeOut together, (2) new labels LaggedStart FadeIn
- Import smoke test (expanded): `/Users/ultramarine/.venvs/manim/bin/python -W error::SyntaxWarning -c "import sys; sys.path.insert(0, '.'); from manim_service.scenes import equation_morph, token_expand, staggered_write, staggered_fadein, reactive_bar, BackupDiagram, PolicyArrowGrid, ValueHeatmap, QValueTable, EpisodeTrail, BaseConceptScene, ActionBarChart"`
