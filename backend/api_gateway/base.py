import threading

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Subsystems
from backend.execution_runtime import ExecutionPipelineError, run_submission_with_timeout
from backend.lessons import LESSON_DEFINITIONS, get_lesson_definition
from backend.job_store import ExecutionJobStore

app = FastAPI(title="RL IDE Backend Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_store = ExecutionJobStore()

class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: float = Field(gt=0, le=1)
    discount_factor: float = Field(gt=0, le=1)
    exploration_rate: float = Field(ge=0, le=1)
    episode_count: int = Field(default=5, ge=1, le=500)


@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.get("/lessons")
def get_lessons():
    return {
        "lessons": [
            {"id": lesson.id, "title": lesson.title}
            for lesson in LESSON_DEFINITIONS.values()
        ]
    }

def _execute_async_job(task_id: str, submission: CodeSubmission) -> None:
    job_store.mark_running(task_id)
    try:
        result = run_submission_with_timeout(submission.model_dump())
        job_store.mark_succeeded(task_id, result)
    except ExecutionPipelineError as error:
        job_store.mark_failed(task_id, error.detail)
    except Exception as error:
        job_store.mark_failed(
            task_id,
            {
                "message": "Unhandled execution failure.",
                "issues": [str(error)],
            },
        )


@app.post("/submit")
def submit_code(submission: CodeSubmission):
    job = job_store.create()
    thread = threading.Thread(
        target=_execute_async_job,
        args=(job.task_id, submission),
        daemon=True,
    )
    thread.start()
    return {
        "task_id": job.task_id,
        "status": job.status,
    }


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    snapshot = job_store.snapshot(task_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"Unknown task_id '{task_id}'.")
    return snapshot


@app.post("/execute")
def execute_code(submission: CodeSubmission):
    try:
        return run_submission_with_timeout(submission.model_dump())
    except ExecutionPipelineError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
