enum ReplayState {
  idle('idle'),
  queued('queued'),
  rendering('rendering'),
  ready('ready'),
  failed('failed'),
  timeout('timeout'),
  unavailable('unavailable');

  const ReplayState(this.value);

  final String value;
}

class ReplayStateSnapshot {
  final ReplayState state;
  final String rawStatus;
  final String videoPath;
  final String? error;

  const ReplayStateSnapshot({
    required this.state,
    required this.rawStatus,
    required this.videoPath,
    this.error,
  });

  String get statusId => state.value;
  bool get hasVideo => videoPath.isNotEmpty;
  bool get hasStatusOrError =>
      hasVideo || state != ReplayState.idle || (error?.isNotEmpty ?? false);

  factory ReplayStateSnapshot.resolve({
    String rawStatus = '',
    String videoPath = '',
    String? error,
  }) {
    final normalizedPath = videoPath.trim();
    final normalizedStatus = rawStatus.trim().toLowerCase();
    if (normalizedPath.isNotEmpty) {
      return ReplayStateSnapshot(
        state: ReplayState.ready,
        rawStatus: normalizedStatus,
        videoPath: normalizedPath,
        error: error,
      );
    }

    final state = switch (normalizedStatus) {
      'idle' => ReplayState.idle,
      'queued' => ReplayState.queued,
      'rendering' => ReplayState.rendering,
      'ready' => ReplayState.unavailable,
      'failed' => ReplayState.failed,
      'timeout' => ReplayState.timeout,
      'unavailable' => ReplayState.unavailable,
      'complete' => ReplayState.unavailable,
      _ when error?.isNotEmpty ?? false => ReplayState.failed,
      _ => ReplayState.unavailable,
    };

    return ReplayStateSnapshot(
      state: state,
      rawStatus: normalizedStatus,
      videoPath: normalizedPath,
      error: error,
    );
  }
}
