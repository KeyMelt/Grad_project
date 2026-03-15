# 1. Repository Overview

- Main technologies used:
  - Flutter with Dart for the client application in [frontend](/Users/ultramarine/Desktop/grad_project/frontend)
  - Python with FastAPI for the backend in [backend](/Users/ultramarine/Desktop/grad_project/backend)
  - Gymnasium for RL environment simulation in [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)
  - Manim for animation generation in [backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py)
  - Pydantic for backend request validation in [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)

- Top-level folders and their roles:
  - [backend](/Users/ultramarine/Desktop/grad_project/backend): Python backend, lesson registry, RL execution loop, validation, logging, visualization, tests
  - [frontend](/Users/ultramarine/Desktop/grad_project/frontend): Flutter client, UI widgets, local state controller, HTTP integration, widget test
  - [ARCHITECTURE.md](/Users/ultramarine/Desktop/grad_project/ARCHITECTURE.md): intended system architecture description
  - [README.md](/Users/ultramarine/Desktop/grad_project/README.md): current repository-level run instructions

- Overall architecture style actually present in the codebase:
  - The codebase currently implements a two-process local client-server architecture.
  - The frontend is a single-window Flutter application with manual state management through a `ChangeNotifier` and `AnimatedBuilder`, rather than an external state framework.
  - The backend is a synchronous request-response FastAPI service that receives a lesson identifier, user code, and numeric parameters, executes the request immediately, and returns metrics and an optional video path.
  - No database, message queue, authentication layer, or distributed service architecture is present.

- Brief statement of implementation maturity:
  - The current implementation includes a functional vertical slice that connects a Flutter interface to a Python backend, executes a small set of tabular RL lesson types on a single environment, logs step data, and can generate simple Manim animations.
  - The codebase is best characterized as an early prototype or partial implementation rather than a fully feature-complete educational platform.

# 2. Implemented Subsystems

## Frontend application structure

### Purpose

This subsystem provides the client application shell, layout composition, and high-level widget arrangement for the educational platform.

### Implementation Status

- Partially implemented

### Evidence

- [frontend/lib/main.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/main.dart)
- [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)
- [frontend/lib/core/constants.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/constants.dart)
- [frontend/lib/core/theme.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/theme.dart)

### Technical Description

The frontend starts in `main()` and instantiates `RLSimulationIDE`, which returns a `MaterialApp`. The application sets a single `home` widget, `MainLayout`, rather than defining named routes or a navigation stack. `MainLayout` is the central composition widget and constructs a three-part interface: a lesson browser on the left, a workspace area in the center, and control panels on the right for wider windows. For narrower widths, the same content is rearranged into a vertically scrollable layout.

The layout uses constant widths from `AppConstants` and theme definitions from `AppTheme`. The implementation is entirely widget-local and does not use route tables, shell navigation frameworks, or module-based screen registration.

### Notes on Completeness

- The application shell is present and functional.
- Only a single main screen exists.
- There is no multi-page navigation, onboarding flow, authentication flow, or administrative UI.

## UI navigation and screen routing

### Purpose

This subsystem would normally provide screen-level navigation between pages or modules.

### Implementation Status

- Scaffold only

### Evidence

- [frontend/lib/main.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/main.dart)
- [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)

### Technical Description

The current implementation uses a single `MaterialApp` with one `home` widget and no named routes, `Navigator` push calls, route generator, or page registry. User interaction occurs entirely within a single composite screen. The only navigational pattern present is a `DefaultTabController` inside the workspace area for switching between a video/results panel and a code editor panel.

### Notes on Completeness

- Internal tab switching exists.
- Screen-level navigation is not implemented.
- The thesis can claim a single-screen desktop interface, but not a multi-screen application flow.

## Add video lesson screen

### Purpose

This subsystem would allow lesson authors or instructors to create or upload video lesson content.

### Implementation Status

- Not found

### Evidence

- No executable implementation was found in [frontend/lib](/Users/ultramarine/Desktop/grad_project/frontend/lib) or [backend](/Users/ultramarine/Desktop/grad_project/backend).

### Technical Description

No form, route, data model, upload workflow, or storage path for creating video lessons is present. The file named `video_player.dart` is not an authoring screen; it is a results/status widget that displays returned metrics and a video path string.

### Notes on Completeness

- No implementation for adding or managing video lesson content was found.

## Coding exercise configuration screen

### Purpose

This subsystem would configure exercises, lesson metadata, or boilerplate templates from an authoring perspective.

### Implementation Status

- Scaffold only

### Evidence

- [frontend/lib/features/controls/parameters_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/parameters_panel.dart)
- [frontend/lib/features/workspace/code_editor.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/code_editor.dart)
- [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)

### Technical Description

The current implementation provides runtime parameter editing for learning rate, discount factor, exploration rate, episode count, and run mode. It also provides a full-text editable code editor containing lesson-specific starter code. However, these features configure an execution session rather than defining new exercises or persisting exercise metadata.

