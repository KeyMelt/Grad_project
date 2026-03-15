# Interactive Reinforcement Learning Platform
## System Overview and Testing Procedures

Prepared from the current repository state at `/Users/ultramarine/Desktop/grad_project` on 2026-03-14.

### 1. Purpose of This Report

This report combines two elements requested for thesis support:

- a high-level but code-backed explanation of how the current codebase works
- a concrete description of the testing procedures that have been executed and can be reproduced from the repository

The report is evidence-based. Every implementation claim below is supported by code found in the repository or by test and smoke-test commands executed during this session.

### 2. Current System Overview

The current implementation is a local software system composed of a Flutter desktop frontend and a FastAPI backend. The frontend allows a learner to select one of three reinforcement learning lessons, edit a Python template for the selected lesson, adjust execution parameters, and trigger a run. The backend accepts the submitted code, validates it against the lesson contract, executes the lesson pipeline, records the episode trace, optionally renders a visualization through Manim, and returns scalar metrics together with lesson sample-test results and a visualization path.

At a high level, the system operates in five stages:

- Flutter starts a single-workbench user interface.
- A central controller stores lesson selection, starter code, editable code, parameters, execution state, and backend results.
- The frontend submits code asynchronously to the FastAPI backend and polls task status.
- The backend validates and executes the lesson in a timed worker process.
- Execution results are sent back to the frontend and displayed in the result region.

### 3. Main Code Structure

- `frontend/lib/main.dart`: frontend application entry point
- `frontend/lib/layout/main_layout.dart`: main workbench layout
- `frontend/lib/core/workbench_state.dart`: central frontend controller and state
- `frontend/lib/core/backend_api.dart`: backend client and JSON serialization
- `backend/api_gateway/base.py`: FastAPI routes and request schema
- `backend/execution_runtime.py`: timed execution pipeline
- `backend/validation/validator.py`: code validation and lesson sample tests
- `backend/rl_engine/engine.py`: lesson execution against the RL environment
- `backend/logger/event_logger.py`: step-level trace capture
- `backend/visualization/controller.py`: trace-to-Manim rendering pipeline

### 4. Representative Implementation Snippets

#### 4.1 Frontend Application Entry

File: `frontend/lib/main.dart`

```dart
void main() {
  runApp(const RLSimulationIDE());
}

class RLSimulationIDE extends StatelessWidget {
  final MainLayout? home;

  const RLSimulationIDE({super.key, this.home});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RL Setup Environment',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: home ?? const MainLayout(),
    );
  }
}
```

This snippet shows that the Flutter application is organized around a single top-level workbench window rather than a multi-route application. The `MainLayout` widget is therefore the primary entry point for interactive use.

#### 4.2 Frontend Controller and Async Run Flow

File: `frontend/lib/core/workbench_state.dart`

```dart
Future<void> run() async {
  if (_code.trim().isEmpty) {
    _resetProgress('Add code before running ${_selectedLesson.title}.');
    notifyListeners();
    return;
  }

  if (_runMode == RunMode.hardware) {
    _runStatus = RunStatus.failed;
    _statusMessage =
        'Hardware mode is not wired yet. Switch to Simulation to call the backend.';
    notifyListeners();
    return;
  }

  _runStatus = RunStatus.running;
  _videoPath = '';
  _testResults = const [];
  _statusMessage = 'Running ${_selectedLesson.title} against the backend...';
  notifyListeners();

  final task = await _api.submitCode(
    lessonId: _selectedLesson.id,
    code: _code,
    learningRate: _learningRate,
    discountFactor: _discountFactor,
    explorationRate: _explorationRate,
    episodeCount: _episodeCount,
  );
  _activeTaskId = task.taskId;
  await _pollUntilComplete(task.taskId);
}
```

This code is the main frontend execution entry. It shows that the frontend does not execute user code locally. Instead, it validates basic UI state, blocks the unimplemented hardware mode, submits a task to the backend, and then follows an asynchronous polling model.

#### 4.3 Frontend JSON Request Construction

File: `frontend/lib/core/backend_api.dart`

```dart
final response = await _client.post(
  Uri.parse('$baseUrl/submit'),
  headers: const {'Content-Type': 'application/json'},
  body: jsonEncode({
    'lesson_id': lessonId,
    'code': code,
    'learning_rate': learningRate,
    'discount_factor': discountFactor,
    'exploration_rate': explorationRate,
    'episode_count': episodeCount,
  }),
);
```

This snippet shows the exact request payload generated by the frontend. The request is lesson-oriented rather than generic. It combines editable source code with scalar reinforcement learning hyperparameters and a bounded episode count.

#### 4.4 Backend Request Schema and Async Submission Route

File: `backend/api_gateway/base.py`

```python
class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: float = Field(gt=0, le=1)
    discount_factor: float = Field(gt=0, le=1)
    exploration_rate: float = Field(ge=0, le=1)
    episode_count: int = Field(default=5, ge=1, le=500)

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
```

