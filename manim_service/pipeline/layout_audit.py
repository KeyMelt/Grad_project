"""Deterministic layout audit — Tier 0 visual QA gate (zero vision tokens).

The pure-geometry logic lives here so it is unit-testable without a live
Manim render. ``BaseConceptScene`` extracts on-screen mobject geometry once
per phase (hooked into ``mark_phase`` / ``tear_down``) and feeds it to
``analyze_phase``, storing the raw geometry too so the logic can be re-run
offline with ``--reanalyze`` (no re-render needed to iterate thresholds).

Two checks, learned from grounding the gate on real renders:

  OFF-CANVAS (HARD)  — a *PRIMARY* (focal) group clipped by the camera frame.
                       Real defect: a full-opacity equation running off the
                       edge. Dim/secondary elements that bleed off the edge
                       (decorative corner thumbnails) are intentional and are
                       reported as advisory `off_canvas_warn`, not a hard fail.

  CROWD (ADVISORY)   — two *major focal blocks* that partially collide, or a
                       near-equal full overlap (double-render). Deliberately
                       NOT a hard fail: bounding-box overlap cannot reliably
                       tell a real collision (equation over a diagram) from
                       intentional composition. So composition is excluded
                       (a framed element inside its box, a small label nested
                       in a node, sub-MAJOR_AREA elements) and what remains is
                       surfaced as a warning for the LLM polish pass to judge.

    python -m manim_service.pipeline.layout_audit <layout_audit.json>
    python -m manim_service.pipeline.layout_audit --reanalyze <layout_audit.json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# --- thresholds -------------------------------------------------------------
PRIMARY_OPACITY = 0.70    # at/above, a leaf is a focal (PRIMARY) element
VISIBLE_OPACITY = 0.05    # below, a leaf is effectively invisible
OFF_CANVAS_TOL = 0.06     # units a group may exceed the frame before it clips
MAJOR_AREA = 1.5          # sq units; below this a group is a sub-element, not a focal block
CROWD_MIN_FRAC = 0.15     # min overlap (of smaller area) to consider at all
CONTAINMENT_FRAC = 0.85   # overlap/min_area at/above this = one (near) contains the other
NEAR_EQUAL_AREA = 0.85    # area ratio at/above this = comparable size (double-render risk)
MAX_PRIMARY = 3           # > this many PRIMARY groups = clutter warning
LOW_CANVAS_USE = 0.40     # min(width,height) span of primary content below this = wasted space
SPREAD_MIN_PRIMARIES = 3  # only flag wasted space on genuinely multi-element phases
FRAME_KINDS = {"SurroundingRectangle", "Rectangle", "RoundedRectangle"}


def _area(b: dict) -> float:
    return max(0.0, b["x_max"] - b["x_min"]) * max(0.0, b["y_max"] - b["y_min"])


def _overlap_area(a: dict, b: dict) -> float:
    dx = min(a["x_max"], b["x_max"]) - max(a["x_min"], b["x_min"])
    dy = min(a["y_max"], b["y_max"]) - max(a["y_min"], b["y_min"])
    if dx <= 0 or dy <= 0:
        return 0.0
    return dx * dy


def _off_canvas_edges(bb: dict, canvas: dict) -> dict:
    over = {
        "left": round(canvas["x_min"] - bb["x_min"], 3),
        "right": round(bb["x_max"] - canvas["x_max"], 3),
        "top": round(bb["y_max"] - canvas["y_max"], 3),
        "bottom": round(canvas["y_min"] - bb["y_min"], 3),
    }
    return {k: v for k, v in over.items() if v > OFF_CANVAS_TOL}


def analyze_phase(phase: int, name: str, groups: list[dict], canvas: dict) -> dict:
    """Pure violation logic for one settled phase.

    Each group dict has: ``id, kind, opacity``, a ``primary_bbox`` (union of
    leaves >= PRIMARY_OPACITY, or ``None`` if the group is all dim) and a
    ``full_bbox`` (union of all visible leaves).
    """
    primaries = [g for g in groups if g.get("primary_bbox")]

    # --- CROWD (advisory): major focal blocks that collide / duplicate ---
    crowd: list[dict] = []
    for i in range(len(primaries)):
        for j in range(i + 1, len(primaries)):
            a, b = primaries[i], primaries[j]
            ba, bb = a["primary_bbox"], b["primary_bbox"]
            aa, ab = _area(ba), _area(bb)
            if min(aa, ab) < MAJOR_AREA:
                continue  # a sub-element (label, node), not a focal block
            ov = _overlap_area(ba, bb)
            if ov <= 0:
                continue
            frac = ov / min(aa, ab)
            if frac < CROWD_MIN_FRAC:
                continue
            if frac >= CONTAINMENT_FRAC:
                larger_kind = a["kind"] if aa >= ab else b["kind"]
                area_ratio = min(aa, ab) / max(aa, ab)
                if larger_kind in FRAME_KINDS:
                    continue  # framed inside a box/panel — composition, not crowd
                if area_ratio < NEAR_EQUAL_AREA:
                    continue  # small element nested in a big one — composition
                severity = "duplicate"   # comparable size, full overlap -> double render
            else:
                severity = "collision"   # genuine partial intrusion
            crowd.append({
                "a": a["id"], "a_kind": a["kind"],
                "b": b["id"], "b_kind": b["kind"],
                "overlap_frac": round(frac, 3), "severity": severity,
            })

    # --- OFF-CANVAS: hard for PRIMARY focal content, advisory for dim bleed ---
    off_canvas: list[dict] = []        # HARD
    off_canvas_warn: list[dict] = []   # advisory (dim / secondary)
    for g in groups:
        is_primary = bool(g.get("primary_bbox"))
        bb = g.get("primary_bbox") if is_primary else g.get("full_bbox")
        if not bb:
            continue
        edges = _off_canvas_edges(bb, canvas)
        if not edges:
            continue
        rec = {"id": g["id"], "kind": g["kind"], "edges": edges}
        (off_canvas if is_primary else off_canvas_warn).append(rec)

    # --- canvas utilization (wasted-space advisory) ---
    # A multi-element phase whose primary content is squeezed into a thin band
    # (leaving large empty margins) wastes the screen and shrinks every artifact
    # — illegible on a small screen. Single focal elements (titles, a centred
    # boxed equation) are exempt: those are *meant* to sit alone.
    space_warn = None
    if len(primaries) >= SPREAD_MIN_PRIMARIES:
        bx = [g["primary_bbox"] for g in primaries]
        used_w = max(b["x_max"] for b in bx) - min(b["x_min"] for b in bx)
        used_h = max(b["y_max"] for b in bx) - min(b["y_min"] for b in bx)
        cw = canvas["x_max"] - canvas["x_min"]
        ch = canvas["y_max"] - canvas["y_min"]
        h_frac = used_w / cw if cw else 0.0
        v_frac = used_h / ch if ch else 0.0
        if min(h_frac, v_frac) < LOW_CANVAS_USE:
            space_warn = (f"under-uses canvas: primary content spans "
                          f"{h_frac:.0%}×{v_frac:.0%} of frame "
                          f"(enlarge / spread to fill — small-screen legibility)")

    warnings: list[str] = []
    if space_warn:
        warnings.append(space_warn)
    if len(primaries) > MAX_PRIMARY:
        warnings.append(f"clutter: {len(primaries)} PRIMARY groups (> {MAX_PRIMARY})")
    for c in crowd:
        warnings.append(
            f"crowd/{c['severity']}: {c['a_kind']}↔{c['b_kind']} ({c['overlap_frac']:.0%})")
    for o in off_canvas_warn:
        warnings.append(f"dim-bleed: {o['kind']} off-edge (intentional?)")

    return {
        "phase": phase,
        "name": name,
        "primary_count": len(primaries),
        "off_canvas": off_canvas,            # HARD
        "off_canvas_warn": off_canvas_warn,  # advisory
        "crowd": crowd,                      # advisory
        "warnings": warnings,
        "hard_fail": bool(off_canvas),
    }


# --- CLI / summariser -------------------------------------------------------

def _print_phase_failures(p: dict) -> None:
    for oc in p["off_canvas"]:
        edges = ", ".join(f"{k}+{v}" for k, v in oc["edges"].items())
        print(f"  FAIL P{p['phase']} {p['name']}: OFF-CANVAS {oc['kind']} [{edges}]")


def summarize(audit_path: str) -> int:
    path = Path(audit_path)
    if not path.exists():
        print(f"LAYOUT-AUDIT: MISSING {audit_path}")
        return 2
    data = json.loads(path.read_text())
    phases = data.get("phases", [])
    fails = [p for p in phases if p.get("hard_fail")]
    warns = [p for p in phases if p.get("warnings") and not p.get("hard_fail")]

    print(f"LAYOUT-AUDIT {data.get('lesson_id', '?')} — {len(phases)} phases")
    for p in fails:
        _print_phase_failures(p)
    for p in warns:
        for w in p["warnings"]:
            print(f"  warn P{p['phase']} {p['name']}: {w}")
    verdict = "FAIL" if fails else "PASS"
    print(f"VERDICT: {verdict}  ({len(fails)} hard, {len(warns)} warn)")
    return 1 if fails else 0


def reanalyze(audit_path: str) -> int:
    """Recompute every phase verdict from stored ``_raw`` geometry, in place.

    Lets the analysis logic / thresholds be iterated without a re-render.
    """
    path = Path(audit_path)
    if not path.exists():
        print(f"LAYOUT-AUDIT: MISSING {audit_path}")
        return 2
    data = json.loads(path.read_text())
    new_phases = []
    missing_raw = 0
    for p in data.get("phases", []):
        raw = p.get("_raw")
        if not raw:
            missing_raw += 1
            new_phases.append(p)
            continue
        rec = analyze_phase(p["phase"], p["name"], raw["groups"], raw["canvas"])
        rec["_raw"] = raw
        new_phases.append(rec)
    data["phases"] = new_phases
    path.write_text(json.dumps(data, indent=2) + "\n")
    if missing_raw:
        print(f"NOTE: {missing_raw} phase(s) had no _raw geometry (re-render to capture)")
    return summarize(audit_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Summarise/reanalyse a layout_audit.json gate file")
    ap.add_argument("audit_path", help="path to {lesson}_layout_audit.json")
    ap.add_argument("--reanalyze", action="store_true",
                    help="recompute verdicts from stored raw geometry, then summarise")
    args = ap.parse_args(argv)
    return reanalyze(args.audit_path) if args.reanalyze else summarize(args.audit_path)


if __name__ == "__main__":
    sys.exit(main())