Lesson starter code is hardcoded in the `RLWorkbenchController`, and the user edits that code in a single multiline `TextField`. No authoring UI exists to define new lessons, change validation rules, upload reference videos, or store exercises externally.

### Notes on Completeness

- Runtime exercise editing exists.
- Exercise authoring or configuration management does not exist.

## Sidebar / parameter panel / toggleable controls

### Purpose

This subsystem allows the user to inspect lessons, edit RL parameters, and trigger execution.

### Implementation Status

- Partially implemented

### Evidence

- [frontend/lib/features/lessons/lesson_browser.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/lessons/lesson_browser.dart)
- [frontend/lib/features/lessons/lesson_card.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/lessons/lesson_card.dart)
- [frontend/lib/features/controls/parameters_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/parameters_panel.dart)
- [frontend/lib/features/controls/run_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/run_panel.dart)

### Technical Description

The lesson browser renders grouped lesson categories and individual lesson cards. The cards are clickable and update the selected lesson through callbacks into the central controller. The parameter panel exposes sliders and text input for numeric parameters and a dropdown for run mode. The run panel includes buttons for `Run`, `Stop`, and `Reset`, and displays current episode count, step count, run status, connection label, and total reward.

The `Stop` action currently changes frontend state only. No backend cancellation mechanism is implemented. The `Share` and some app bar buttons are also present visually but have empty callbacks.

### Notes on Completeness

- Lesson selection and runtime parameter adjustment are implemented.
- Control actions are partially implemented.
- Several controls remain UI placeholders with no business logic behind them.

## State management

### Purpose

This subsystem holds the lesson definitions, editable code, numeric parameters, run status, metrics, and backend output state for the UI.

### Implementation Status

- Fully implemented

### Evidence

- [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)
- [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)

### Technical Description

The central state object is `RLWorkbenchController`, which extends `ChangeNotifier`. It stores:

- hardcoded lesson sections and lesson definitions
- currently selected lesson
- editable code text
- learning rate, discount factor, exploration rate, episode count
- current run mode
- run state enum
- current episode count and step count
- total reward, average reward, best episode reward
- current status message
- current video path

`MainLayout` instantiates this controller and rebuilds through `AnimatedBuilder`. No `Provider`, `Bloc`, `Riverpod`, or inherited service container is used. The controller also performs side effects directly by invoking the backend API client. This means state management and service orchestration are coupled in one class.

### Notes on Completeness

- The current implementation includes a coherent local state model for the existing UI.
- The solution is simple and functional, but not separated into repository/service/viewmodel layers.

## Platform build scaffolding

### Purpose

This subsystem provides the native runner projects and platform-level build settings required to package the Flutter client for desktop and mobile operating systems.

### Implementation Status

- Partially implemented

### Evidence

- [frontend/macos/Runner/DebugProfile.entitlements](/Users/ultramarine/Desktop/grad_project/frontend/macos/Runner/DebugProfile.entitlements)
- [frontend/macos/Runner/Release.entitlements](/Users/ultramarine/Desktop/grad_project/frontend/macos/Runner/Release.entitlements)
- [frontend/macos/Runner/Configs/AppInfo.xcconfig](/Users/ultramarine/Desktop/grad_project/frontend/macos/Runner/Configs/AppInfo.xcconfig)
- [frontend/android/app/src/main/AndroidManifest.xml](/Users/ultramarine/Desktop/grad_project/frontend/android/app/src/main/AndroidManifest.xml)
- [frontend/ios/Runner/Info.plist](/Users/ultramarine/Desktop/grad_project/frontend/ios/Runner/Info.plist)

### Technical Description

The codebase currently includes generated Flutter runner projects for macOS, Android, and iOS. The macOS runner contains explicit sandbox entitlements for outbound networking, which is required for the desktop client to call the local FastAPI backend. `AppInfo.xcconfig` defines the macOS product name and bundle identifier. Android and iOS runner files are also present, but they remain close to the default generated Flutter scaffold and do not contain custom native integrations for RL, hardware communication, or media playback.

### Notes on Completeness

- macOS support is meaningfully configured because the entitlement files explicitly allow client networking.
- Android and iOS support exist mainly as generated project scaffolds.
- No custom native plugin, platform channel, or hardware bridge implementation was found in the native runners.

## Lesson model and content configuration

### Purpose

This subsystem defines what lessons exist, how they are categorized, and which backend function each lesson requires.

### Implementation Status

- Partially implemented

### Evidence

- [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)
- [backend/lessons.py](/Users/ultramarine/Desktop/grad_project/backend/lessons.py)

### Technical Description

The frontend defines `LessonDefinition` and `LessonSection` as immutable Dart classes and hardcodes three lessons:

- Policy Evaluation
- MC Prediction
- Q-Learning

Each lesson includes an identifier, title, description, category, starter code, and simple flags for `hasVideo` and `hasHardware`.

