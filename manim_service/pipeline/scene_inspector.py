"""Static scene inspector — Tier-1 pre-render lint (zero render, zero vision).

Parses a concept-video scene ``.py`` with the ``ast`` module and flags the
defect *sources* documented in the V-01/V-02 QA dossier, before a single
frame is rendered:

    RC5-WAIT   : a ``self.wait(...)`` runs before the first animation of a
                 phase — the reveal's first element is scheduled after a pause
                 (the RC-5 "animation after a wait" smell).
    SLOW-ENTER : the first reveal animation of a phase uses run_time >= 1.0,
                 so the focal element is still dim ~1 s into the phase
                 (the dim-entry residual on P02/P08/P21).

Scope note: ghost-rectangle / orphan-mobject detection is deliberately NOT
done here. Mobject lifecycle is too dynamic for precise static tracking
(container ``.add()``, ``self.``-attribute aliasing, keep-lists), and the real
P26 ghost rect came from opacity manipulation during a morph, not a missing
fade — so it is caught empirically by the Tier-2 pixel scanner instead. Every
rule below is high-precision: what it reports is a true positive.

This is *advisory*: findings are warnings the script writer / Manim expert
should resolve, not a hard render block (some are intentional). Exit code is
1 when findings exist so an orchestrator can surface them, 0 when clean.

    python -m manim_service.pipeline.scene_inspector <scene.py> [<scene.py> ...]
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

SLOW_REVEAL_RUNTIME = 1.0
_REVEAL_ANIMS = {"FadeIn", "Write", "Create", "GrowFromCenter", "DrawBorderThenFill"}


def _call_name(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _runtime_of(call: ast.Call) -> float | None:
    for kw in call.keywords:
        if kw.arg == "run_time" and isinstance(kw.value, ast.Constant):
            try:
                return float(kw.value.value)
            except (TypeError, ValueError):
                return None
    return None


def inspect_file(path: Path) -> list[dict]:
    """Return a list of finding dicts for one scene file."""
    src = path.read_text()
    tree = ast.parse(src, filename=str(path))
    findings: list[dict] = []

    # Per-phase checks.
    for fn in ast.walk(tree):
        if not (isinstance(fn, ast.FunctionDef) and fn.name.startswith("_phase")):
            continue
        plays, waits = [], []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                cn = _call_name(node)
                if cn == "play":
                    plays.append(node)
                elif cn == "wait":
                    waits.append(node)
        if not plays:
            continue
        first_play_line = min(p.lineno for p in plays)

        # RC5-WAIT: a wait before the first play.
        for w in waits:
            if w.lineno < first_play_line:
                findings.append({
                    "rule": "RC5-WAIT", "line": w.lineno,
                    "detail": f"{fn.name}: self.wait() before first animation",
                })
                break

        # SLOW-ENTER: first play is a slow *cold* reveal.
        # A crossfade (the play also contains a FadeOut) keeps outgoing content
        # on screen during the entrance, so it is NOT a dim-entry — skip it to
        # avoid flagging intentional transitions.
        first_play = min(plays, key=lambda p: p.lineno)
        rt = _runtime_of(first_play)
        # > (not >=): run_time == 1.0 reaches full opacity exactly at t=1.0s,
        # so it is not dim "one second in"; only run_time > 1.0 is.
        if rt is not None and rt > SLOW_REVEAL_RUNTIME:
            arg_calls = [a for a in first_play.args if isinstance(a, ast.Call)]
            has_reveal = any(_call_name(a) in _REVEAL_ANIMS for a in arg_calls)
            is_crossfade = any(_call_name(a) == "FadeOut" for a in arg_calls)
            if has_reveal and not is_crossfade:
                findings.append({
                    "rule": "SLOW-ENTER", "line": first_play.lineno,
                    "detail": f"{fn.name}: first cold reveal run_time={rt} "
                              f"(> {SLOW_REVEAL_RUNTIME}s dim-entry risk)",
                })
    findings.sort(key=lambda f: f["line"])
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Static pre-render lint for concept scenes")
    ap.add_argument("paths", nargs="+", help="scene .py file(s)")
    args = ap.parse_args(argv)

    total = 0
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"SCENE-LINT: MISSING {p}")
            continue
        findings = inspect_file(path)
        print(f"SCENE-LINT {path.name} — {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f['rule']} L{f['line']}: {f['detail']}")
        total += len(findings)
    print(f"TOTAL: {total} advisory finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
