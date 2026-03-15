import 'dart:async';

import 'package:flutter/material.dart';

import 'backend_api.dart';

enum RunMode { simulation, hardware }

enum RunStatus { idle, running, success, failed, stopped }

@immutable
class LessonDefinition {
  final String id;
  final String title;
  final String description;
  final String category;
  final String starterCode;
  final bool hasVideo;
  final bool hasHardware;

  const LessonDefinition({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.starterCode,
    this.hasVideo = true,
    this.hasHardware = false,
  });
}

class LessonSection {
  final String title;
  final List<LessonDefinition> lessons;

  const LessonSection({
    required this.title,
    required this.lessons,
  });
}

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
            for action, action_prob in enumerate(policy[state]):
                for transition_prob, next_state, reward, done in env.P[state][action]:
                    future = 0.0 if done else V[next_state]
                    new_value += action_prob * transition_prob * (reward + gamma * future)
            V[state] = new_value
            delta = max(delta, abs(old_value - new_value))
    return V
''',
              ),
            ],
          ),
          LessonSection(
            title: 'Monte Carlo Methods',
            lessons: [
              LessonDefinition(
                id: 'mc_first_visit',
                title: 'MC Prediction',
                description:
                    'Estimate value functions from complete episodes with first-visit returns.',
                category: 'Monte Carlo Methods',
                starterCode: '''
def mc_first_visit_prediction(episode, V, returns, gamma=0.9):
    visited_states = set()
    for index, (state, _action, _reward) in enumerate(episode):
        if state in visited_states:
            continue
        visited_states.add(state)
        G = 0.0
        discount = 1.0
        for _next_state, _next_action, reward in episode[index:]:
            G += discount * reward
            discount *= gamma
        returns[state].append(G)
        V[state] = sum(returns[state]) / len(returns[state])
    return V
''',
                hasHardware: true,
              ),
            ],
          ),
          LessonSection(
            title: 'Temporal Difference',
            lessons: [
              LessonDefinition(
                id: 'td_q_learning',
                title: 'Q-Learning',
                description:
                    'Update a tabular action-value function from one-step TD targets.',
                category: 'Temporal Difference',
                starterCode: '''
def q_learning_update(Q, state, action, reward, next_state, alpha, gamma):
    best_next_value = max(Q[next_state])
    td_target = reward + gamma * best_next_value
    Q[state][action] = Q[state][action] + alpha * (td_target - Q[state][action])
    return Q
