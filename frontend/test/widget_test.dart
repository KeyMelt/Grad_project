import 'package:flutter_test/flutter_test.dart';
import 'package:rl_ide/core/backend_api.dart';
import 'package:rl_ide/core/workbench_state.dart';
import 'package:rl_ide/layout/main_layout.dart';
import 'package:rl_ide/main.dart';

class FakeBackendApi extends BackendApi {
  @override
  Future<SubmittedExecutionTask> submitCode({
    required String lessonId,
    required String code,
    required double learningRate,
    required double discountFactor,
    required double explorationRate,
    required int episodeCount,
  }) async {
    return const SubmittedExecutionTask(
      taskId: 'task-123',
      status: ExecutionTaskStatus.queued,
    );
  }

  @override
  Future<ExecutionTaskSnapshot> getTaskStatus(String taskId) async {
    return const ExecutionTaskSnapshot(
      taskId: 'task-123',
      status: ExecutionTaskStatus.succeeded,
      result: ExecutionResult(
        message: 'Execution pipeline completed.',
        lessonTitle: 'Monte Carlo: First-Visit Prediction',
        videoPath: '/tmp/mc_first_visit.mp4',
        visualizationReady: true,
        metrics: ExecutionMetrics(
          episodesCompleted: 5,
          stepsRecorded: 17,
          totalReward: 3,
          averageReward: 0.6,
          bestEpisodeReward: 1,
        ),
        testResults: [
          ExecutionTestCaseResult(
            name: 'mc_first_visit_returns',
            passed: true,
            message: 'Computes first-visit returns over a short episode.',
            expected: 'V[0] = 3.0 and V[1] = 2.0',
            actual: 'V[0] = 3.0 and V[1] = 2.0',
          ),
        ],
      ),
    );
  }
}

void main() {
  testWidgets('App runs against backend client and renders returned metrics', (
    WidgetTester tester,
  ) async {
    final controller = RLWorkbenchController(api: FakeBackendApi());

    await tester.pumpWidget(
      RLSimulationIDE(
        home: MainLayout(controller: controller),
      ),
    );

    expect(find.text('RL_IDE'), findsOneWidget);

    await tester.tap(find.text('MC Prediction'));
    await tester.pumpAndSettle();

    expect(find.text('Visualization: MC Prediction'), findsOneWidget);

    await tester.ensureVisible(find.text('Run'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Run'));
    await tester.pumpAndSettle();

    expect(find.text('Complete'), findsWidgets);
    expect(find.textContaining('Video ready'), findsWidgets);
    expect(find.text('3.0'), findsOneWidget);
    expect(find.textContaining('/tmp/mc_first_visit.mp4'), findsOneWidget);
    expect(find.text('Lesson Sample Tests'), findsOneWidget);
    expect(find.text('mc_first_visit_returns'), findsOneWidget);
  });
}