The backend defines a separate `LessonDefinition` dataclass containing only the lesson identifier, title, required function name, and environment name. The backend registry is used to validate the incoming lesson identifier and route execution logic to the correct engine branch.

No shared configuration file, JSON lesson catalog, YAML schema, database table, or CMS layer exists. Frontend and backend lesson definitions are manually duplicated.

### Notes on Completeness

- The platform has a working in-code lesson registry.
- It is not externally configurable.
- Lesson metadata duplication across frontend and backend is a maintenance limitation.

## RL algorithm implementation

### Purpose

This subsystem executes the algorithmic lesson logic for dynamic programming, Monte Carlo, and temporal-difference learning.

### Implementation Status

- Partially implemented

### Evidence

- [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)
- [backend/rl_engine/templates/dp_policy_eval.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/templates/dp_policy_eval.py)
- [backend/rl_engine/templates/mc_first_visit.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/templates/mc_first_visit.py)
- [backend/rl_engine/templates/td_q_learning.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/templates/td_q_learning.py)
- [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)

### Technical Description

The backend `RLEngine` executes one of three lesson flows depending on `lesson_id`. It dynamically evaluates the submitted code string using `exec`, extracts the required function from that dynamic context, and then invokes one of:

- `_run_policy_evaluation`
- `_run_mc_first_visit`
- `_run_q_learning`

Each flow operates on a `FrozenLake-v1` environment, creates basic in-memory state structures such as `values`, `returns`, or `q_table`, and logs each step through `EventLogger`.

However, the codebase does not contain a mature built-in library of RL algorithms. The reusable algorithm files under `backend/rl_engine/templates` are placeholders containing `pass`. The actual runnable example logic shown to the user exists mainly as starter code strings embedded in the frontend controller. Furthermore, action selection in the engine is random sampling from the action space; no actual epsilon-greedy control policy is implemented in the engine itself.

### Notes on Completeness

- A partial implementation exists for executing user-supplied RL update functions within a minimal lesson pipeline.
- The thesis can claim the presence of execution paths for DP, MC, and Q-learning lessons.
- It cannot honestly claim a full internal library of completed RL algorithm implementations or advanced algorithm comparison features.

## Environment/simulation integration

### Purpose

This subsystem integrates the educational platform with an RL environment for actual state transitions and rewards.

### Implementation Status

- Partially implemented

### Evidence

- [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py)

### Technical Description

The `EnvironmentAdapter` class encapsulates environment creation, reset, step, and close operations. At present, it supports only one environment: `FrozenLake-v1` with a fixed 4x4 map and `is_slippery=False`. The environment is used in all three lesson types.

The engine resets the environment, samples actions, steps the environment, and logs the transition tuple `state`, `action`, `reward`, and `next_state`. Observations are discrete state indices from the Gymnasium environment.

### Notes on Completeness

- RL environment integration exists for one deterministic tabular environment.
- No multi-environment support, no robotics simulator, no custom environment authoring, and no continuous control support were found.

## Visualization/animation pipeline

### Purpose

This subsystem transforms logged RL step data into rendered animations.

### Implementation Status

- Partially implemented

### Evidence

- [backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py)
- [backend/visualization/animations/scenes/dp_policy_eval_scene.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/scenes/dp_policy_eval_scene.py)
- [backend/visualization/animations/scenes/td_q_learning_scene.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/scenes/td_q_learning_scene.py)
- [backend/visualization/animations/videos/dp_policy_eval_scene/480p15/RLEpisodeScene.mp4](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/videos/dp_policy_eval_scene/480p15/RLEpisodeScene.mp4)
- [backend/visualization/animations/videos/td_q_learning_scene/480p15/RLEpisodeScene.mp4](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/videos/td_q_learning_scene/480p15/RLEpisodeScene.mp4)

### Technical Description

`VisualizationController` receives episode log data, serializes the latest episode to `temp_data.json`, generates a Manim scene file dynamically, and launches Manim as a subprocess using a configured Python interpreter. The generated animation consists of:

- a grid represented with `NumberPlane`
- a title identifying the lesson
- a red dot as the agent position
- per-step movement across the grid
- temporary text overlays for updated values

The scene files under `backend/visualization/animations/scenes` appear to be generated outputs rather than a handcrafted visualization library. Generated SVG text fragments and MP4 files are also present in the repository, which demonstrates that the pipeline has run successfully at least for some lessons.

### Notes on Completeness

- The codebase currently implements a working animation generation pipeline.
- The visuals are generic and limited.
- No heatmaps, symbolic equation mapping, epsilon-greedy visualization, or Bellman backup table animation was found.

## User interaction and execution flow

### Purpose

This subsystem connects the visible UI actions to backend execution and returned results.

### Implementation Status

- Partially implemented

### Evidence

- [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)
- [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)
- [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart)

### Technical Description