This code shows the backend boundary clearly. The `CodeSubmission` model enforces typed request fields, while `/submit` creates a queued execution task rather than processing the request synchronously in the request thread.

#### 4.5 Timed Backend Execution Pipeline

File: `backend/execution_runtime.py`

```python
def run_submission_with_timeout(
    submission_payload: dict[str, Any],
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    ctx = multiprocessing.get_context("spawn")
    queue: multiprocessing.Queue = ctx.Queue()
    process = ctx.Process(
        target=_execution_worker,
        args=(submission_payload, queue),
        daemon=True,
    )
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        raise ExecutionPipelineError(
            status_code=408,
            detail={
                "message": "Execution timed out.",
                "issues": [
                    f"The lesson execution exceeded the {timeout_seconds}-second limit.",
                ],
            },
        )
```

This implementation detail matters because the project is executing learner-submitted Python. The current design therefore isolates execution in a separate process and imposes a hard timeout, which is materially safer than executing the submitted code directly inside the API process.

#### 4.6 Lesson-Aware Validation

File: `backend/validation/validator.py`

```python
function = load_user_function(submitted_code, lesson.required_function)
test_results = run_lesson_tests(lesson_id, function)
failed_results = [
    result for result in test_results if not result["passed"]
]
if failed_results:
    return ValidationResult(
        is_valid=False,
        errors=[
            f"{len(failed_results)} lesson sample test(s) failed.",
        ],
        test_results=test_results,
    )
```

This snippet shows that validation is not limited to checking the function name. The backend loads the submitted function, executes lesson-specific sample tests, and can reject code that is syntactically acceptable but semantically incorrect for the lesson.

### 5. Operational Execution Flow

The current system can be described operationally as follows:

1. The user launches the Flutter application.
2. The user selects one of the available lessons stored in `RLWorkbenchController`.
3. The selected lesson loads a Python starter template into the editor.
4. The user modifies the template and adjusts execution parameters.
5. Pressing Run triggers `RLWorkbenchController.run()`.
6. The controller sends a JSON payload to `POST /submit`.
7. The FastAPI backend validates the payload through `CodeSubmission`.
8. The backend creates an in-memory execution job and starts a worker thread.
9. The worker thread invokes the timed execution pipeline.
10. The execution pipeline validates the submitted function and lesson sample tests.
11. If validation succeeds, the reinforcement learning engine runs the selected lesson.
12. The event logger records state transitions and reward data.
13. The visualization controller writes trace data and generates a Manim scene and MP4 output when rendering succeeds.
14. The backend stores the final response in the job store.
15. The frontend polls the task endpoint until the task finishes.
16. The controller stores metrics, test results, status text, and the video path for display in the result tab.

### 6. Testing Procedures

The repository currently evidences three kinds of practical testing:

- automated backend unit testing
- automated frontend widget testing
- manual backend smoke and API validation testing

The procedures below describe how these tests were executed and what they verified.

#### 6.1 Backend Unit Testing Procedure

Command used:

```bash
python3 -m unittest discover /Users/ultramarine/Desktop/grad_project/backend/tests -v
```

Test files involved:

- `backend/tests/test_validator.py`
- `backend/tests/test_event_logger.py`
- `backend/tests/test_job_store.py`

Procedure:

1. Open a shell in the repository root.
2. Run the unittest discovery command targeting `backend/tests`.
3. Observe the named test cases and final summary.
4. Record whether all tests complete without failure.

Observed result on 2026-03-14:

```text
Ran 8 tests in 0.001s
OK
```

Behaviors verified by these backend tests:

- unknown lesson identifiers are rejected
- missing required lesson functions are rejected
- valid lesson functions are accepted
- forbidden imports are rejected
- episode logs remain separated by episode boundary
- logger clear/reset empties in-memory state
- queued, running, succeeded, and failed job-store states are represented correctly

Representative test code:

```python
def test_rejects_missing_required_function(self):
    result = self.validator.validate_code(
        "def helper():\n    return 1\n",
        "td_q_learning",
    )

    self.assertFalse(result.is_valid)
    self.assertIn("q_learning_update", result.errors[0])
```

This backend testing procedure is suitable for repeatable unit verification during development because it does not require the frontend or a running API server.

#### 6.2 Frontend Widget Testing Procedure

Command used:

```bash
cd /Users/ultramarine/Desktop/grad_project/frontend
flutter test
```

Test file involved:

- `frontend/test/widget_test.dart`

Procedure:

1. Change into the `frontend` directory.
2. Run `flutter test`.
3. Allow the widget tree to be pumped and settled by the test harness.
4. Observe the text assertions reported by the test runner.

Observed result on 2026-03-14:

```text
00:00 +0: App runs against backend client and renders returned metrics
00:01 +1: All tests passed!
```

Representative test code:

```dart
await tester.tap(find.text('Run'));
await tester.pumpAndSettle();

expect(find.text('Complete'), findsWidgets);
expect(find.textContaining('Video ready'), findsWidgets);
expect(find.text('3.0'), findsOneWidget);
expect(find.textContaining('/tmp/mc_first_visit.mp4'), findsOneWidget);
expect(find.text('Lesson Sample Tests'), findsOneWidget);
```

