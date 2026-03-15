# 1. Code Snippet Selection Principles

The snippet set was selected using three criteria. First, each excerpt had to represent an actual implementation mechanism rather than a cosmetic or declarative fragment. Second, each excerpt had to support a specific Chapter 4 claim, such as application composition, state propagation, request serialization, backend orchestration, algorithm execution, logging, or visualization. Third, each excerpt was kept short enough to be thesis-usable while preserving the real control flow and interfaces used by the system.

# 2. Thesis-Relevant Code Evidence

## Snippet Title

Frontend Application Entry Point

### Purpose

This snippet proves how the Flutter application is bootstrapped and how the main workbench screen is registered as the application home.

### File

[frontend/lib/main.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/main.dart)

### Code

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

### Technical Significance

The codebase currently implements a single-entry Flutter application in which `main()` launches `RLSimulationIDE`, and `MaterialApp` binds the visual root of the system to `MainLayout`. This is architecturally significant because it shows that the deployed client is a single-shell application rather than a route-driven multi-page interface. It supports the thesis claim that the frontend is organized around a unified interactive workbench.

### Suggested Thesis Use

4.2.1 Architecture

## Snippet Title

Main Workbench Layout Composition

### Purpose

This snippet proves how the user interface is composed from the lesson browser, workspace, and control panels, and how these elements are bound to a central controller.

### File

[frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)

### Code

```dart
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return Scaffold(
          appBar: _buildFigmaAppBar(),
          body: LayoutBuilder(
            builder: (context, constraints) {
              final lessonBrowser = LessonBrowser(
                sections: _controller.sections,
                selectedLesson: _controller.selectedLesson,
                onLessonSelected: _controller.selectLesson,
              );
              final workspace = WorkspaceTabs(
                lesson: _controller.selectedLesson,
                code: _controller.code,
                onCodeChanged: _controller.updateCode,
                statusMessage: _controller.statusMessage,
                runStatusLabel: _controller.runStatusLabel,
                totalReward: _controller.totalReward,
                averageReward: _controller.averageReward,
                bestEpisodeReward: _controller.bestEpisodeReward,
                videoPath: _controller.videoPath,
              );
              final controls = _buildControlsSection();
```

### Technical Significance

This module provides the top-level composition of the frontend workbench. The `AnimatedBuilder` listens directly to the `RLWorkbenchController`, which means UI refresh is driven by state change notifications from a single controller object. The snippet supports the thesis claim that the frontend is implemented as a controller-bound composite interface containing lesson selection, parameter control, code editing, and result presentation in one synchronized layout.

### Suggested Thesis Use

4.2.2 Frontend

## Snippet Title

Workbench State Initialization and Lesson Configuration

### Purpose

This snippet proves that the frontend controller stores lesson metadata, starter code, and run parameters directly in a `ChangeNotifier`-based state object.

### File

[frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)

### Code

```dart
class RLWorkbenchController extends ChangeNotifier {
  RLWorkbenchController({
    BackendApi? api,
  })  : _api = api ?? HttpBackendApi(),
        _sections = const [
          LessonSection(
            title: 'Dynamic Programming',
            lessons: [
              LessonDefinition(
                id: 'dp_policy_eval',
                title: 'Policy Evaluation',
                description:
                    'Evaluate a policy over FrozenLake using Bellman expectation updates.',
                category: 'Dynamic Programming',
                starterCode: '''
def policy_evaluation(V, policy, env, gamma=0.9, theta=1e-8):
    delta = float("inf")
    while delta > theta:
        delta = 0.0
        for state in range(len(V)):
            old_value = V[state]
            new_value = 0.0
''',
              ),
            ],
          ),
```

### Technical Significance

The current implementation includes lesson configuration inside the central controller rather than in an external file or database. This excerpt is important because it shows that the system binds lesson identity, category, and editable starter code into the same state object used by the UI. It supports the thesis claim that the present frontend implementation manages lessons and code templates in-memory as part of the interactive workbench state.