The user selects a lesson, edits the code, adjusts parameters, and presses `Run`. `RLWorkbenchController.run()` validates the local state, switches the UI into a `running` status, and invokes the backend through `HttpBackendApi.executeCode()`. The request body includes:

- `lesson_id`
- `code`
- `learning_rate`
- `discount_factor`
- `exploration_rate`
- `episode_count`

The returned JSON is parsed into `ExecutionResult` and `ExecutionMetrics`, and then displayed in the run panel and video/results panel. The video/results tab does not play the generated MP4; it only displays the video path string.

### Notes on Completeness

- End-to-end request/response interaction exists.
- Result visualization inside the frontend remains textual rather than multimedia playback.
- `Stop` does not cancel the backend.

## Persistence/storage

### Purpose

This subsystem would manage durable storage for lessons, runs, analytics, or user state.

### Implementation Status

- Scaffold only

### Evidence

- [backend/logger/event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/logger/event_logger.py)
- [backend/visualization/animations/scenes/temp_data.json](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/scenes/temp_data.json)

### Technical Description

No database or persistent application data layer exists. The frontend stores all state in memory inside `RLWorkbenchController`. The backend stores run logs in memory inside `EventLogger`, though the class includes a `save_logs()` method that can write a JSON file. During visualization, the backend writes transient JSON scene input and generated media files into the repository under `backend/visualization/animations`.

### Notes on Completeness

- File-based intermediate output exists.
- No durable user storage, lesson repository, analytics store, or results history was found.

## Backend/API/service layer

### Purpose

This subsystem exposes the execution service to the frontend and orchestrates lesson validation, RL execution, and result construction.

### Implementation Status

- Partially implemented

### Evidence

- [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)
- [backend/main.py](/Users/ultramarine/Desktop/grad_project/backend/main.py)
- [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart)

### Technical Description

The backend provides three routes:

- `GET /` returns a status object
- `GET /lessons` returns the available lesson registry
- `POST /execute` performs validation, simulation, visualization, and response assembly

`CodeSubmission` is the main request model and applies numeric constraints with Pydantic fields. CORS is enabled globally. The backend creates per-request logger and visualization controller instances, validates submitted code, executes the lesson, computes aggregate metrics, and returns a JSON response containing lesson metadata, metrics, and a video path.

The frontend service layer is minimal and consists of one HTTP client class that performs only `POST /execute`. No authentication, user accounts, retry policy, or structured backend repository layer exists.

### Notes on Completeness

- The local service bridge is implemented.
- The backend is narrow in scope and suitable for the current prototype only.

## Testing infrastructure

### Purpose

This subsystem verifies selected backend and frontend behavior.

### Implementation Status

- Partially implemented

### Evidence

- [backend/tests/test_validator.py](/Users/ultramarine/Desktop/grad_project/backend/tests/test_validator.py)
- [backend/tests/test_event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/tests/test_event_logger.py)
- [frontend/test/widget_test.dart](/Users/ultramarine/Desktop/grad_project/frontend/test/widget_test.dart)
- [backend/test_execution.py](/Users/ultramarine/Desktop/grad_project/backend/test_execution.py)

### Technical Description

The backend test suite uses `unittest` and covers two small areas:

- validation behavior for unknown lessons and missing functions
- event logger episode lifecycle behavior

The frontend has a single widget test that injects a fake backend client and verifies a successful lesson run updates the UI with status text, metric text, and a video path string.

`backend/test_execution.py` is a manual request script rather than an automated test.

### Notes on Completeness

- Basic unit and widget tests exist.
- No integration tests, no end-to-end frontend-backend tests, no performance tests, and no hardware tests were found.

## Hardware communication / Bluetooth / robot integration

### Purpose

This subsystem would support ESP32, BLE, robot peripherals, sensors, or physical actuation.

### Implementation Status

- Not found

### Evidence

- Repository-wide search did not find executable hardware, BLE, ESP32, or robot communication modules in [backend](/Users/ultramarine/Desktop/grad_project/backend) or [frontend/lib](/Users/ultramarine/Desktop/grad_project/frontend/lib).

### Technical Description

The only visible reference to hardware is the `Run mode` dropdown, which includes a `Hardware` option, and `hasHardware` flags on some lessons in the frontend controller. These are presentation-level placeholders. `RLWorkbenchController.run()` explicitly rejects hardware mode with a failure status message, indicating that no hardware path exists.

### Notes on Completeness

- No executable implementation was found for hardware communication.

## Error handling and validation

### Purpose

This subsystem prevents invalid submissions, reports errors, and manages failure states.

### Implementation Status

- Partially implemented

### Evidence

- [backend/validation/validator.py](/Users/ultramarine/Desktop/grad_project/backend/validation/validator.py)
- [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)
- [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart)
- [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)

### Technical Description

The backend validator checks:

- whether the lesson identifier is known
- whether the submitted code is empty
- whether the required function is defined and callable

The backend then maps failures to HTTP exceptions and returns error payloads. The frontend distinguishes `BackendApiException` from generic failure and updates the UI status accordingly.

