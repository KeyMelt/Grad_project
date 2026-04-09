from backend.visualization.controller import VisualizationController


class VisualizationService:
    """Service boundary for trace-to-animation rendering."""

    def __init__(self, output_dir: str = "backend/visualization/animations"):
        self._controller = VisualizationController(output_dir=output_dir)

    def generate_animation(self, log_data: list, lesson_id: str) -> str:
        return self._controller.generate_animation(log_data, lesson_id)