### Suggested Thesis Use

4.2.3 State Management

## Snippet Title

Workbench Run Lifecycle and Result Binding

### Purpose

This snippet proves how the frontend initiates execution, sends the selected lesson and parameters to the backend, and stores the returned metrics and visualization path.

### File

[frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)

### Code

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
    _currentEpisode = 0;
    _currentStep = _nonEmptyLineCount(_code);
    _totalReward = 0.0;
    _averageReward = 0.0;
    _bestEpisodeReward = 0.0;
    _videoPath = '';
    _statusMessage =
        'Running ${_selectedLesson.title} against the backend...';
    notifyListeners();

    try {
      final result = await _api.executeCode(
        lessonId: _selectedLesson.id,
        code: _code,
        learningRate: _learningRate,
        discountFactor: _discountFactor,
        explorationRate: _explorationRate,
        episodeCount: _episodeCount,
      );
```

### Technical Significance

This module provides the asynchronous control-flow bridge between user interaction and backend execution. The controller validates local preconditions, transitions the UI into a running state, serializes the lesson and parameter state into a backend call, and later commits the returned metrics into controller fields. It supports the thesis claim that execution in the current system is coordinated by a single client-side controller responsible for both state mutation and service invocation.

### Suggested Thesis Use

4.3 System Integration

## Snippet Title

Frontend Request Serialization and Response Parsing

### Purpose

This snippet proves how the frontend serializes the execution payload and converts the backend JSON response into typed result objects.

### File

[frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart)

### Code

```dart
  @override
  Future<ExecutionResult> executeCode({
    required String lessonId,
    required String code,
    required double learningRate,
    required double discountFactor,
    required double explorationRate,
    required int episodeCount,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/execute'),
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

    final responseJson = _decodeBody(response.body);
    if (response.statusCode >= 400) {
      throw BackendApiException(_extractErrorMessage(responseJson));
    }

    return ExecutionResult.fromJson(responseJson);
  }
```

### Technical Significance

This excerpt captures the client-side service boundary. The code implements explicit JSON serialization of lesson identifier, source code, and RL hyperparameters, then maps the backend response into a typed `ExecutionResult`. It supports the thesis claim that frontend-backend integration is realized through a local HTTP API with strongly structured request and response handling.

### Suggested Thesis Use

4.2.4 Backend API

## Snippet Title

Parameter Panel Input Binding

### Purpose

This snippet proves how runtime parameters are edited through UI controls and forwarded to the state controller through callbacks.

### File

[frontend/lib/features/controls/parameters_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/parameters_panel.dart)

### Code

```dart
          TextField(
            controller: _episodesController,
            keyboardType: TextInputType.number,
            onChanged: widget.onEpisodeCountChanged,
            decoration: InputDecoration(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: AppTheme.borderLight),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text('Run mode', style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              border: Border.all(color: AppTheme.borderLight),
              borderRadius: BorderRadius.circular(8),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: widget.runMode == RunMode.simulation
                    ? 'Simulation'
                    : 'Hardware',
                isExpanded: true,
                items: ['Simulation', 'Hardware'].map((String value) {
```

### Technical Significance

The codebase currently implements parameter editing as direct callback binding from widgets into the controller. The excerpt is useful because it shows that episode count and run mode are not static labels; they are true interactive inputs that update execution state. It supports the thesis claim that the frontend includes a parameterized execution interface rather than a fixed demonstration screen.

### Suggested Thesis Use

4.2.2 Frontend

## Snippet Title

Run Panel Control Binding

### Purpose

This snippet proves how the frontend exposes the operational actions `Run`, `Stop`, and `Reset`, and how execution metrics are displayed in the control panel.

### File

[frontend/lib/features/controls/run_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/run_panel.dart)

### Code

```dart
          ElevatedButton.icon(
            onPressed: onRun,
            icon: const Icon(Icons.play_arrow_outlined),
            label: const Text('Run'),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onStop,
                  icon: const Icon(Icons.stop_outlined, size: 20),
                  label: const Text('Stop'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onReset,
                  icon: const Icon(Icons.refresh_outlined, size: 20),
                  label: const Text('Reset'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 24),
          _buildMetricRow(context, 'Episode:', '$currentEpisode / $episodeCount'),
          const SizedBox(height: 12),
          _buildMetricRow(context, 'Step:', '$currentStep'),
```

### Technical Significance

This excerpt demonstrates that the workbench implements an execution control surface, not only a code editor. It exposes operational actions and binds them to callbacks from the main controller, while simultaneously reflecting current episode and step counters in the same panel. It supports the thesis claim that the interface integrates command and monitoring functions in a unified control component.

### Suggested Thesis Use

4.2.2 Frontend

## Snippet Title

Code Editor Synchronization with Controller State

### Purpose

This snippet proves that the code editor is synchronized with the current lesson selection and propagates user edits back into the workbench controller.

### File

[frontend/lib/features/workspace/code_editor.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/code_editor.dart)

### Code

```dart
class _CodeEditorTabState extends State<CodeEditorTab> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.code);
  }

  @override
  void didUpdateWidget(covariant CodeEditorTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.code != widget.code && _controller.text != widget.code) {
      _controller.value = TextEditingValue(
        text: widget.code,
        selection: TextSelection.collapsed(offset: widget.code.length),
      );
    }
  }
```

### Technical Significance

This module provides the synchronization mechanism between lesson changes and editor contents. The text controller is initialized from the currently selected lesson code and is updated whenever the parent widget passes a new code string. It supports the thesis claim that the code editor is integrated into the lesson workflow and does not operate as an isolated text area.

### Suggested Thesis Use

4.2.2 Frontend

## Snippet Title

Execution Result Rendering in the Workspace

### Purpose

This snippet proves how backend-produced status text, reward metrics, and the generated video path are bound into the result view.

### File

[frontend/lib/features/workspace/video_player.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/video_player.dart)

### Code

```dart
              Text(
                'Visualization: $lessonTitle',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              Text(
                runStatusLabel,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppTheme.primaryBlue,
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 8),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Text(
                  statusMessage,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Total reward: ${totalReward.toStringAsFixed(1)}',
```

### Technical Significance

The current implementation includes a bound results view in which execution outputs are displayed directly from controller state. This excerpt matters because it shows the UI contract for returned backend data: lesson title, run status, message text, and reward metrics are rendered as live interface data. It supports the thesis claim that backend execution output is surfaced to the user in a dedicated results panel.

### Suggested Thesis Use

4.3 System Integration

## Snippet Title

FastAPI Application Setup and Request Schema

### Purpose

This snippet proves the existence of the backend service boundary, including middleware configuration and the typed request model used by the execution endpoint.

### File

[backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)

### Code

```python
app = FastAPI(title="RL IDE Backend Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global components
validator = CodeValidator()

class CodeSubmission(BaseModel):
    lesson_id: str
    code: str
    learning_rate: float = Field(gt=0, le=1)
    discount_factor: float = Field(gt=0, le=1)
    exploration_rate: float = Field(ge=0, le=1)
    episode_count: int = Field(default=5, ge=1, le=500)
```

### Technical Significance

This code defines the backend as a concrete HTTP service rather than an internal library. The `CodeSubmission` model constrains the execution request using typed fields and numeric bounds, while the CORS middleware enables local cross-origin access from the frontend. It supports the thesis claim that the backend API is implemented as a typed FastAPI gateway with explicit execution inputs.

### Suggested Thesis Use

4.2.4 Backend API

## Snippet Title

Execution Route Orchestration and Response Construction

### Purpose

This snippet proves how a backend request is processed end-to-end: lesson resolution, validation, engine execution, visualization generation, and structured response return.

### File

[backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)

### Code

```python
@app.post("/execute")
def execute_code(submission: CodeSubmission):
    lesson = get_lesson_definition(submission.lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail=f"Unknown lesson '{submission.lesson_id}'.")

    adapter = None
    logger = EventLogger(log_dir="backend/logger/logs")
    visualizer = VisualizationController(output_dir="backend/visualization/animations")

    try:
        adapter = EnvironmentAdapter(env_name=lesson.environment_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        validation_result = validator.validate_code(submission.code, submission.lesson_id)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Code validation failed.",
                    "issues": validation_result.errors,
                },
            )

        engine = RLEngine(adapter=adapter, logger=logger)
        engine.run_episodes(
            submission.lesson_id,
            submission.code,
```

### Technical Significance

This excerpt is one of the strongest pieces of code evidence in the repository because it exposes the orchestration layer of the backend. The route connects lesson lookup, environment creation, contract validation, simulation execution, logging, and visualization into one deterministic service pipeline. It supports the thesis claim that the backend is not limited to request forwarding, but performs integrated execution management and response assembly.

### Suggested Thesis Use

4.3 System Integration

## Snippet Title

Lesson Registry and Function Contract Mapping

### Purpose

This snippet proves how lesson identifiers are bound to titles, required function names, and environment names.

### File

[backend/lessons.py](/Users/ultramarine/Desktop/grad_project/backend/lessons.py)

### Code

```python
@dataclass(frozen=True)
class LessonDefinition:
    id: str
    title: str
    required_function: str
    environment_name: str


LESSON_DEFINITIONS = {
    "dp_policy_eval": LessonDefinition(
        id="dp_policy_eval",
        title="Dynamic Programming: Policy Evaluation",
        required_function="policy_evaluation",
        environment_name="FrozenLake",
    ),
    "mc_first_visit": LessonDefinition(
        id="mc_first_visit",
        title="Monte Carlo: First-Visit Prediction",
        required_function="mc_first_visit_prediction",
        environment_name="FrozenLake",
    ),
```

### Technical Significance

The current implementation includes an explicit lesson registry rather than implicit string comparisons distributed throughout the system. This matters because it defines the execution contract for each lesson in one data structure, including the required student-defined function name and the environment to instantiate. It supports the thesis claim that lesson execution is governed by a formal registry of lesson metadata and callable contracts.

### Suggested Thesis Use

4.2.5 RL Execution

## Snippet Title

Dynamic Code Execution and Lesson Dispatch

### Purpose

This snippet proves that the backend loads submitted code dynamically, resolves the required function, and dispatches execution according to the selected lesson.

### File

[backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)

### Code

```python
    def run_episodes(self, lesson_id: str, code_module_str: str, num_episodes: int, hyperparameters: Dict[str, float]):
        """Runs the RL loop with the injected code snippet."""
        self.logger.clear()
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            raise ValueError(f"Unsupported lesson '{lesson_id}'.")

        local_context: Dict[str, Any] = {"__builtins__": __builtins__}
        exec(code_module_str, local_context, local_context)

        lesson_function = local_context.get(lesson.required_function)
        if not callable(lesson_function):
            raise ValueError(
                f"Required function '{lesson.required_function}' is missing from the submission."
            )

        if lesson_id == "dp_policy_eval":
            self._run_policy_evaluation(lesson_function, num_episodes, hyperparameters)
        elif lesson_id == "mc_first_visit":
            self._run_mc_first_visit(lesson_function, num_episodes, hyperparameters)
        elif lesson_id == "td_q_learning":
            self._run_q_learning(lesson_function, num_episodes, hyperparameters)
```

### Technical Significance

This excerpt shows the central execution mechanism of the backend. The engine dynamically evaluates the submitted code, extracts the function required by the lesson registry, and dispatches control to a lesson-specific execution path. It supports the thesis claim that the platform executes user-provided RL logic within a controlled lesson-dependent backend pipeline.

### Suggested Thesis Use

4.2.5 RL Execution

## Snippet Title

Q-Learning Episode Loop with Step Logging

### Purpose

This snippet proves how the backend steps the environment, applies a user-defined update function, and records the transition trace required for later analysis and visualization.

### File

[backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)

### Code

```python
    def _run_q_learning(self, lesson_function, num_episodes: int, hyperparameters: Dict[str, float]):
        state_count = self.adapter.env.observation_space.n
        action_count = self.adapter.env.action_space.n
        q_table = [[0.0 for _ in range(action_count)] for _ in range(state_count)]

        for _ in range(num_episodes):
            state, _ = self.adapter.reset()
            done = False

            while not done:
                action = self.adapter.env.action_space.sample()
                next_state, reward, terminated, truncated, _ = self.adapter.step(action)
                lesson_function(
                    q_table,
                    state,
                    action,
                    reward,
                    next_state,
                    hyperparameters["alpha"],
                    hyperparameters["gamma"],
                )
                self.logger.log_step(
                    {
                        "state": state,
                        "action": action,
                        "reward": reward,
                        "next_state": next_state,
```

### Technical Significance

This module provides concrete evidence of the backend RL loop. The environment is stepped iteratively, the user-supplied learning rule is executed against the evolving Q-table, and each transition is recorded by the event logger. It supports the thesis claim that the current implementation performs real simulation-time RL updates and not merely static code evaluation.

### Suggested Thesis Use

4.2.5 RL Execution

## Snippet Title

Lesson-Aware Code Validation

### Purpose

This snippet proves how the backend validates that the submitted source code contains the required callable for the selected lesson before execution begins.

### File

[backend/validation/validator.py](/Users/ultramarine/Desktop/grad_project/backend/validation/validator.py)

### Code

```python
    def validate_code(self, submitted_code: str, lesson_id: str) -> ValidationResult:
        """
        Executes the submitted code against lesson-specific contract checks.
        """
        lesson = get_lesson_definition(lesson_id)
        if lesson is None:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown lesson_id '{lesson_id}'."],
            )

        if not submitted_code.strip():
            return ValidationResult(
                is_valid=False,
                errors=["Submitted code is empty."],
            )

        try:
            local_context: Dict[str, Any] = {"__builtins__": __builtins__}
            exec(submitted_code, local_context, local_context)

            function = local_context.get(lesson.required_function)
            if not callable(function):
```

### Technical Significance

This excerpt demonstrates that validation is lesson-dependent rather than generic. The validator resolves the lesson contract, executes the submitted code in a temporary context, and checks whether the required function exists and is callable. It supports the thesis claim that the backend enforces a structural correctness gate before entering the RL execution loop.

### Suggested Thesis Use

4.2.6 Validation

## Snippet Title

Structured Episode Logging

### Purpose

This snippet proves how RL interaction traces are accumulated at step level and grouped into episode-level histories.

### File

[backend/logger/event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/logger/event_logger.py)

### Code

```python
class EventLogger:
    """Logs intermediate RL steps in a structured format during simulation."""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.current_episode = []
        self.all_episodes = []
        os.makedirs(self.log_dir, exist_ok=True)
        
    def clear(self):
        """Clears existing logs for a new run."""
        self.current_episode = []
        self.all_episodes = []

    def log_step(self, step_data: Dict[str, Any]):
        """
        Logs a single step.
        Expected format includes: state, action, reward, next_state, updated_values (e.g., Q-estimates)
        """
        self.current_episode.append(step_data)
```

### Technical Significance

The current implementation includes an explicit logging subsystem dedicated to RL state transitions. The logger accumulates step dictionaries in-memory, allowing each episode to be reconstructed as a structured trace. It supports the thesis claim that execution traces are retained in a machine-readable form for post-processing and visualization.

### Suggested Thesis Use

4.2.7 Logging

## Snippet Title

Visualization Pipeline and Manim Subprocess Invocation

### Purpose

This snippet proves how logged execution traces are serialized, converted into a generated Manim scene, and rendered into an MP4 file by subprocess invocation.

### File

[backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py)

### Code

```python
    def generate_animation(self, log_data: list, lesson_id: str) -> str:
        """
        Takes the log_data from EventLogger and uses Manim to generate an mp4.
        Returns the path to the generated MP4.
        """
        if not log_data or not log_data[0]:
            logging.warning("No log data provided for Manim visualization.")
            return ""

        latest_episode = log_data[-1] 
        data_path = os.path.join(self.scenes_dir, "temp_data.json")
        with open(data_path, "w") as f:
            json.dump(latest_episode, f, cls=NpEncoder)

        scene_file = os.path.join(self.scenes_dir, f"{lesson_id}_scene.py")
        self._write_manim_script(scene_file, data_path, lesson_id)
        
        video_output_dir = os.path.abspath(self.output_dir)
        cmd = [
            self.manim_python_path, "-m", "manim",
            "-pqL",
            "--media_dir", video_output_dir,
            scene_file,
            "RLEpisodeScene"
        ]
```

### Technical Significance

This excerpt exposes the visualization bridge between simulation logs and rendered media. The controller selects the latest episode trace, writes it to JSON, generates a scene script, and launches Manim through a subprocess command that targets the generated scene. It supports the thesis claim that the current implementation includes an automated visualization pipeline rather than manual or pre-rendered media.

### Suggested Thesis Use

4.2.8 Visualization

# 3. Minimum Snippet Set for Chapter 4

- Frontend Application Entry Point
  - File: [frontend/lib/main.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/main.dart)
  - Reason: establishes the client bootstrap and single-shell application structure.

- Main Workbench Layout Composition
  - File: [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)
  - Reason: shows how the major user-facing subsystems are composed around one controller.

- Workbench State Initialization and Lesson Configuration
  - File: [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)
  - Reason: proves that lesson metadata and starter code are maintained in the central frontend state object.

- Workbench Run Lifecycle and Result Binding
  - File: [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)
  - Reason: shows the full client-side execution lifecycle and state mutation after backend completion.

- Frontend Request Serialization and Response Parsing
  - File: [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart)
  - Reason: captures the exact request payload and typed response handling used for integration.

- FastAPI Application Setup and Request Schema
  - File: [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)
  - Reason: demonstrates the service boundary and request contract of the backend.

- Execution Route Orchestration and Response Construction
  - File: [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)
  - Reason: proves that the backend integrates validation, execution, logging, visualization, and metric return in one pipeline.

- Lesson Registry and Function Contract Mapping
  - File: [backend/lessons.py](/Users/ultramarine/Desktop/grad_project/backend/lessons.py)
  - Reason: provides direct evidence of lesson-to-function and lesson-to-environment binding.

- Dynamic Code Execution and Lesson Dispatch
  - File: [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)
  - Reason: shows how submitted code is executed and routed into lesson-specific algorithm paths.

- Q-Learning Episode Loop with Step Logging
  - File: [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)
  - Reason: provides the clearest evidence of real environment stepping, learner update application, and trace capture.

- Lesson-Aware Code Validation
  - File: [backend/validation/validator.py](/Users/ultramarine/Desktop/grad_project/backend/validation/validator.py)
  - Reason: demonstrates the pre-execution correctness gate used by the backend.

- Visualization Pipeline and Manim Subprocess Invocation
  - File: [backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py)
  - Reason: shows the actual mechanism by which execution traces are converted into rendered animation output.

# 4. Missing Code Evidence Placeholders

- 4.1 Hardware Implementation
  - [Placeholder for future code evidence]

- Persistent Storage / Database Layer
  - [Placeholder for future code evidence]

- Lesson Authoring / Video Authoring Workflow
  - [Placeholder for future code evidence]