However, there is no execution timeout, no sandboxing of user code, no loop watchdog, and no backend cancellation path. The validator checks contract shape rather than mathematical correctness.

### Notes on Completeness

- Basic validation is implemented.
- Safety and robustness mechanisms remain incomplete.

## Logging/debug tooling

### Purpose

This subsystem captures run-step information and provides lightweight debugging aids.

### Implementation Status

- Partially implemented

### Evidence

- [backend/logger/event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/logger/event_logger.py)
- [backend/test_execution.py](/Users/ultramarine/Desktop/grad_project/backend/test_execution.py)
- [backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py)

### Technical Description

`EventLogger` records each execution step into an in-memory episode structure and can export JSON. The visualization controller uses Python logging and writes warnings or errors if Manim is unavailable or fails. The manual `test_execution.py` file provides a small debugging script for backend route testing.

### Notes on Completeness

- Step-level RL logging exists.
- There is no structured application telemetry, no audit logging of user edits, and no researcher-oriented logging pipeline.

# 3. Screen-by-Screen Implementation Audit

- Screen name: Application Shell
  - Purpose: top-level desktop interface
  - File location: [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart)
  - Key widgets/components: `Scaffold`, app bar, lesson browser, workspace tabs, controls section
  - Connected logic/providers/controllers: `RLWorkbenchController`
  - Current completeness: partially complete
  - Missing pieces: no route navigation, app bar actions mostly placeholders

- Screen name: Lesson Browser
  - Purpose: display available lesson categories and allow lesson selection
  - File location: [frontend/lib/features/lessons/lesson_browser.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/lessons/lesson_browser.dart)
  - Key widgets/components: grouped categories, `LessonCard`
  - Connected logic/providers/controllers: `RLWorkbenchController.selectLesson`
  - Current completeness: complete for the current hardcoded lesson list
  - Missing pieces: no dynamic lesson loading from backend, no authoring UI

- Screen name: Lesson Card
  - Purpose: display an individual lesson summary and status badges
  - File location: [frontend/lib/features/lessons/lesson_card.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/lessons/lesson_card.dart)
  - Key widgets/components: title, description, video badge, hardware badge
  - Connected logic/providers/controllers: click callback only
  - Current completeness: complete as a presentation widget
  - Missing pieces: no deeper navigation or metadata drill-down

- Screen name: Parameters Panel
  - Purpose: modify execution parameters before running a lesson
  - File location: [frontend/lib/features/controls/parameters_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/parameters_panel.dart)
  - Key widgets/components: sliders, episode count text field, run mode dropdown
  - Connected logic/providers/controllers: `updateLearningRate`, `updateDiscountFactor`, `updateExplorationRate`, `updateEpisodeCount`, `updateRunMode`
  - Current completeness: partially complete
  - Missing pieces: no saved presets, no parameter validation feedback beyond integer parsing, hardware mode not implemented

- Screen name: Run Controls Panel
  - Purpose: trigger execution and display run statistics
  - File location: [frontend/lib/features/controls/run_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/run_panel.dart)
  - Key widgets/components: run, stop, reset buttons; metric rows; status message
  - Connected logic/providers/controllers: `run`, `stop`, `reset`
  - Current completeness: partially complete
  - Missing pieces: stop does not cancel backend execution; metrics are limited; no progress visualization

- Screen name: Workspace Tabs
  - Purpose: switch between code editing and result/visualization views
  - File location: [frontend/lib/features/workspace/workspace_tabs.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/workspace_tabs.dart)
  - Key widgets/components: `DefaultTabController`, `TabBar`, `TabBarView`
  - Connected logic/providers/controllers: receives controller-derived state from `MainLayout`
  - Current completeness: complete for two-tab switching
  - Missing pieces: no additional workspace tabs, no persistent tab state

- Screen name: Code Editor Tab
  - Purpose: allow the user to edit the lesson starter code
  - File location: [frontend/lib/features/workspace/code_editor.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/code_editor.dart)
  - Key widgets/components: multiline `TextField`, instructional labels
  - Connected logic/providers/controllers: `updateCode`
  - Current completeness: partially complete
  - Missing pieces: no syntax highlighting, no line numbers, no compile-time validation in the editor, no save/load

- Screen name: Video/Results Tab
  - Purpose: display the result status, metrics, and generated video path
  - File location: [frontend/lib/features/workspace/video_player.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/video_player.dart)
  - Key widgets/components: status icon, run status label, status message, metric text, video path text
  - Connected logic/providers/controllers: `runStatusLabel`, `statusMessage`, `totalReward`, `averageReward`, `bestEpisodeReward`, `videoPath`
  - Current completeness: partially complete
  - Missing pieces: despite the filename, no video playback widget is present

- Screen name: Add Video Lesson Screen
  - Purpose: author or upload lesson videos
  - File location: not found
  - Key widgets/components: not found
  - Connected logic/providers/controllers: not found
  - Current completeness: not found
  - Missing pieces: entire screen and workflow

