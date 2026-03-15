# System Architecture

## Tech Stack
* **Frontend**: Flutter (Desktop build only)
* **Backend**: Python 3 (Microservices via FastAPI)
* **Core Libraries**: Gymnasium, Manim

## Core Subsystems
1. **LessonManager & API Gateway**: Handles frontend requests, serves lesson configurations, and routes execution commands.
2. **RLEngine & EnvironmentAdapter**: Manages Gymnasium environments and core RL logic (DP, MC, TD).
3. **CodeValidator**: Unit testing mechanism for code validation.
4. **EventLogger**: Logs intermediate RL steps (state, action, reward, next state, value updates).
5. **VisualizationController**: Generates Manim animations from EventLogger data.

## Execution Flow
1. Load lesson configuration and create Gymnasium environment.
2. Retrieve student code -> run basic unit tests via CodeValidator.
3. On failure -> return error to Flutter IDE and halt.
4. On success -> inject code into RLEngine, clear EventLogger.
5. Run episode loop (step/action/observe/update/log).
6. Pass EventLogger data to VisualizationController to build Manim MP4.
7. Return animation file path and learning metrics to Flutter IDE.

_Detailed mapping of RL logs to Manim visualization properties will be fleshed out soon._