This procedure verifies the frontend state-binding path using a `FakeBackendApi`. It confirms that the controller and widget tree can render a successful run result, but it does not verify live HTTP communication with the FastAPI backend.

#### 6.3 Live Backend Smoke-Test Procedure

Commands used:

```bash
cd /Users/ultramarine/Desktop/grad_project
/Users/ultramarine/.venvs/manim/bin/python -m backend.main
```

In a separate terminal:

```bash
/Users/ultramarine/.venvs/manim/bin/python /Users/ultramarine/Desktop/grad_project/backend/test_execution.py
```

Procedure:

1. Start the FastAPI backend from the repository root.
2. Run the smoke-test script in a second terminal.
3. The script submits a lesson execution request and polls task status until completion.
4. Record the final returned payload.

Observed result on 2026-03-14:

```text
{'task_id': 'c32dc790978b47b2987b00ce153482b8', 'status': 'succeeded', 'result': {'status': 'success', 'message': 'Execution pipeline completed.', 'lesson': {'id': 'td_q_learning', 'title': 'Temporal Difference: Q-Learning'}, 'video_path': '/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/videos/td_q_learning_scene/480p15/RLEpisodeScene.mp4', 'visualization_ready': True, 'test_results': [{'name': 'q_learning_update_rule', 'passed': True, 'message': 'Updates the selected Q-value using the one-step TD target.', 'expected': 'Q[0][1] = 1.75', 'actual': 'Q[0][1] = 1.75'}], 'metrics': {'episodes_completed': 5, 'steps_recorded': 48, 'total_reward': 1, 'average_reward': 0.2, 'best_episode_reward': 1}}}
```

This procedure is significant because it exercises an integrated backend path: request submission, job creation, validation, lesson execution, event logging, visualization generation, and structured response construction.

#### 6.4 Manual API Validation Procedure

The backend was also tested through explicit negative API calls to confirm that error handling is exposed correctly at the HTTP boundary.

##### Unknown lesson check

Command used:

```bash
curl -s -X POST http://127.0.0.1:8000/execute \
  -H 'Content-Type: application/json' \
  -d '{"lesson_id":"unknown_lesson","code":"def helper():\n    return 1\n","learning_rate":0.1,"discount_factor":0.9,"exploration_rate":0.1,"episode_count":5}'
```

Observed response:

```json
{"detail":"Unknown lesson 'unknown_lesson'."}
```

##### Missing required function check

Command used:

```bash
curl -s -X POST http://127.0.0.1:8000/execute \
  -H 'Content-Type: application/json' \
  -d '{"lesson_id":"td_q_learning","code":"def helper():\n    return 1\n","learning_rate":0.1,"discount_factor":0.9,"exploration_rate":0.1,"episode_count":5}'
```

Observed response:

```json
{"detail":{"message":"Code validation failed.","issues":["ValueError: Required function 'q_learning_update' was not defined."],"test_results":[]}}
```

##### Out-of-range payload field check

Command used:

```bash
curl -s -X POST http://127.0.0.1:8000/execute \
  -H 'Content-Type: application/json' \
  -d '{"lesson_id":"td_q_learning","code":"def q_learning_update(Q, state, action, reward, next_state, alpha, gamma):\n    return Q\n","learning_rate":1.5,"discount_factor":0.9,"exploration_rate":0.1,"episode_count":5}'
```

Observed response:

```json
{"detail":[{"type":"less_than_equal","loc":["body","learning_rate"],"msg":"Input should be less than or equal to 1","input":1.5,"ctx":{"le":1.0}}]}
```

These checks are useful because they verify three separate failure classes:

- lesson-resolution failure
- lesson-function validation failure
- typed schema validation failure

#### 6.5 Interpretation of Current Testing Coverage

The testing procedures above demonstrate that the following claims are currently supported by evidence:

- core backend validation behavior is unit tested
- core logger and job-store behavior is unit tested
- the frontend can render a successful execution result through its controller path
- the backend execution pipeline can complete a successful lesson run and produce a visualization artifact
- the API exposes meaningful error responses for invalid lesson identifiers, invalid code contracts, and invalid numeric payloads

The following areas remain weakly tested or not yet tested in an automated way:

- real frontend-to-backend live integration through the GUI
- frontend playback of the generated video artifact
- request cancellation while a backend job is active
- performance under repeated or concurrent use
- hardware mode, which is still intentionally blocked in the frontend

### 7. Combined Conclusion

Taken together, the implementation overview and testing procedures show that the repository currently contains a functioning software prototype centered on local lesson execution. The strongest implemented path is the simulation workflow from editable lesson template to backend execution, sample-test validation, metric generation, and visualization output. The strongest testing evidence is on the backend side, where unit tests and manual smoke tests verify both normal and failure behavior. The frontend is functionally connected to the backend design, but its live integration coverage remains lighter than the backend’s current test coverage.
