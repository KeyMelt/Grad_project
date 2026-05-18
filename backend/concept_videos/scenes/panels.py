"""Re-exports from manim_service.scenes.panels.

The canonical panel implementation lives in manim_service/scenes/panels.py.
This shim allows existing backend scenes to continue importing from the
backend package path until the full migration is done in Session 6.
"""
from manim_service.scenes.panels import *  # noqa: F401, F403
from manim_service.scenes.panels import (
    STATE_COLOR, VALUE_COLOR, REWARD_COLOR, PENALTY_COLOR,
    POLICY_COLOR, ACTION_COLOR, BG_COLOR, BG_PANEL, BG_GRID, CODE_ACCENT,
    ACCENT_BLUE, ACCENT_YELLOW, ACCENT_GREEN, ACCENT_SLATE, BG_DEEP,
    OPACITY_PRIMARY, OPACITY_SECONDARY, OPACITY_BACKGROUND,
    BaseConceptScene,
    note_stack, panel, code_panel, equation_panel, pill,
    frozenlake_frame, environment_panel, card_mobject,
    blackjack_panel, cliffwalking_panel,
    FormulaStepper, StatefulHighlighter,
    HighlightedAnimation, highlighted_animation,
    CodeStepper,
    ActionBarChart, SynchronizedFocusGroup, action_arrows_overlay,
    zoom_to, zoom_reset,
    EnvironmentPanel, env_panel,
)