''',
                hasHardware: true,
              ),
            ],
          ),
        ],
        _learningRate = 0.10,
        _discountFactor = 0.95,
        _explorationRate = 0.20,
        _episodeCount = 5,
        _runMode = RunMode.simulation,
        _runStatus = RunStatus.idle,
        _currentEpisode = 0,
        _currentStep = 0,
        _totalReward = 0.0,
        _averageReward = 0.0,
        _bestEpisodeReward = 0.0,
        _statusMessage = 'Ready to run.' {
    _selectedLesson = _sections.first.lessons.first;
    _code = _selectedLesson.starterCode;
    _statusMessage = 'Ready to run ${_selectedLesson.title}.';
  }

  final BackendApi _api;
  final List<LessonSection> _sections;
  late LessonDefinition _selectedLesson;
  late String _code;
  double _learningRate;
  double _discountFactor;
  double _explorationRate;
  int _episodeCount;
  RunMode _runMode;
  RunStatus _runStatus;
  int _currentEpisode;
  int _currentStep;
  double _totalReward;
  double _averageReward;
  double _bestEpisodeReward;
  String _statusMessage;
  String _videoPath = '';
  String? _activeTaskId;
  List<ExecutionTestCaseResult> _testResults = const [];

  List<LessonSection> get sections => _sections;
  LessonDefinition get selectedLesson => _selectedLesson;
  String get code => _code;
  double get learningRate => _learningRate;
  double get discountFactor => _discountFactor;
  double get explorationRate => _explorationRate;
  int get episodeCount => _episodeCount;
  RunMode get runMode => _runMode;
  RunStatus get runStatus => _runStatus;
  int get currentEpisode => _currentEpisode;
  int get currentStep => _currentStep;
  double get totalReward => _totalReward;
  double get averageReward => _averageReward;
  double get bestEpisodeReward => _bestEpisodeReward;
  String get statusMessage => _statusMessage;
  String get videoPath => _videoPath;
  List<ExecutionTestCaseResult> get testResults => _testResults;

  String get connectionLabel =>
      _runMode == RunMode.simulation ? 'Simulation' : 'Hardware';

  String get runStatusLabel {
    switch (_runStatus) {
      case RunStatus.idle:
        return 'Idle';
      case RunStatus.running:
        return 'Running';
      case RunStatus.success:
        return 'Complete';
      case RunStatus.failed:
        return 'Failed';
      case RunStatus.stopped:
        return 'Stopped';
    }
  }

  void selectLesson(LessonDefinition lesson) {
    if (_selectedLesson.id == lesson.id) {
      return;
    }

    _selectedLesson = lesson;
    _code = lesson.starterCode;
    _resetProgress('Ready to run ${lesson.title}.');
    notifyListeners();
  }

  void updateCode(String value) {
    _code = value;
    notifyListeners();
  }

  void updateLearningRate(double value) {
    _learningRate = value;
    notifyListeners();
  }

  void updateDiscountFactor(double value) {
    _discountFactor = value;
    notifyListeners();
  }

  void updateExplorationRate(double value) {
    _explorationRate = value;
    notifyListeners();
  }

  void updateEpisodeCount(String value) {
    final parsed = int.tryParse(value);
    if (parsed == null || parsed < 1) {
      return;
    }

    _episodeCount = parsed;
    notifyListeners();
  }

  void updateRunMode(RunMode? mode) {
    if (mode == null) {
      return;
    }

    _runMode = mode;
    notifyListeners();
  }

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
    _testResults = const [];
    _statusMessage = 'Running ${_selectedLesson.title} against the backend...';
    notifyListeners();

    try {
      final task = await _api.submitCode(
        lessonId: _selectedLesson.id,
        code: _code,
        learningRate: _learningRate,
        discountFactor: _discountFactor,
        explorationRate: _explorationRate,
        episodeCount: _episodeCount,
      );
      _activeTaskId = task.taskId;
      _statusMessage =
          'Queued ${_selectedLesson.title}. Waiting for task ${task.taskId}.';
      notifyListeners();

      await _pollUntilComplete(task.taskId);
    } on BackendApiException catch (error) {
      _runStatus = RunStatus.failed;
      _activeTaskId = null;
      _resetExecutionDetails();
      _testResults = error.testResults;
      _statusMessage = error.message;
    } catch (_) {
      _runStatus = RunStatus.failed;
      _activeTaskId = null;
      _resetExecutionDetails();
      _testResults = const [];
      _statusMessage =
          'The frontend could not reach the backend. Check that FastAPI is running on $defaultBackendBaseUrl.';
    }

    notifyListeners();
  }

  void stop() {
    if (_runStatus == RunStatus.idle) {
      return;
    }

    _activeTaskId = null;
    _runStatus = RunStatus.stopped;
    _statusMessage =
        'Polling stopped in the UI. The current backend task is still running server-side.';
    notifyListeners();
  }

  void reset() {
    _activeTaskId = null;
    _code = _selectedLesson.starterCode;
    _resetProgress('Reset ${_selectedLesson.title} to its starter template.');
    notifyListeners();
  }

  void _resetProgress(String message) {
    _runStatus = RunStatus.idle;
    _currentEpisode = 0;
    _currentStep = 0;
    _resetExecutionDetails();
    _statusMessage = message;
  }

  void _resetExecutionDetails() {
    _totalReward = 0.0;
    _averageReward = 0.0;
    _bestEpisodeReward = 0.0;
    _videoPath = '';
    _testResults = const [];
  }

  int _nonEmptyLineCount(String source) {
    return source.split('\n').where((line) => line.trim().isNotEmpty).length;
  }

  Future<void> _pollUntilComplete(String taskId) async {
    while (_activeTaskId == taskId && _runStatus == RunStatus.running) {
      final snapshot = await _api.getTaskStatus(taskId);

      if (_activeTaskId != taskId || _runStatus != RunStatus.running) {
        return;
      }

      switch (snapshot.status) {
        case ExecutionTaskStatus.queued:
          _statusMessage = 'Task $taskId is queued on the backend.';
          notifyListeners();
          break;
        case ExecutionTaskStatus.running:
          _statusMessage = 'Task $taskId is running on the backend.';
          notifyListeners();
          break;
        case ExecutionTaskStatus.succeeded:
          final result = snapshot.result;
          if (result == null) {
            throw const BackendApiException(
              'Backend completed a task without returning a result.',
            );
          }

          _activeTaskId = null;
          _runStatus = RunStatus.success;
          _currentEpisode = result.metrics.episodesCompleted;
          _currentStep = result.metrics.stepsRecorded;
          _totalReward = result.metrics.totalReward;
          _averageReward = result.metrics.averageReward;
          _bestEpisodeReward = result.metrics.bestEpisodeReward;
          _videoPath = result.videoPath;
          _testResults = result.testResults;
          _statusMessage = result.visualizationReady
              ? '${result.message} Video ready for ${result.lessonTitle}.'
              : '${result.message} Metrics are ready, but no video was generated.';
          notifyListeners();
          return;
        case ExecutionTaskStatus.failed:
          _activeTaskId = null;
          _runStatus = RunStatus.failed;
          _resetExecutionDetails();
          _testResults = snapshot.testResults;
          _statusMessage = snapshot.errorMessage ?? 'Execution task failed.';
          notifyListeners();
          return;
      }

      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }
}
