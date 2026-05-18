"""Manim scene helpers for the production pipeline."""
from .motion import (
    equation_morph,
    token_expand,
    staggered_write,
    staggered_fadein,
    reactive_bar,
)
from .rl_visuals import (
    BackupDiagram,
    PolicyArrowGrid,
    ValueHeatmap,
    QValueTable,
    EpisodeTrail,
)
from .panels import (
    # Color constants
    STATE_COLOR,
    VALUE_COLOR,
    REWARD_COLOR,
    PENALTY_COLOR,
    POLICY_COLOR,
    ACTION_COLOR,
    BG_COLOR,
    BG_PANEL,
    BG_GRID,
    CODE_ACCENT,
    # Legacy aliases
    ACCENT_BLUE,
    ACCENT_YELLOW,
    ACCENT_GREEN,
    ACCENT_SLATE,
    BG_DEEP,
    # Opacity constants
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    OPACITY_BACKGROUND,
    # Scene base class
    BaseConceptScene,
    # Panel builders
    note_stack,
    panel,
    code_panel,
    equation_panel,
    pill,
    # Environment panels
    frozenlake_frame,
    environment_panel,
    card_mobject,
    blackjack_panel,
    cliffwalking_panel,
    # Stepper / highlighter classes
    FormulaStepper,
    StatefulHighlighter,
    HighlightedAnimation,
    highlighted_animation,
    CodeStepper,
    # Animated helpers
    ActionBarChart,
    SynchronizedFocusGroup,
    action_arrows_overlay,
    # Camera helpers
    zoom_to,
    zoom_reset,
    # EnvironmentPanel protocol + factory
    EnvironmentPanel,
    env_panel,
)

__all__ = [
    # motion primitives
    "equation_morph", "token_expand",
    "staggered_write", "staggered_fadein",
    "reactive_bar",
    # RL visuals
    "BackupDiagram", "PolicyArrowGrid", "ValueHeatmap", "QValueTable", "EpisodeTrail",
    # Color constants
    "STATE_COLOR", "VALUE_COLOR", "REWARD_COLOR", "PENALTY_COLOR",
    "POLICY_COLOR", "ACTION_COLOR", "BG_COLOR", "BG_PANEL", "BG_GRID",
    "CODE_ACCENT",
    "ACCENT_BLUE", "ACCENT_YELLOW", "ACCENT_GREEN", "ACCENT_SLATE", "BG_DEEP",
    "OPACITY_PRIMARY", "OPACITY_SECONDARY", "OPACITY_BACKGROUND",
    "BaseConceptScene",
    "note_stack", "panel", "code_panel", "equation_panel", "pill",
    "frozenlake_frame", "environment_panel", "card_mobject",
    "blackjack_panel", "cliffwalking_panel",
    "FormulaStepper", "StatefulHighlighter",
    "HighlightedAnimation", "highlighted_animation",
    "CodeStepper",
    "ActionBarChart", "SynchronizedFocusGroup", "action_arrows_overlay",
    "zoom_to", "zoom_reset",
    "EnvironmentPanel", "env_panel",
]
