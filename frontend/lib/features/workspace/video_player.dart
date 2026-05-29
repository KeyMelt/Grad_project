import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';

import '../../core/backend_api.dart';
import '../../core/theme.dart';
import '../../core/workbench_state.dart';

// ── VTT caption model ────────────────────────────────────────────────────────

class _VttCue {
  final Duration start;
  final Duration end;
  final String text;

  const _VttCue(this.start, this.end, this.text);
}

// ── VTT parser ───────────────────────────────────────────────────────────────

Duration _parseVttTimestamp(String ts) {
  // Accepts HH:MM:SS.mmm or MM:SS.mmm
  final parts = ts.trim().split(':');
  int hours = 0, minutes = 0;
  double seconds = 0;
  if (parts.length == 3) {
    hours = int.tryParse(parts[0]) ?? 0;
    minutes = int.tryParse(parts[1]) ?? 0;
    seconds = double.tryParse(parts[2]) ?? 0;
  } else if (parts.length == 2) {
    minutes = int.tryParse(parts[0]) ?? 0;
    seconds = double.tryParse(parts[1]) ?? 0;
  }
  final ms = ((hours * 3600 + minutes * 60 + seconds) * 1000).round();
  return Duration(milliseconds: ms);
}

List<_VttCue> _parseVttBody(String vttText) {
  final cues = <_VttCue>[];
  // Split into blocks by blank lines
  final blocks = vttText.replaceAll('\r\n', '\n').split(RegExp(r'\n{2,}'));
  for (final block in blocks) {
    final lines = block.trim().split('\n');
    // Find the cue timing line (contains ' --> ')
    int timingIndex = -1;
    for (int i = 0; i < lines.length; i++) {
      if (lines[i].contains(' --> ')) {
        timingIndex = i;
        break;
      }
    }
    if (timingIndex < 0) continue;

    final timingParts = lines[timingIndex].split(' --> ');
    if (timingParts.length < 2) continue;

    final start = _parseVttTimestamp(timingParts[0].trim());
    // Strip cue settings (e.g. "align:start position:10%") from end timestamp
    final endRaw = timingParts[1].trim().split(RegExp(r'\s+'))[0];
    final end = _parseVttTimestamp(endRaw);

    // Text lines follow the timing line
    final textLines = lines.sublist(timingIndex + 1);
    if (textLines.isEmpty) continue;

    final text =
        textLines.map((l) => l.trim()).where((l) => l.isNotEmpty).join('\n');
    if (text.isNotEmpty) {
      cues.add(_VttCue(start, end, text));
    }
  }
  return cues;
}

// ── Widget ───────────────────────────────────────────────────────────────────

class VideoPlayerTab extends StatefulWidget {
  final LessonDefinition lesson;
  final ValueChanged<Map<String, dynamic>>? onSessionEnded;

  const VideoPlayerTab({
    super.key,
    required this.lesson,
    this.onSessionEnded,
  });

  @override
  State<VideoPlayerTab> createState() => _VideoPlayerTabState();
}