- Screen name: Coding Exercise Configuration Screen
  - Purpose: author new coding exercises or bind them to lessons
  - File location: not found as a separate screen
  - Key widgets/components: not found
  - Connected logic/providers/controllers: not found
  - Current completeness: not found as an authoring screen
  - Missing pieces: entire authoring flow

# 4. Data Models and Configuration

- Models/entities/classes found:
  - Backend lesson registry model: `LessonDefinition` dataclass in [backend/lessons.py](/Users/ultramarine/Desktop/grad_project/backend/lessons.py)
  - Frontend lesson model: `LessonDefinition` class in [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart)
  - Frontend lesson grouping model: `LessonSection` in the same file
  - Frontend response models: `ExecutionMetrics`, `ExecutionResult`, and `BackendApiException` in [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart)
  - Backend request model: `CodeSubmission` in [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py)
  - Backend validation result model: `ValidationResult` in [backend/validation/validator.py](/Users/ultramarine/Desktop/grad_project/backend/validation/validator.py)

- JSON/YAML/config schemas:
  - No authored JSON or YAML lesson schema was found.
  - The main operational JSON structure is the HTTP payload sent to `/execute`.
  - `temp_data.json` in [backend/visualization/animations/scenes/temp_data.json](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/scenes/temp_data.json) is a generated intermediary file for Manim scene rendering, not a reusable configuration source.

- Lesson/exercise/video configuration structures:
  - Lessons are configured in code, not files.
  - Frontend lesson configuration includes title, description, category, starter code, and visual badges.
  - Backend lesson configuration includes only title, function contract, and environment binding.
  - No external video catalog or exercise authoring schema was found.

- Data loading, validation, transformation, and consumption:
  - The frontend loads lesson definitions directly from in-memory constants inside `RLWorkbenchController`.
  - User code and parameters are transformed into a JSON payload by `HttpBackendApi.executeCode()`.
  - The backend validates incoming numeric fields through Pydantic and validates the code contract through `CodeValidator`.
  - Execution produces step logs, which are transformed into metrics and a generated scene/video path.
  - The frontend consumes the response JSON through `ExecutionResult.fromJson()` and displays the results in the UI.

- Sample configuration flow from model to UI or execution layer:
  - A lesson definition is constructed in [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart).
  - `LessonBrowser` renders it through `LessonCard`.
  - When selected, the controller updates the current starter code and status.
  - On `Run`, `HttpBackendApi` packages the selected lesson ID, code, and numeric parameters into JSON.
  - The backend uses [backend/lessons.py](/Users/ultramarine/Desktop/grad_project/backend/lessons.py) to identify the required function contract and environment binding.
  - After execution, the frontend maps returned JSON back into `ExecutionResult` and displays metric and video path text.

# 5. Execution Flow of the Current System

The current system starts with the Flutter application entry point in [frontend/lib/main.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/main.dart). `RLSimulationIDE` creates a `MaterialApp` whose `home` is `MainLayout`. `MainLayout` creates an `RLWorkbenchController`, which immediately provides a default lesson and starter code.

The initial user interface shows a lesson browser, a parameter panel, a run control panel, and a workspace area. The lesson browser presents three hardcoded lessons grouped by category. When the user selects a lesson, `selectLesson()` in the controller replaces the current code editor contents with the corresponding starter code string and resets metrics and status.

The user can then modify:

- learning rate
- discount factor
- exploration rate
- episode count
- run mode
- the lesson code itself

These values are held entirely in memory by `RLWorkbenchController`.

When the user presses `Run`, `RLWorkbenchController.run()` first checks whether the code editor is empty and whether hardware mode was selected. Hardware mode is rejected immediately. For simulation mode, the controller marks the UI as running and sends an HTTP request to the backend using `HttpBackendApi.executeCode()`.

On the backend, FastAPI receives the request in `POST /execute`. The backend checks the lesson ID against the backend lesson registry, creates the environment adapter, validates the submitted code contract, and then runs the lesson through `RLEngine`. The engine dynamically executes the submitted code, identifies the lesson function, and performs one of the supported lesson flows over the FrozenLake environment. Each step is logged with the event logger.

After the episode loop completes, the backend passes the latest episode log to `VisualizationController`. The controller writes a temporary JSON data file, generates a Python Manim scene file, invokes Manim as a subprocess, and attempts to return the expected MP4 path. The API then returns a JSON object containing lesson metadata, aggregate reward metrics, and a video path string if rendering succeeded.

The frontend receives the response, deserializes it into `ExecutionResult`, updates the controller state, and rebuilds the UI. The run panel shows current counters and total reward. The video/results tab displays:

- run status
- backend message
- total reward
- average reward
- best episode reward
- video path

The current flow breaks or remains incomplete in the following places:

