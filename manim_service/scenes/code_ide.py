"""IDECodePanel — STYLE_BIBLE §34 conformant code panel.

Renders Python source as if displayed in an IDE: monospaced font,
syntax highlighting by token category, line numbers in a gutter, and
a debugger-style active-line highlight rectangle.

Replaces / complements `CodeStepper` from `panels.py`. Use this whenever
STYLE_BIBLE §34 applies (any phase whose plan.md description includes
code execution / code panel).

Usage:
    code = IDECodePanel([
        "env = gym.make('FrozenLake-v1', is_slippery=True)",
        "n_states = env.observation_space.n",
        "for prob, ns, r, done in env.unwrapped.P[s][a]:",
        "    v_new += pi[s, a] * prob * (r + gamma * v_prev[ns])",
    ], width=6.4)
    self.add(code)
    self.play(*code.step(self, 0))   # highlight line 0
    self.play(*code.step(self, 1))
    self.play(*code.reset(self))

Color map (uses STYLE_BIBLE 10-color palette only — no custom hex):
    keyword  -> POLICY_COLOR  (#A78BFA)
    builtin  -> ACTION_COLOR  (#FB923C)
    string   -> REWARD_COLOR  (#34D399)
    number   -> VALUE_COLOR   (#FACC15)
    comment  -> CODE_ACCENT   (#64748B) dimmed
    default  -> WHITE
    gutter   -> CODE_ACCENT   (#64748B) at OPACITY_BACKGROUND
    active   -> VALUE_COLOR   stroke on a BG_PANEL rectangle
"""
from __future__ import annotations

import re
from typing import Iterable

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    BLACK,
    Create,
    FadeOut,
    Rectangle,
    Scene,
    Text,
    VGroup,
    VectorizedPoint,
    WHITE,
)

from manim_service.scenes.panels import (
    ACTION_COLOR,
    BG_PANEL,
    CODE_ACCENT,
    OPACITY_BACKGROUND,
    OPACITY_PRIMARY,
    OPACITY_SECONDARY,
    POLICY_COLOR,
    REWARD_COLOR,
    VALUE_COLOR,
)

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

PYTHON_KEYWORDS = frozenset({
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
})

PYTHON_BUILTINS = frozenset({
    "abs", "all", "any", "bool", "bytes", "callable", "chr", "complex",
    "dict", "dir", "divmod", "enumerate", "eval", "filter", "float",
    "format", "frozenset", "getattr", "hasattr", "hash", "hex", "id",
    "input", "int", "isinstance", "issubclass", "iter", "len", "list",
    "map", "max", "min", "next", "object", "oct", "open", "ord", "pow",
    "print", "property", "range", "repr", "reversed", "round", "set",
    "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super",
    "tuple", "type", "vars", "zip",
    # Common library aliases that appear in our code samples:
    "np", "gym", "torch",
})

# Token kinds: comment, string, number, keyword, builtin, default
_TOKEN_RE = re.compile(
    r"""
    (?P<comment>\#[^\n]*)
    | (?P<string>'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")
    | (?P<fstring>f'(?:[^'\\]|\\.)*'|f"(?:[^"\\]|\\.)*")
    | (?P<number>\b\d+(?:\.\d+)?\b)
    | (?P<ident>[A-Za-z_][A-Za-z_0-9]*)
    | (?P<ws>\s+)
    | (?P<op>[^\w\s])
    """,
    re.VERBOSE,
)


def _classify(ident: str) -> str:
    if ident in PYTHON_KEYWORDS:
        return "keyword"
    if ident in PYTHON_BUILTINS:
        return "builtin"
    return "default"


def tokenize_python(line: str) -> list[tuple[str, str]]:
    """Return a list of (text, kind) tuples for one source line."""
    out: list[tuple[str, str]] = []
    pos = 0
    for m in _TOKEN_RE.finditer(line):
        if m.start() != pos:
            out.append((line[pos:m.start()], "default"))
        kind = m.lastgroup or "default"
        text = m.group()
        if kind == "ident":
            kind = _classify(text)
        elif kind in ("string", "fstring"):
            kind = "string"
        elif kind in ("ws", "op"):
            kind = "default"
        out.append((text, kind))
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], "default"))
    return out


_KIND_COLOR = {
    "keyword": POLICY_COLOR,
    "builtin": ACTION_COLOR,
    "string":  REWARD_COLOR,
    "number":  VALUE_COLOR,
    "comment": CODE_ACCENT,
    "default": WHITE,
}

