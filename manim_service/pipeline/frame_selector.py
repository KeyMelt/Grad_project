"""Frame selector — deterministic timestamps for visual QA.

Both Manim Expert (self-QA Phase 0) and QA Agent (Gate 5 spot-check) call
the same `strategic_frames()` function. This guarantees they look at the
same frames; no disagreement on what was inspected.

Strategy (per STYLE_BIBLE §34/§35 + cognitive-load §27):
    - Segment boundaries (last frame of each segment): catch stale visuals
    - §34 code-walkthrough mid-frames: verify two-panel + IDE layout
    - §35 equation-dissection mid-frames: verify single-token PRIMARY
    - Cognitive-load high phases (≥3 mobjects per choreo §6): overlap risk
    - Final hold: visual stability
    - Random sampling (deterministic seed): catch unmarked regressions

V-02 with 26 phases / 8 segments yields ~14-16 frames.

Usage:
    from manim_service.pipeline.frame_selector import strategic_frames

    frames = strategic_frames(
        lesson_id="policies_values_bellman",
        phase_timestamps_path="...phase_timestamps.json",
        choreo_path="..._choreo.md",
        plan_path="..._plan.md",
    )
    # frames is a list[dict]: {timestamp, kind, phase_name, rationale}
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class FrameSpec:
    timestamp: float
    kind: str             # boundary | code_walk | eq_diss | cog_high | final | random
    phase_idx: int        # 1-indexed phase number
    phase_name: str
    rationale: str        # one line for the agent to log alongside its observation


# ---------------------------------------------------------------------------
# Heuristics for phase classification
# ---------------------------------------------------------------------------

_CODE_PATTERNS = [
    # Any phase whose name mentions "code" is treated as a §34 code-walkthrough.
    # Underscores are word characters in re, so \bcode\b fails on "P21_code_entry".
    # Use a non-word/start-or-end boundary explicitly.
    r"(?:^|[^a-z])code(?:[^a-z]|$)",
    r"ide(?:[^a-z]|$).*code|code.*ide",
    r"codestepper",
]
_EQ_DISSECTION_PATTERNS = [
    r"derivation",
    r"dissect",
    r"token[_\s]?(by[_\s]?token|highlight)",
    r"bellman[_\s]?step",
    r"step[_\s]?\d+",
    r"recursive[_\s]?value",
    r"recursion[_\s]?in[_\s]?expectation",
    r"action[_\s]?sum|transition[_\s]?sum|policy[_\s]?sum",
]
_BOXED_REVEAL_PATTERNS = [
    r"boxed",
    r"final[_\s]?hold",
    r"takeaway",
    r"hold[_\s]?frame",
]
_REVEAL_PATTERNS = [
    r"reveal",
    r"entry",
    r"intro",
    r"definition",
]


def _matches_any(name: str, patterns: list[str]) -> bool:
    nm = name.lower()
    return any(re.search(p, nm) for p in patterns)


# ---------------------------------------------------------------------------
# Choreo cognitive-load extraction
# ---------------------------------------------------------------------------

def _high_cognitive_load_phases(choreo_text: str) -> set[str]:
    """Return phase names flagged as 'high cognitive load' in choreo §6.

    The choreo template (STYLE_BIBLE-aligned) usually marks these explicitly
    with a row like `| S5-P17 | 4 mobjects | high |`. We grep for that.

    This is heuristic; a phase not marked here can still be sampled by the
    random selector below.
    """
    flagged = set()
    # Pattern: phase tag at start of row, "high" or "≥4" or "4 mobjects" somewhere
    for line in choreo_text.splitlines():
        m = re.match(r"\|\s*(S\d+-P\d+\w*)\s*\|", line)
        if not m:
            continue
        if re.search(r"\bhigh\b|\b[4-9]\s*mobjects?\b|≥\s*4|≥4", line, re.IGNORECASE):
            flagged.add(m.group(1))
    return flagged


# ---------------------------------------------------------------------------
# Phase timestamps loader
# ---------------------------------------------------------------------------

def _load_phase_timestamps(path: str | Path) -> tuple[list[dict], float]:
    data = json.loads(Path(path).read_text())
    return data["phases"], data["total_duration_seconds"]


def _phase_end(phases: list[dict], idx: int, total: float) -> float:
    if idx + 1 < len(phases):
        return phases[idx + 1]["start_seconds"]
    return total


# ---------------------------------------------------------------------------
# Main selector
# ---------------------------------------------------------------------------

def strategic_frames(
    *,
    lesson_id: str,
    phase_timestamps_path: str | Path,
    choreo_path: str | Path | None = None,
    plan_path: str | Path | None = None,
    n_random: int = 2,
) -> list[FrameSpec]:
    """Return the strategic frame list for this lesson.

    Deterministic given the inputs — seeded RNG for the random samples.
    """
    phases, total = _load_phase_timestamps(phase_timestamps_path)
    choreo_text = ""
    if choreo_path and Path(choreo_path).exists():
        choreo_text = Path(choreo_path).read_text(errors="replace")
    high_load_names = _high_cognitive_load_phases(choreo_text)

    out: list[FrameSpec] = []
    seen_ts: set[float] = set()

    def _emit(ts: float, kind: str, idx: int, name: str, rationale: str) -> None:
        # Quantise to 1 decimal to dedupe near-identical timestamps.
        q = round(ts, 1)
        if q in seen_ts or q < 0 or q > total:
            return
        seen_ts.add(q)
        out.append(FrameSpec(timestamp=q, kind=kind, phase_idx=idx + 1,
                             phase_name=name, rationale=rationale))

    # 1. Segment boundaries — last frame of each segment (next_start − 0.2)
    last_segment: str | None = None
    for i, p in enumerate(phases):
        seg = p["name"].split("-")[0] if "-" in p["name"] else p["name"][:3]
        if last_segment is None:
            last_segment = seg
            continue
        if seg != last_segment:
            # The phase BEFORE this transition is segment-end of last_segment.
            prev = i - 1
            prev_end = _phase_end(phases, prev, total)
            _emit(prev_end - 0.2, "boundary", prev, phases[prev]["name"],
                  f"end of segment {last_segment}; stale-visual check")
            last_segment = seg

    # 2. §34 code-walkthrough mid-frames
    for i, p in enumerate(phases):
        if _matches_any(p["name"], _CODE_PATTERNS):
            ts = p["start_seconds"] + 1.0
            _emit(ts, "code_walk", i, p["name"],
                  "§34: two-panel layout + IDE syntax + active-line highlight")

    # 3. §35 equation-dissection mid-frames
    for i, p in enumerate(phases):
        if _matches_any(p["name"], _EQ_DISSECTION_PATTERNS):
            ts = p["start_seconds"] + (_phase_end(phases, i, total) - p["start_seconds"]) / 2
            _emit(ts, "eq_diss", i, p["name"],
                  "§35: single token at PRIMARY; cross_highlight with env partner")

    # 4. Boxed reveals / takeaway / final hold
    for i, p in enumerate(phases):
        if _matches_any(p["name"], _BOXED_REVEAL_PATTERNS):
            ts = p["start_seconds"] + 1.0
            _emit(ts, "boxed", i, p["name"],
                  "boxed equation fully inside frame; no duplicate; no stroke-fill artifact")

    # 5. Cognitive-load high phases (explicitly flagged in choreo)
    for i, p in enumerate(phases):
        if p["name"] in high_load_names:
            ts = p["start_seconds"] + (_phase_end(phases, i, total) - p["start_seconds"]) / 2
            _emit(ts, "cog_high", i, p["name"],
                  "choreo cognitive-load HIGH: overlap risk")

    # 6. Final hold
    last_idx = len(phases) - 1
    _emit(total - 2.5, "final", last_idx, phases[last_idx]["name"],
          "final hold: visual stability; no flicker; correct takeaway")

    # 7. Reveal/entry phases — confirm the named element appears at start+1
    for i, p in enumerate(phases):
        if _matches_any(p["name"], _REVEAL_PATTERNS) and not _matches_any(p["name"], _CODE_PATTERNS):
            ts = p["start_seconds"] + 1.0
            _emit(ts, "reveal", i, p["name"],
                  "RC-5 check: named element must be PRIMARY at start + 1.0 s")

    # 8. Deterministic random samples from phases we haven't covered
    covered_idxs = {fs.phase_idx - 1 for fs in out}
    uncovered = [i for i in range(len(phases)) if i not in covered_idxs]
    if uncovered and n_random > 0:
        # Seeded RNG keyed on lesson_id for reproducibility
        seed = int(hashlib.sha1(lesson_id.encode()).hexdigest()[:8], 16)
        import random
        rng = random.Random(seed)
        picks = rng.sample(uncovered, min(n_random, len(uncovered)))
        for i in picks:
            p = phases[i]
            ts = p["start_seconds"] + (_phase_end(phases, i, total) - p["start_seconds"]) / 2
            _emit(ts, "random", i, p["name"],
                  "uniform sample: catch unmarked regressions")

    # Sort by timestamp for ffmpeg efficiency (sequential reads).
    out.sort(key=lambda fs: fs.timestamp)
    return out


# ---------------------------------------------------------------------------
# Spot-check selector for QA Gate 5 (verifier mode)
# ---------------------------------------------------------------------------

def spot_check_subset(
    strategic: list[FrameSpec],
    *,
    lesson_id: str,
    n: int = 5,
) -> list[FrameSpec]:
    """QA Gate 5 calls this after reading the Manim Expert's self_qa_report.

    Picks `n` frames deterministically (seeded on lesson_id + 'qa') so the
    QA pass is reproducible but unpredictable to the Manim Expert at the
    time of self-QA.
    """
    seed = int(hashlib.sha1(f"{lesson_id}|qa".encode()).hexdigest()[:8], 16)
    import random
    rng = random.Random(seed)
    if n >= len(strategic):
        return list(strategic)
    return sorted(rng.sample(strategic, n), key=lambda fs: fs.timestamp)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser(description="Compute strategic frames for a lesson.")
    parser.add_argument("--lesson-id", required=True)
    parser.add_argument("--phase-timestamps", required=True)
    parser.add_argument("--choreo", default=None)
    parser.add_argument("--plan", default=None)
    parser.add_argument("--random", type=int, default=2)
    parser.add_argument("--spot-check", type=int, default=0,
                        help="If >0, return the QA-mode spot-check subset of this size.")
    args = parser.parse_args()

    frames = strategic_frames(
        lesson_id=args.lesson_id,
        phase_timestamps_path=args.phase_timestamps,
        choreo_path=args.choreo,
        plan_path=args.plan,
        n_random=args.random,
    )
    if args.spot_check > 0:
        frames = spot_check_subset(frames, lesson_id=args.lesson_id, n=args.spot_check)
    print(json.dumps([asdict(f) for f in frames], indent=2))
