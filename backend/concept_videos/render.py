import shutil
import subprocess
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAME_DIR = ROOT / "frontend" / "assets" / "lesson_media" / "frozenlake"
VIDEO_DIR = Path(
    os.getenv("RL_IDE_CONCEPT_VIDEO_DIR", str(ROOT / "backend" / "media" / "concept_videos"))
).expanduser()
TMP_MEDIA_DIR = ROOT / "backend" / "concept_videos" / "_manim_media"
SCENE_DIR = ROOT / "backend" / "concept_videos" / "scenes"
MANIM_PYTHON = Path(os.getenv("RL_IDE_MANIM_PYTHON", "/Users/ultramarine/.venvs/manim/bin/python3"))

SCENE_EXPORTS = (
    {
        "scene_file": SCENE_DIR / "policy_evaluation.py",
        "scene_name": "PolicyEvaluationConcept",
        "output_name": "dp_policy_eval_concept.mp4",
    },
    {
        "scene_file": SCENE_DIR / "value_iteration.py",
        "scene_name": "ValueIterationConcept",
        "output_name": "dp_value_iteration_concept.mp4",
    },
    {
        "scene_file": SCENE_DIR / "policy_improvement.py",
        "scene_name": "PolicyImprovementConcept",
        "output_name": "dp_policy_improvement_concept.mp4",
    },
    {
        "scene_file": SCENE_DIR / "monte_carlo.py",
        "scene_name": "MonteCarloConcept",
        "output_name": "mc_first_visit_concept.mp4",
    },
    {
        "scene_file": SCENE_DIR / "sarsa.py",
        "scene_name": "SARSAConcept",
        "output_name": "td_sarsa_concept.mp4",
    },
    {
        "scene_file": SCENE_DIR / "q_learning.py",
        "scene_name": "QLearningConcept",
        "output_name": "td_q_learning_concept.mp4",
    },
)


def render_all() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    TMP_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    _copy_existing_frozenlake_states()

    for export in SCENE_EXPORTS:
        _render_scene(
            export["scene_file"],
            export["scene_name"],
            export["output_name"],
        )


def _copy_existing_frozenlake_states() -> None:
    capture_root = ROOT / "backend" / "visualization" / "animations" / "captures"
    target_root = capture_root / "dp_policy_eval"
    if not target_root.exists():
        return
    source_dir = next(
        (path for path in target_root.iterdir() if path.is_dir()),
        None,
    )
    if source_dir is None:
        return

    for index in range(16):
        source = source_dir / f"policy_eval_{index + 1:03d}.png"
        target = FRAME_DIR / f"state_{index:02d}.png"
        if not source.exists():
            continue
        shutil.copyfile(source, target)


def _render_scene(scene_file: Path, scene_name: str, output_name: str) -> None:
    cmd = [
        str(MANIM_PYTHON),
        "-m",
        "manim",
        "-ql",
        "--media_dir",
        str(TMP_MEDIA_DIR),
        str(scene_file),
        scene_name,
    ]
    subprocess.run(cmd, check=True)

    rendered = TMP_MEDIA_DIR / "videos" / scene_file.stem / "480p15" / f"{scene_name}.mp4"
    if not rendered.exists():
        raise FileNotFoundError(f"Expected render output not found: {rendered}")

    shutil.copyfile(rendered, VIDEO_DIR / output_name)


if __name__ == "__main__":
    render_all()
