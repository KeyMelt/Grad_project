from backend.api_gateway.routes.admin import build_admin_router
from backend.api_gateway.routes.auth import build_auth_router
from backend.api_gateway.routes.evaluation import build_evaluation_router
from backend.api_gateway.routes.concept_videos import build_concept_videos_router
from backend.api_gateway.routes.execution import build_execution_router
from backend.api_gateway.routes.lessons import build_lessons_router
from backend.api_gateway.routes.quiz import build_quiz_router
from backend.api_gateway.routes.study_buddy import build_study_buddy_router
from backend.api_gateway.routes.telemetry import build_telemetry_router
from backend.api_gateway.routes.visualization import build_visualization_router
from backend.api_gateway.routes.workspace import build_workspace_router

__all__ = [
    "build_admin_router",
    "build_auth_router",
    "build_evaluation_router",
    "build_concept_videos_router",
    "build_execution_router",
    "build_lessons_router",
    "build_quiz_router",
    "build_study_buddy_router",
    "build_telemetry_router",
    "build_visualization_router",
    "build_workspace_router",
]
