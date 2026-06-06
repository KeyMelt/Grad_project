"""Tokenised equations with in-place sub-part morphing (STYLE_BIBLE §39).

Build an equation from *named* tokens, then expand ONE token — typically a
summation sign and its operand — into its explicit terms while the rest of the
equation stays put and reflows around it. This is the mechanism behind the
"expand only the sum you're talking about" teaching move: the learner watches a
single Σ unfold into the concrete terms it stands for, then fold back.

    eq = TexEquation([
        ("v",   "v(s)"),
        ("eq",  "="),
        ("sum", "\\sum_a \\pi(a\\mid s)\\,q(s,a)"),
    ], font_size=44)
    self.add(eq.mob)
    # expand ONLY the action sum, in place:
    eq2 = eq.expand(self, "sum", [
        ("t0", "\\tfrac14 q(s,\\mathrm{L})"), ("p0", "+"),
        ("t1", "\\tfrac14 q(s,\\mathrm{D})"), ("p1", "+"),
        ("t2", "\\tfrac14 q(s,\\mathrm{R})"), ("p2", "+"),
        ("t3", "\\tfrac14 q(s,\\mathrm{U})"),
    ])
    # ... and collapse back:
    eq2.collapse(self, ("sum", "\\sum_a \\pi(a\\mid s)\\,q(s,a)"),
                 replacing=["t0","p0","t1","p1","t2","p2","t3"])
"""
from __future__ import annotations

from manim import MathTex, TransformMatchingTex, WHITE


class TexEquation:
    """A MathTex whose parts are addressable by name and morphable individually."""

    def __init__(self, tokens, *, font_size: float = 48, color=WHITE,
                 max_width: float | None = None):
        # tokens: list of (name, tex)
        self.tokens = list(tokens)
        self.font_size = font_size
        self.color = color
        self.max_width = max_width
        self.mob = MathTex(*[t for _, t in self.tokens], font_size=font_size, color=color)
        if max_width and self.mob.width > max_width:
            self.mob.scale_to_fit_width(max_width)
        self._index = {n: i for i, (n, _) in enumerate(self.tokens)}

    def __getitem__(self, name: str):
        return self.mob[self._index[name]]

    def names(self):
        return [n for n, _ in self.tokens]

    def _rebuilt(self, new_tokens, color=None):
        new = TexEquation(new_tokens, font_size=self.font_size,
                          color=color or self.color, max_width=self.max_width)
        new.mob.move_to(self.mob)  # keep centred where the original sat
        return new

    def with_expanded(self, name: str, sub_tokens, color=None) -> "TexEquation":
        """Return a new TexEquation with token `name` replaced by `sub_tokens`."""
        out = []
        for n, t in self.tokens:
            out.extend(sub_tokens if n == name else [(n, t)])
        return self._rebuilt(out, color=color)

    def expand(self, scene, name: str, sub_tokens, *, run_time: float = 1.4,
               color=None) -> "TexEquation":
        """Morph token `name` into `sub_tokens` IN PLACE; rest of the eq holds."""
        new = self.with_expanded(name, sub_tokens, color=color)
        scene.play(TransformMatchingTex(self.mob, new.mob), run_time=run_time)
        return new

    def collapse(self, scene, folded_token, *, replacing, run_time: float = 1.2):
        """Inverse of expand: fold the `replacing` token names back into one
        token. `folded_token` is a single (name, tex)."""
        out = []
        done = False
        repl = set(replacing)
        for n, t in self.tokens:
            if n in repl:
                if not done:
                    out.append(folded_token)
                    done = True
            else:
                out.append((n, t))
        new = self._rebuilt(out)
        scene.play(TransformMatchingTex(self.mob, new.mob), run_time=run_time)
        return new
