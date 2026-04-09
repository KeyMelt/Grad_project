import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAME_DIR = ROOT / "frontend" / "assets" / "lesson_media" / "frozenlake"
VIDEO_DIR = ROOT / "frontend" / "assets" / "videos"
TMP_MEDIA_DIR = ROOT / "backend" / "visualization" / "_concept_media"
SCENE_FILE = ROOT / "backend" / "visualization" / "concept_scenes.py"
MANIM_PYTHON = Path("/Users/ultramarine/.venvs/manim/bin/python")

SCENE_EXPORTS = {
    "DPMentalModelScene": "dp_policy_eval_concept.mp4",
    "ValueIterationConcept": "dp_value_iteration_concept.mp4",
    "PolicyImprovementConcept": "dp_policy_improvement_concept.mp4",
    "MonteCarloConcept": "mc_first_visit_concept.mp4",
    "SARSAConcept": "td_sarsa_concept.mp4",
    "QLearningConcept": "td_q_learning_concept.mp4",
}


def render_all() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    TMP_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    _copy_existing_frozenlake_states()

    for scene_name, output_name in SCENE_EXPORTS.items():
        _render_scene(scene_name, output_name)


def _copy_existing_frozenlake_states() -> None:
    capture_root = ROOT / "backend" / "visualization" / "animations" / "captures"
    source_dir = next(
        (path for path in (capture_root / "dp_policy_eval").iterdir() if path.is_dir()),
        None,
    )
    if source_dir is None:
        raise FileNotFoundError(
            "No existing FrozenLake frame captures were found under backend/visualization/animations/captures/dp_policy_eval."
        )

    for index in range(16):
        source = source_dir / f"policy_eval_{index + 1:03d}.png"
        target = FRAME_DIR / f"state_{index:02d}.png"
        if not source.exists():
            raise FileNotFoundError(f"Missing FrozenLake frame capture: {source}")
        shutil.copyfile(source, target)


def _render_scene(scene_name: str, output_name: str) -> None:
    cmd = [
        str(MANIM_PYTHON),
        "-m",
        "manim",
        "-ql",
        "--media_dir",
        str(TMP_MEDIA_DIR),
        str(SCENE_FILE),
        scene_name,
    ]
    subprocess.run(cmd, check=True)

    rendered = (
        TMP_MEDIA_DIR
        / "videos"
        / "concept_scenes"
        / "480p15"
        / f"{scene_name}.mp4"
    )
    if not rendered.exists():
        raise FileNotFoundError(f"Expected render output not found: {rendered}")

    shutil.copyfile(rendered, VIDEO_DIR / output_name)


if __name__ == "__main__":
    render_all()