class _VideoPlayerTabState extends State<VideoPlayerTab>
    with AutomaticKeepAliveClientMixin {
  VideoPlayerController? _controller;
  bool _isLoading = false;

  // Caption state
  List<_VttCue> _captions = const [];
  bool _captionsEnabled = false;
  bool _captionsAvailable = false;

  // Telemetry
  DateTime _sessionStartedAtUtc = DateTime.now().toUtc();
  DateTime? _playStartedAtUtc;
  Duration _watchDuration = Duration.zero;
  Duration _maxPosition = Duration.zero;
  Duration _lastPosition = Duration.zero;
  int _seekBackCount = 0;
  int _replayCount = 0;
  bool _completedOnce = false;
  bool _sessionReported = false;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _initializeVideo();
  }

  @override
  void didUpdateWidget(covariant VideoPlayerTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.lesson.conceptVideo.effectiveStreamPath !=
        widget.lesson.conceptVideo.effectiveStreamPath) {
      _emitSessionTelemetry();
      _disposeController();
      _resetSessionTelemetry();
      _resetCaptions();
      _initializeVideo();
    }
  }

  @override
  void dispose() {
    _emitSessionTelemetry();
    _disposeController();
    super.dispose();
  }

  // ── Initialisation ──────────────────────────────────────────────────────────

  Future<void> _initializeVideo() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final controller = await _buildBackendVideoController(
        widget.lesson.conceptVideo.effectiveStreamPath,
      );
      if (!mounted) {
        await controller.dispose();
        return;
      }
      setState(() {
        _controller = controller;
        _isLoading = false;
      });
    } catch (error, stackTrace) {
      if (!mounted) return;
      _logVideoError(error, stackTrace);
      setState(() {
        _isLoading = false;
      });
    }

    // Load captions after video; failure is silent.
    _loadCaptions();
  }

  Future<VideoPlayerController> _buildBackendVideoController(
    String streamPath,
  ) async {
    if (streamPath.trim().isEmpty) {
      throw StateError('No concept video path is configured.');
    }
    final controller = VideoPlayerController.networkUrl(
      _resolveBackendUri(streamPath),
    );
    await controller.initialize().timeout(const Duration(seconds: 45));
    await controller.setLooping(false);
    controller.addListener(_onControllerChanged);
    return controller;
  }

  // ── Captions ────────────────────────────────────────────────────────────────

  Future<void> _loadCaptions() async {
    final captionPath = widget.lesson.conceptVideo.captionPath;
    if (captionPath.isEmpty) return;

    try {
      final uri = _resolveBackendUri(captionPath);
      final response = await http.get(uri).timeout(const Duration(seconds: 15));
      if (response.statusCode != 200) return;

      final cues = _parseVttBody(response.body);
      if (!mounted) return;
      setState(() {
        _captions = cues;
        _captionsAvailable = cues.isNotEmpty;
        _captionsEnabled = cues.isNotEmpty;
      });
    } catch (_) {
      // Captions are best-effort — a missing file is not an error.
    }
  }

  void _resetCaptions() {
    _captions = const [];
    _captionsEnabled = false;
    _captionsAvailable = false;
  }

  void _toggleCaptions() {
    if (!_captionsAvailable) return;
    setState(() => _captionsEnabled = !_captionsEnabled);
  }

  String? _activeCaptionText(Duration position) {
    if (!_captionsEnabled || _captions.isEmpty) return null;
    for (final cue in _captions) {
      if (position >= cue.start && position <= cue.end) return cue.text;
    }
    return null;
  }

  // ── Seek ────────────────────────────────────────────────────────────────────

  Future<void> _seekRelative(Duration delta) async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) return;
    final target = controller.value.position + delta;
    final Duration clamped;
    if (target < Duration.zero) {
      clamped = Duration.zero;
    } else if (target > controller.value.duration) {
      clamped = controller.value.duration;
    } else {
      clamped = target;
    }
    await controller.seekTo(clamped);
    if (mounted) setState(() {});
  }

  // ── Playback ─────────────────────────────────────────────────────────────────

  Future<void> _togglePlayback() async {
    final controller = _controller;
    if (controller == null) return;

    if (controller.value.isPlaying) {
      await controller.pause();
    } else {
      final duration = controller.value.duration;
      final nearEnd = duration.inMilliseconds > 0 &&
          duration - controller.value.position <= const Duration(seconds: 1);
      if (_completedOnce &&
          (nearEnd || controller.value.position.inSeconds <= 1)) {
        _replayCount += 1;
      }
      await controller.play();
    }
    if (mounted) setState(() {});
  }

  Future<void> _stopPlayback() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) return;
    await controller.pause();
    await controller.seekTo(Duration.zero);
    if (mounted) setState(() {});
  }

  // ── Helpers ─────────────────────────────────────────────────────────────────

  Uri _resolveBackendUri(String path) {
    final parsed = Uri.tryParse(path);
    if (parsed != null && parsed.hasScheme) return parsed;
    final base = Uri.parse(BackendConnectionManager().baseUrl);
    final normalized = path.startsWith('/') ? path : '/$path';
    return base.replace(path: normalized);
  }

  void _logVideoError(Object error, StackTrace stackTrace) {
    debugPrint('Concept video load failure: $error');
    debugPrint(stackTrace.toString());
  }

  void _onControllerChanged() {
    final controller = _controller;
    if (controller?.value.isInitialized ?? false) {
      _updatePlaybackTelemetry(controller!.value);
    }
    if (mounted) setState(() {});
  }

  void _disposeController() {
    _controller?.removeListener(_onControllerChanged);
    _controller?.dispose();
    _controller = null;
  }

  // ── Telemetry ────────────────────────────────────────────────────────────────

  void _resetSessionTelemetry() {
    _sessionStartedAtUtc = DateTime.now().toUtc();
    _playStartedAtUtc = null;
    _watchDuration = Duration.zero;
    _maxPosition = Duration.zero;
    _lastPosition = Duration.zero;
    _seekBackCount = 0;
    _replayCount = 0;
    _completedOnce = false;
    _sessionReported = false;
  }

  void _updatePlaybackTelemetry(VideoPlayerValue value) {
    final now = DateTime.now().toUtc();
    if (value.isPlaying && _playStartedAtUtc == null) {
      _playStartedAtUtc = now;
    } else if (!value.isPlaying && _playStartedAtUtc != null) {
      _watchDuration += now.difference(_playStartedAtUtc!);
      _playStartedAtUtc = null;
    }

    final position = value.position;
    if (_lastPosition - position > const Duration(seconds: 2)) {
      _seekBackCount += 1;
    }
    if (position > _maxPosition) _maxPosition = position;

    final duration = value.duration;
    if (duration.inMilliseconds > 0 &&
        duration - position <= const Duration(seconds: 1)) {
      _completedOnce = true;
    }
    _lastPosition = position;
  }

  void _emitSessionTelemetry() {
    if (_sessionReported) return;
    final controller = _controller;
    if (controller?.value.isInitialized ?? false) {
      _updatePlaybackTelemetry(controller!.value);
    }
    if (_playStartedAtUtc != null) {
      _watchDuration += DateTime.now().toUtc().difference(_playStartedAtUtc!);
      _playStartedAtUtc = null;
    }

    final duration = controller?.value.duration ?? Duration.zero;
    final completionRatio = duration.inMilliseconds <= 0
        ? 0.0
        : (_maxPosition.inMilliseconds / duration.inMilliseconds)
            .clamp(0.0, 1.0);
    final interacted = _watchDuration.inMilliseconds > 0 ||
        _maxPosition.inMilliseconds > 0 ||
        _seekBackCount > 0 ||
        _replayCount > 0;
    if (!interacted) return;

    widget.onSessionEnded?.call({
      'watch_duration_seconds': _watchDuration.inMilliseconds / 1000,
      'completion_ratio': completionRatio,
      'seek_back_count': _seekBackCount,
      'replay_count': _replayCount,
      'started_at_utc': _sessionStartedAtUtc.toIso8601String(),
    });
    _sessionReported = true;
  }

  // ── Build ────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final controller = _controller;
    final isInitialized = controller?.value.isInitialized ?? false;
    final isPlaying = controller?.value.isPlaying ?? false;

    return LayoutBuilder(
      builder: (context, constraints) {
        final heroHeight = (constraints.maxHeight * 0.62).clamp(240.0, 520.0);
        return Container(
          decoration: BoxDecoration(
            color: AppTheme.surfaceWhite,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.borderLight),
          ),
          clipBehavior: Clip.antiAlias,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: SizedBox(
                height: heroHeight,
                child: Container(
                  color: Colors.black,
                  child: _buildVideoSurface(
                    context,
                    controller: controller,
                    isInitialized: isInitialized,
                    isPlaying: isPlaying,
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  // ── Video surface (with caption overlay) ────────────────────────────────────

  Widget _buildVideoSurface(
    BuildContext context, {
    required VideoPlayerController? controller,
    required bool isInitialized,
    required bool isPlaying,
  }) {
    if (isInitialized && controller != null) {
      final activeCaption = _activeCaptionText(controller.value.position);

      return Stack(
        fit: StackFit.expand,
        children: [
          ColoredBox(
            color: Colors.black,
            child: FittedBox(
              fit: BoxFit.contain,
              child: SizedBox(
                width: controller.value.size.width,
                height: controller.value.size.height,
                child: VideoPlayer(controller),
              ),
            ),
          ),
          // Tap overlay (play/pause)
          Positioned.fill(
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: _togglePlayback,
                child: AnimatedOpacity(
                  duration: const Duration(milliseconds: 180),
                  opacity: isPlaying ? 0 : 1,
                  child: Center(
                    child: Container(
                      width: 88,
                      height: 88,
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.46),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.white.withValues(alpha: 0.25),
                          width: 1.2,
                        ),
                      ),
                      child: const Icon(
                        Icons.play_arrow_rounded,
                        color: Colors.white,
                        size: 46,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          if (activeCaption != null)
            Positioned(
              left: 16,
              right: 16,
              bottom: 92,
              child: IgnorePointer(
                child: _CaptionOverlay(text: activeCaption),
              ),
            ),
          Positioned(
            left: 12,
            right: 12,
            bottom: 12,
            child: _buildInlineControls(
              context,
              controller: controller,
              isInitialized: true,
              isPlaying: isPlaying,
            ),
          ),
        ],
      );
    }

    return Stack(
      fit: StackFit.expand,
      children: [
        _VideoPlaceholder(isLoading: _isLoading),
        Positioned(
          left: 12,
          right: 12,
          bottom: 12,
          child: _buildInlineControls(
            context,
            controller: controller,
            isInitialized: false,
            isPlaying: false,
          ),
        ),
      ],
    );
  }

  // ── Inline controls ──────────────────────────────────────────────────────────

  Widget _buildInlineControls(
    BuildContext context, {
    required VideoPlayerController? controller,
    required bool isInitialized,
    required bool isPlaying,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xE6000000),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white24),
      ),
      child: Column(
        children: [
          Row(
            children: [
              _SkipButton(
                icon: Icons.replay_10_rounded,
                label: 'Back 10 seconds',
                enabled: isInitialized,
                onTap: () => _seekRelative(const Duration(seconds: -10)),
              ),
              const SizedBox(width: 6),
              IconButton(
                onPressed: isInitialized ? _togglePlayback : null,
                color: Colors.white,
                disabledColor: Colors.white30,
                icon: Icon(
                  isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                ),
              ),
              const SizedBox(width: 6),
              IconButton(
                tooltip: 'Stop',
                onPressed: isInitialized ? _stopPlayback : null,
                color: Colors.white,
                disabledColor: Colors.white30,
                icon: const Icon(Icons.stop_rounded),
              ),
              const SizedBox(width: 6),
              _SkipButton(
                icon: Icons.forward_10_rounded,
                label: 'Forward 10 seconds',
                enabled: isInitialized,
                onTap: () => _seekRelative(const Duration(seconds: 10)),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  _timelineLabel(controller),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
              const SizedBox(width: 8),
              _CcButton(
                available: _captionsAvailable,
                enabled: _captionsEnabled,
                onTap: _toggleCaptions,
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (isInitialized && controller != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: VideoProgressIndicator(
                controller,
                allowScrubbing: true,
                padding: EdgeInsets.zero,
                colors: const VideoProgressColors(
                  playedColor: AppTheme.primaryBlue,
                  bufferedColor: Color(0xFF60A5FA),
                  backgroundColor: Color(0xFF334155),
                ),
              ),
            )
          else
            Container(
              height: 6,
              decoration: BoxDecoration(
                color: const Color(0xFFE5E7EB),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
        ],
      ),
    );
  }

  // ── Helpers ──────────────────────────────────────────────────────────────────

  String _timelineLabel(VideoPlayerController? controller) {
    if (controller == null || !controller.value.isInitialized) {
      return '00:00 / 00:00';
    }
    return '${_fmt(controller.value.position)} / ${_fmt(controller.value.duration)}';
  }

  String _fmt(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
  }
}

// ── Caption overlay ──────────────────────────────────────────────────────────

class _CaptionOverlay extends StatelessWidget {
  final String text;

  const _CaptionOverlay({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.72),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        textAlign: TextAlign.center,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 14,
          fontWeight: FontWeight.w500,
          height: 1.45,
          shadows: [
            Shadow(blurRadius: 4, color: Colors.black),
          ],
        ),
      ),
    );
  }
}

// ── Skip button ──────────────────────────────────────────────────────────────

class _SkipButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool enabled;
  final VoidCallback onTap;

  const _SkipButton({
    required this.icon,
    required this.label,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = enabled ? Colors.white : Colors.white30;
    return Tooltip(
      message: label,
      child: InkWell(
        onTap: enabled ? onTap : null,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 6),
          child: Icon(icon, color: color, size: 28),
        ),
      ),
    );
  }
}

// ── CC toggle button ─────────────────────────────────────────────────────────

class _CcButton extends StatelessWidget {
  final bool available;
  final bool enabled;
  final VoidCallback onTap;

  const _CcButton({
    required this.available,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (!available) {
      return const Tooltip(
        message: 'No captions available',
        child: Icon(
          Icons.closed_caption_disabled_outlined,
          size: 22,
          color: Color(0xFFCBD5E1),
        ),
      );
    }

    return Tooltip(
      message: enabled ? 'Hide captions' : 'Show captions',
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(6),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
          decoration: BoxDecoration(
            color: enabled
                ? AppTheme.primaryBlue.withValues(alpha: 0.12)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(
              color: enabled ? AppTheme.primaryBlue : const Color(0xFFCBD5E1),
              width: 1.2,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                enabled
                    ? Icons.closed_caption_rounded
                    : Icons.closed_caption_outlined,
                size: 18,
                color: enabled ? AppTheme.primaryBlue : const Color(0xFF94A3B8),
              ),
              const SizedBox(width: 4),
              Text(
                'CC',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color:
                      enabled ? AppTheme.primaryBlue : const Color(0xFF94A3B8),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Supporting widgets ───────────────────────────────────────────────────────

class _VideoPlaceholder extends StatelessWidget {
  final bool isLoading;

  const _VideoPlaceholder({
    required this.isLoading,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        const DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Color(0xFF020617),
                Color(0xFF10233D),
                Color(0xFF07111F),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        if (isLoading)
          const Center(
            child: SizedBox(
              width: 26,
              height: 26,
              child: CircularProgressIndicator(
                strokeWidth: 2.4,
                color: Colors.white70,
              ),
            ),
          ),
      ],
    );
  }
}