- no screen-level navigation exists
- no backend cancellation exists for `Stop`
- no actual video playback exists in the frontend
- hardware mode is explicitly blocked
- lessons are not loaded dynamically from the backend even though `/lessons` exists
- algorithm templates under `backend/rl_engine/templates` remain placeholders
- timeout or infinite-loop protection is not implemented

# 6. External Libraries and Their Actual Use

- Flutter:
  - Used for the entire frontend widget tree, layout, text input, tabs, buttons, and desktop app shell in [frontend/lib](/Users/ultramarine/Desktop/grad_project/frontend/lib).

- `http` package for Flutter:
  - Used in [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart) to send a `POST /execute` request to the backend and parse returned JSON.

- FastAPI:
  - Used in [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py) to declare the service routes and return HTTP responses.

- Pydantic:
  - Used in the same backend API file to define the `CodeSubmission` request model and numeric constraints.

- Gymnasium:
  - Used in [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py) to instantiate and interact with `FrozenLake-v1`.

- NumPy:
  - Used in [backend/logger/event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/logger/event_logger.py) only for JSON encoding of NumPy types.

- Manim:
  - Used in [backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py) as an external subprocess target for rendering MP4 animations.

- `requests`:
  - Used only in [backend/test_execution.py](/Users/ultramarine/Desktop/grad_project/backend/test_execution.py) for a manual backend smoke script.

- `unittest`:
  - Used in backend tests under [backend/tests](/Users/ultramarine/Desktop/grad_project/backend/tests).

- `flutter_test`:
  - Used in [frontend/test/widget_test.dart](/Users/ultramarine/Desktop/grad_project/frontend/test/widget_test.dart).

- `pytest`:
  - Listed in [backend/requirements.txt](/Users/ultramarine/Desktop/grad_project/backend/requirements.txt), but no pytest-style test suite was found.

# 7. Gaps Relevant to Thesis Chapter 4

- The current implementation lacks any executable hardware integration, despite hardware-related expectations in the project context.
- The frontend contains no real video playback; it only shows the returned filesystem path.
- Lessons are hardcoded on both frontend and backend and are not backed by a shared configuration source.
- The RL engine supports only one Gymnasium environment and a small lesson set.
- The algorithm templates in the backend remain placeholders and do not constitute a mature algorithm library.
- Execution safety is limited. There is no timeout watchdog, no secure sandboxing, and no backend-side stop mechanism.
- The frontend has no multi-page navigation, no lesson creation workflow, no video lesson upload workflow, and no exercise authoring UI.
- Testing is limited to small unit tests and one widget test with a fake backend.
- Research-oriented data collection such as code edit history, quiz data, or N-Gain analytics is absent.
- Some platform support exists only as generated scaffold files and not as documented, tested product features.

# 8. Thesis-Ready Chapter Mapping

## 4.1 Hardware Implementation

The codebase currently does not provide an executable hardware implementation. No ESP32 firmware, Bluetooth communication stack, robot control layer, sensor ingestion module, or physical device protocol was found. The only hardware-related element in the current implementation is a frontend `Hardware` run mode option and lesson flags indicating hardware availability, but the controller explicitly rejects hardware execution. Therefore, this section can only state that hardware support was planned in the interface but not implemented in the current repository state.

## 4.2 Software Implementation

The codebase currently implements a software prototype consisting of:

- a Flutter frontend desktop application
- a central client-side state controller for lesson selection, code editing, parameter editing, and result display
- a FastAPI backend with routes for status, lesson listing, and execution
- a lesson registry covering three tabular RL lesson types
- a Gymnasium-based execution pipeline using FrozenLake
- a validation layer that checks code contract conformance
- an event logging layer that records step-by-step RL transitions
- a Manim-based animation pipeline that converts logged steps into simple MP4 visualizations

These components form the strongest basis for the software implementation portion of the thesis.

## 4.3 System Integration

The current implementation includes real integration at the following points:

- Flutter frontend to FastAPI backend through local HTTP
- backend lesson routing to a Gymnasium environment
- backend execution logging to a Manim rendering pipeline
- backend response metrics back into the frontend state and UI

The integrations that remain incomplete are:

- frontend video playback of generated media
- dynamic lesson synchronization between frontend and backend
- hardware pathway integration
- execution cancellation and watchdog handling
- persistent storage and analytics integration

## 4.4 Summary

The current repository implements a functional educational RL prototype centered on a local Flutter-to-FastAPI execution workflow. The software implementation is sufficient to demonstrate lesson selection, code submission, parameter configuration, RL environment execution, metric generation, and basic animation rendering. However, several planned capabilities remain incomplete, especially hardware support, richer visualization semantics, persistent data management, safety controls, and pedagogical evaluation modules.

# 9. Final Completion Matrix