# Monospaced font fallback chain (first available wins; Menlo ships on macOS,
# DejaVu Sans Mono on Linux, Consolas on Windows).
_MONOSPACE_FONTS = ("Menlo", "Consolas", "DejaVu Sans Mono", "Courier New", "Courier")


def _pick_mono_font() -> str:
    """Return a monospaced font name; manim's Text falls back silently if
    the named font isn't installed, but we still send our preferred order."""
    return _MONOSPACE_FONTS[0]


# ---------------------------------------------------------------------------
# IDECodePanel
# ---------------------------------------------------------------------------

class IDECodePanel(VGroup):
    """STYLE_BIBLE §34-conformant IDE-style code panel.

    Layout:
        [bg rectangle]
        [line gutter (numbers) | code text]
        [debugger-highlight rect overlays the active line]

    Public API:
        .lines           — list of VGroups, one per source line (for
                           cross_highlight_pair).
        .step(scene, i)  — returns a list of animations: move the
                           debugger highlight to line i, dim previously
                           active line, brighten line i.
        .reset(scene)    — return all lines to PRIMARY, remove highlight.
    """

    def __init__(
        self,
        lines: Iterable[str],
        *,
        width: float = 6.4,
        font_size: float = 22,
        line_spacing: float = 0.32,
        padding: float = 0.32,
        show_gutter: bool = True,
        title: str | None = None,
    ) -> None:
        super().__init__()
        self._line_strings = list(lines)
        self._font = _pick_mono_font()
        self._font_size = font_size
        self._line_spacing = line_spacing
        self._padding = padding
        self._active_idx: int | None = None
        self._highlight_rect: Rectangle | None = None

        # Build line mobjects.
        line_mobjects: list[VGroup] = []
        for src in self._line_strings:
            line_mob = self._build_line(src)
            line_mobjects.append(line_mob)

        # Determine row count + total height.
        n = len(line_mobjects)
        total_h = padding * 2 + n * line_spacing
        # Background panel.
        self._bg = Rectangle(
            width=width,
            height=max(total_h, line_spacing + padding * 2),
            fill_color=BG_PANEL,
            fill_opacity=1.0,
            stroke_color=CODE_ACCENT,
            stroke_width=1.0,
        )
        self.add(self._bg)

        # Gutter (line numbers).
        self._gutter_width = 0.55 if show_gutter else 0.0
        self._gutter_mobjects: list[Text] = []
        if show_gutter:
            for i in range(n):
                num = Text(
                    f"{i + 1:>2d}",
                    font=self._font,
                    font_size=max(font_size - 4, 16),
                    color=CODE_ACCENT,
                )
                num.set_opacity(OPACITY_BACKGROUND + 0.3)  # ≈0.47, readable but quiet
                self._gutter_mobjects.append(num)

        # Position each line mobject inside the panel.
        bg_top    = self._bg.get_top()[1]
        bg_left_x = self._bg.get_left()[0]
        top_y     = bg_top - padding
        code_x    = bg_left_x + padding + self._gutter_width + 0.15
        gutter_x  = bg_left_x + padding + self._gutter_width * 0.5

        self._line_mobs: list[VGroup] = []
        for i, line_mob in enumerate(line_mobjects):
            y = top_y - (i + 0.5) * line_spacing
            # Move to row centre, then shift so the line's LEFT edge sits at code_x.
            line_mob.move_to([code_x, y, 0])
            current_left = line_mob.get_left()[0]
            line_mob.shift(RIGHT * (code_x - current_left))
            self.add(line_mob)
            self._line_mobs.append(line_mob)
            if show_gutter:
                num = self._gutter_mobjects[i]
                num.move_to([gutter_x, y, 0])
                self.add(num)

        # Optional title bar.
        if title:
            title_mob = Text(title, font=self._font, font_size=font_size - 2,
                             color=CODE_ACCENT)
            title_mob.next_to(self._bg, UP, buff=0.12).align_to(self._bg, LEFT)
            self.add(title_mob)
            self._title = title_mob
        else:
            self._title = None

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_line(self, src: str) -> VGroup:
        """Tokenize one source line and build a VGroup of colored Text tokens.

        Strategy: estimate a monospace character width from a single 'M', then
        place each non-whitespace token at the x-position implied by its
        character offset in the original source line. This sidesteps manim
        Text's variable bounding boxes and respects indentation exactly.
        """
        # Monospace ADVANCE (cell) width — NOT the inked bbox of one glyph.
        # A single glyph's bounding box is narrower than its cell by the side
        # bearings; using it under-counts every column and compresses the line
        # until adjacent letters collide. Measure the true per-character advance
        # from a run of glyphs ("M"*11 minus "M" = 10 advances).
        sizer = Text("M", font=self._font, font_size=self._font_size)
        ref = Text("M" * 11, font=self._font, font_size=self._font_size)
        char_w = (ref.width - sizer.width) / 10  # true monospace cell width
        ascender = sizer.height  # used for y centring

        token_mobs: list[Text] = []
        char_idx = 0
        for text, kind in tokenize_python(src):
            if text == "":
                continue
            if text.strip() == "":
                # Pure whitespace token — advance the cursor only.
                char_idx += len(text)
                continue
            color = _KIND_COLOR.get(kind, WHITE)
            mob = Text(text, font=self._font, font_size=self._font_size, color=color)
            if kind == "comment":
                mob.set_opacity(OPACITY_SECONDARY)
            # Position: the LEFT edge of the token at char_idx * char_w from origin.
            # We'll place around origin; the parent will move the whole line.
            target_x = char_idx * char_w + mob.width / 2
            mob.move_to([target_x, 0, 0])
            token_mobs.append(mob)
            char_idx += len(text)
        # Anchor at column 0 so the VGroup's left edge represents the start
        # of the line (preserving indentation). VectorizedPoint renders nothing
        # but counts toward bounding box.
        anchor = VectorizedPoint([0, 0, 0])
        if not token_mobs:
            return VGroup(anchor)
        return VGroup(anchor, *token_mobs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def lines(self) -> list[VGroup]:
        """Read-only view of per-line VGroups, for cross_highlight_pair."""
        return self._line_mobs

    @property
    def panel(self) -> Rectangle:
        """The background rectangle (for size queries / anchoring)."""
        return self._bg

    def step(self, scene: Scene, line_idx: int) -> list:
        """Return animations: move the debugger highlight to line_idx.

        Implementation: dim previously active line to OPACITY_SECONDARY,
        ensure target line is OPACITY_PRIMARY, animate the highlight
        Rectangle (one shared object) into position behind the target.
        """
        if not (0 <= line_idx < len(self._line_mobs)):
            raise IndexError(f"line_idx {line_idx} out of range")
        anims: list = []
        target = self._line_mobs[line_idx]

        # Dim every line that isn't this one; brighten this one.
        for i, line_mob in enumerate(self._line_mobs):
            if i == line_idx:
                anims.append(line_mob.animate.set_opacity(OPACITY_PRIMARY))
            else:
                anims.append(line_mob.animate.set_opacity(OPACITY_SECONDARY))

        # Debugger highlight rectangle — one shared instance that slides.
        target_width = self._bg.width - self._gutter_width - 0.2
        target_height = self._line_spacing
        target_pos = [
            self._bg.get_left()[0] + self._gutter_width + target_width / 2,
            target.get_center()[1],
            0,
        ]
        if self._highlight_rect is None:
            rect = Rectangle(
                width=target_width,
                height=target_height,
                fill_color=BG_PANEL,
                fill_opacity=0.0,
                stroke_color=VALUE_COLOR,
                stroke_width=1.6,
            )
            rect.move_to(target_pos)
            self._highlight_rect = rect
            anims.append(Create(rect))
            # Ensure highlight sits behind the code text.
            scene.add(rect)
            rect.z_index = self._bg.z_index + 1
        else:
            anims.append(self._highlight_rect.animate.move_to(target_pos))

        self._active_idx = line_idx
        return anims

    def reset(self, scene: Scene) -> list:
        """Restore all lines to PRIMARY and remove the highlight rectangle."""
        anims: list = []
        if self._highlight_rect is not None:
            anims.append(FadeOut(self._highlight_rect))
            self._highlight_rect = None
        for line_mob in self._line_mobs:
            anims.append(line_mob.animate.set_opacity(OPACITY_PRIMARY))
        self._active_idx = None
        return anims

    def get_active_line(self) -> VGroup | None:
        """Return the currently-highlighted line VGroup, or None."""
        if self._active_idx is None:
            return None
        return self._line_mobs[self._active_idx]
