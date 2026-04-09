import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';

class _FakeBackendApi extends BackendApi {
  _FakeBackendApi({
    this.shouldFailRun = false,
  });

  final bool shouldFailRun;
  int _pollCount = 0;
  int _workspacePollCount = 0;

  @override
  Future<LearnerDashboard> signIn({
    required String displayName,
    required String password,
    String? firebaseIdToken,
  }) async {
    if (firebaseIdToken != null) {}
    if (password == 'wrong') {
      throw const BackendApiException('Invalid display name or password.');
    }

    return LearnerDashboard(
      student: LearnerProfile(id: 'student-1', displayName: displayName),
      progress: const LearnerProgress.empty(),
    );
  }

  @override
  Future<LearnerDashboard> getDashboard({
    required String studentId,
  }) async {
    return LearnerDashboard(
      student: LearnerProfile(id: studentId, displayName: 'Maya'),
      progress: const LearnerProgress.empty(),
    );
  }

  @override
  Future<QuizSessionData> startQuiz({
    required String studentId,
    required QuizPhase phase,
  }) async {
    throw UnimplementedError();
  }

  @override
  Future<QuizAttemptSummary> submitQuiz({
    required String studentId,
    required String sessionId,
    required Map<String, int> answers,
  }) async {
    throw UnimplementedError();
  }

  @override
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    String? studentId,
  }) async {
    return const SubmittedExecutionTask(
      taskId: 'task-1',
      status: ExecutionTaskStatus.queued,
    );
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    _pollCount += 1;
    if (shouldFailRun) {
      return const ExecutionTaskSnapshot(
        taskId: 'task-1',
        status: ExecutionTaskStatus.failed,
        errorMessage: 'Code validation failed.',
      );
    }

    if (_pollCount == 1) {
      return const ExecutionTaskSnapshot(
        taskId: 'task-1',
        status: ExecutionTaskStatus.queued,
      );
    }
    return const ExecutionTaskSnapshot(
      taskId: 'task-1',
      status: ExecutionTaskStatus.succeeded,
      result: ExecutionResult(
        message: 'Execution pipeline completed.',
        lessonTitle: 'Policy Evaluation',
        videoPath: '/tmp/demo.mp4',
        visualizationReady: true,
        metrics: ExecutionMetrics(
          episodesCompleted: 3,
          stepsRecorded: 12,
          totalReward: 2.0,
          averageReward: 0.66,
          bestEpisodeReward: 1.0,
        ),
        testResults: [],
        stepTrace: [],
      ),
    );
  }

  @override
  Future<NGainMetricsExport> exportNGainMetrics() async {
    throw UnimplementedError();
  }

  @override
  Future<WorkspaceSessionData> createWorkspaceSession({
    required String lessonId,
  }) async {
    return WorkspaceSessionData(
      sessionId: 'workspace-$lessonId',
      lessonId: lessonId,
      visibleFiles: const ['script.py'],
      consoleReady: true,
    );
  }

  @override
  Future<WorkspaceHealthData> getWorkspaceHealth() async {
    return const WorkspaceHealthData(
      ready: true,
      workerReachable: true,
      dockerCliAvailable: true,
      dockerDaemonReachable: true,
      runtimeMode: 'docker',
      message: 'Workspace runtime is ready.',
      issues: [],
    );
  }

  @override
  Future<WorkspaceSessionData> getWorkspaceSession(String sessionId) async {
    return WorkspaceSessionData(
      sessionId: sessionId,
      lessonId: 'dp_policy_eval',
      visibleFiles: const ['script.py'],
      consoleReady: true,
    );
  }

  @override
  Future<WorkspaceFileSnapshot> getWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
  }) async {
    return const WorkspaceFileSnapshot(
      path: 'script.py',
      content: 'print("workspace")\n',
      version: 2,
      diagnostics: [],
    );
  }

  @override
  Future<WorkspaceFileSnapshot> updateWorkspaceFile({
    required String sessionId,
    String path = 'script.py',
    required String content,
  }) async {
    return WorkspaceFileSnapshot(
      path: path,
      content: content,
      version: 3,
      diagnostics: const [],
    );
  }

  @override
  Future<WorkspaceRunData> runWorkspaceScript({
    required String sessionId,
  }) async {
    return const WorkspaceRunData(
      runId: 'run-1',
      status: 'running',
      exitCode: null,
      startedAt: '2026-01-01T00:00:00Z',
      finishedAt: null,
    );
  }

  @override
  Future<WorkspaceRunData> getWorkspaceRun({
    required String sessionId,
    required String runId,
  }) async {
    _workspacePollCount += 1;
    return WorkspaceRunData(
      runId: runId,
      status: _workspacePollCount > 1 ? 'completed' : 'running',
      exitCode: _workspacePollCount > 1 ? 0 : null,
      startedAt: '2026-01-01T00:00:00Z',
      finishedAt: _workspacePollCount > 1 ? '2026-01-01T00:00:01Z' : null,
    );
  }

  @override
  String workspaceEditorShellUrl(String sessionId) {
    return 'http://127.0.0.1:8000/workspace/editor-shell?session_id=$sessionId';
  }
}

void main() {
  test('cubit sign-in then sign-out updates auth state', () async {
    final cubit = RLWorkbenchCubit(api: _FakeBackendApi());

    await cubit.signIn('Maya', 'Password123!');
    expect(cubit.state.learner?.displayName, 'Maya');
    expect(cubit.state.homeMessage, contains('Signed in as Maya.'));

    cubit.signOut();
    expect(cubit.state.learner, isNull);
    expect(cubit.state.homeMessage, contains('Signed out.'));

    await cubit.close();
  });

  test('cubit workspace run lifecycle reaches terminal status', () async {
    final cubit = RLWorkbenchCubit(api: _FakeBackendApi());

    cubit.openLesson(cubit.state.selectedLesson);
    await Future<void>.delayed(const Duration(milliseconds: 20));
    await cubit.run();

    expect(cubit.state.workspaceSessionId, isNotNull);
    expect(cubit.state.activeRunId, isNull);
    expect(cubit.state.statusMessage, contains('Workspace run completed.'));

    await cubit.close();
  });

  test('cubit submit lifecycle handles failure state', () async {
    final cubit = RLWorkbenchCubit(api: _FakeBackendApi(shouldFailRun: true));

    await cubit.submit();

    expect(cubit.state.runStatus, RunStatus.failed);
    expect(cubit.state.statusMessage, contains('Code validation failed.'));

    await cubit.close();
  });
}