| Component | Status | Evidence files | Can be claimed in thesis? | Notes |
|---|---|---|---|---|
| Flutter client shell | Partially implemented | [frontend/lib/main.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/main.dart), [frontend/lib/layout/main_layout.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/layout/main_layout.dart) | Yes | Single-screen application only |
| Lesson browser UI | Fully implemented | [frontend/lib/features/lessons/lesson_browser.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/lessons/lesson_browser.dart), [frontend/lib/features/lessons/lesson_card.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/lessons/lesson_card.dart) | Yes | Hardcoded lessons only |
| Parameter control UI | Partially implemented | [frontend/lib/features/controls/parameters_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/parameters_panel.dart) | Yes | Runtime parameters only |
| Run control and status UI | Partially implemented | [frontend/lib/features/controls/run_panel.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/controls/run_panel.dart) | Yes | Stop is not a real cancellation |
| Code editing interface | Partially implemented | [frontend/lib/features/workspace/code_editor.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/code_editor.dart) | Yes with limitation | Plain text editor, no advanced IDE features |
| Video/results interface | Partially implemented | [frontend/lib/features/workspace/video_player.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/features/workspace/video_player.dart) | Yes with limitation | Displays metrics and path, not video playback |
| Frontend-backend HTTP integration | Implemented | [frontend/lib/core/backend_api.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/backend_api.dart), [backend/api_gateway/base.py](/Users/ultramarine/Desktop/grad_project/backend/api_gateway/base.py) | Yes | Core local API bridge exists |
| Lesson registry | Partially implemented | [frontend/lib/core/workbench_state.dart](/Users/ultramarine/Desktop/grad_project/frontend/lib/core/workbench_state.dart), [backend/lessons.py](/Users/ultramarine/Desktop/grad_project/backend/lessons.py) | Yes with limitation | Duplicated and hardcoded |
| RL execution engine | Partially implemented | [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py) | Yes with limitation | Supports limited flows and one environment |
| Gymnasium environment integration | Partially implemented | [backend/rl_engine/engine.py](/Users/ultramarine/Desktop/grad_project/backend/rl_engine/engine.py) | Yes with limitation | FrozenLake only |
| Code validation | Partially implemented | [backend/validation/validator.py](/Users/ultramarine/Desktop/grad_project/backend/validation/validator.py) | Yes with limitation | Contract checking only |
| Step logging | Fully implemented | [backend/logger/event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/logger/event_logger.py) | Yes | In-memory logging with optional JSON save |
| Platform build scaffolding | Partially implemented | [frontend/macos/Runner/DebugProfile.entitlements](/Users/ultramarine/Desktop/grad_project/frontend/macos/Runner/DebugProfile.entitlements), [frontend/macos/Runner/Release.entitlements](/Users/ultramarine/Desktop/grad_project/frontend/macos/Runner/Release.entitlements), [frontend/macos/Runner/Configs/AppInfo.xcconfig](/Users/ultramarine/Desktop/grad_project/frontend/macos/Runner/Configs/AppInfo.xcconfig), [frontend/android/app/src/main/AndroidManifest.xml](/Users/ultramarine/Desktop/grad_project/frontend/android/app/src/main/AndroidManifest.xml), [frontend/ios/Runner/Info.plist](/Users/ultramarine/Desktop/grad_project/frontend/ios/Runner/Info.plist) | Yes with limitation | macOS networking is configured, while Android and iOS remain mostly generated scaffolds |
| Manim animation pipeline | Partially implemented | [backend/visualization/controller.py](/Users/ultramarine/Desktop/grad_project/backend/visualization/controller.py) | Yes with limitation | Simple generic animation pipeline |
| Generated animation outputs | Implemented evidence artifact | [backend/visualization/animations/videos/dp_policy_eval_scene/480p15/RLEpisodeScene.mp4](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/videos/dp_policy_eval_scene/480p15/RLEpisodeScene.mp4), [backend/visualization/animations/videos/td_q_learning_scene/480p15/RLEpisodeScene.mp4](/Users/ultramarine/Desktop/grad_project/backend/visualization/animations/videos/td_q_learning_scene/480p15/RLEpisodeScene.mp4) | Yes with limitation | Demonstrates rendered output, not feature richness |
| Test coverage | Partially implemented | [backend/tests/test_validator.py](/Users/ultramarine/Desktop/grad_project/backend/tests/test_validator.py), [backend/tests/test_event_logger.py](/Users/ultramarine/Desktop/grad_project/backend/tests/test_event_logger.py), [frontend/test/widget_test.dart](/Users/ultramarine/Desktop/grad_project/frontend/test/widget_test.dart) | Yes with limitation | Narrow scope, no end-to-end tests |
| Persistence/database layer | Not found | No database files or persistence modules found | No | Only transient files and in-memory state |
| Lesson authoring / video authoring | Not found | No dedicated creation screens or storage layer found | No | Planned functionality not implemented |
| Hardware / BLE / robot integration | Not found | No executable hardware modules found | No | UI placeholder only |
| Quiz / N-Gain / pedagogy analytics | Not found | No quiz or analytics implementation found | No | Not present in current codebase |
