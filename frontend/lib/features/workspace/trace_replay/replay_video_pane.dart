import 'dart:async';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import '../../../core/backend_api.dart';
import '../../../core/replay_contract.dart';
import 'replay_media_auth.dart';

class ReplayVideoPane extends StatefulWidget {
  final String videoPath;
  final String replayRenderStatus;
  final String? replayRenderError;
  final VoidCallback? onCompleted;
  final VoidCallback? onOpenInteractiveTrace;
  final bool showInteractiveTraceAction;

  const ReplayVideoPane({
    super.key,
    required this.videoPath,
    required this.replayRenderStatus,
    this.replayRenderError,
    this.onCompleted,
    this.onOpenInteractiveTrace,
    this.showInteractiveTraceAction = false,
  });

  @override
  State<ReplayVideoPane> createState() => _ReplayVideoPaneState();
}

class _ReplayVideoPaneState extends State<ReplayVideoPane> {
  VideoPlayerController? _controller;
  bool _isLoading = false;
  String? _loadError;
  StreamSubscription<void>? _playbackListener;

  @override
  void initState() {
    super.initState();
    _initializeReplayVideo();
  }

  @override
  void didUpdateWidget(covariant ReplayVideoPane oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.videoPath != widget.videoPath) {
      _initializeReplayVideo();
    }
  }

  @override
  void dispose() {
    _disposeController();
    super.dispose();
  }

  Future<void> _initializeReplayVideo() async {
    await _disposeController();
    if (!mounted) {
      return;
    }
    if (widget.videoPath.isEmpty) {
      setState(() {
        _controller = null;
        _isLoading = false;
        _loadError = null;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _loadError = null;
    });

    try {
      final controller = VideoPlayerController.networkUrl(
        _replayVideoUri(widget.videoPath),
        httpHeaders: replayMediaAuthHeaders(),
      );
      await controller.initialize();
      await _playbackListener?.cancel();
      _playbackListener = controller.position.asStream().listen((_) {
        final value = controller.value;
        if (!value.isInitialized || value.duration == Duration.zero) {
          return;
        }
        if (value.position >= value.duration) {
          widget.onCompleted?.call();
        }
        if (mounted) {
          setState(() {});
        }
      });
      if (!mounted) {
        await controller.dispose();
        return;
      }
      setState(() {
        _controller = controller;
        _isLoading = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _controller = null;
        _isLoading = false;
        _loadError = 'The generated MP4 could not be loaded yet.';
      });
    }
  }

  Future<void> _disposeController() async {
    await _playbackListener?.cancel();
    _playbackListener = null;
    final controller = _controller;
    _controller = null;
    await controller?.dispose();
  }

  Uri _replayVideoUri(String videoPath) {
    final baseUri = Uri.parse(BackendConnectionManager().baseUrl);
    return baseUri.replace(
      path: '/visualization/video',
      queryParameters: {'path': videoPath},
    );
  }

  Future<void> _toggleReplayPlayback() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) {
      return;
    }
    if (controller.value.isPlaying) {
      await controller.pause();
    } else {
      await controller.play();
    }
    if (mounted) {
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final controller = _controller;
    final replayState = ReplayStateSnapshot.resolve(
      rawStatus: widget.replayRenderStatus,
      videoPath: widget.videoPath,
      error: widget.replayRenderError,
    );
    final isReady = controller?.value.isInitialized ?? false;
    final isPlaying = controller?.value.isPlaying ?? false;
    final statusLabel = _statusChipLabel(isReady, replayState);
    final statusAccent = _statusChipColor(isReady, replayState);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Container(
            key: const ValueKey('replay-video-frame'),
            color: Colors.black,
            child: AspectRatio(
              aspectRatio: isReady ? controller!.value.aspectRatio : 16 / 9,
              child: isReady && controller != null
                  ? _buildReplayVideoSurface(controller, isPlaying)
                  : _buildReplayVideoPlaceholder(context, replayState),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _buildReplayVideoControls(
          context,
          controller,
          isReady,
          isPlaying,
          statusLabel,
          statusAccent,
        ),
      ],
    );
  }

  Widget _buildReplayVideoSurface(
    VideoPlayerController controller,
    bool isPlaying,
  ) {
    return Stack(
      fit: StackFit.expand,
      children: [
        FittedBox(
          fit: BoxFit.contain,
          child: SizedBox(
            width: controller.value.size.width,
            height: controller.value.size.height,
            child: VideoPlayer(controller),
          ),
        ),
        Positioned.fill(
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: _toggleReplayPlayback,
              child: AnimatedOpacity(
                duration: const Duration(milliseconds: 180),
                opacity: isPlaying ? 0 : 1,
                child: const Center(
                  child: Icon(
                    Icons.play_circle_fill_rounded,
                    color: Colors.white,
                    size: 82,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildReplayVideoPlaceholder(
    BuildContext context,
    ReplayStateSnapshot replayState,
  ) {
    final message = _isLoading
        ? 'Preparing generated replay video...'
        : (_loadError ??
            widget.replayRenderError ??
            _renderStatusMessage(replayState));
    return Container(
      alignment: Alignment.center,
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_isLoading)
            const CircularProgressIndicator(color: Color(0xFF38BDF8))
          else
            const Icon(
              Icons.ondemand_video_outlined,
              color: Color(0xFF94A3B8),
              size: 42,
            ),
          const SizedBox(height: 12),
          Text(
            message,
            key: const ValueKey('replay-video-status-message'),
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFFE2E8F0),
                ),
          ),
          if (!_isLoading) ...[
            const SizedBox(height: 12),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              alignment: WrapAlignment.center,
              children: [
                OutlinedButton.icon(
                  onPressed: _initializeReplayVideo,
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('Retry'),
                ),
                if (widget.showInteractiveTraceAction &&
                    widget.onOpenInteractiveTrace != null)
                  OutlinedButton.icon(
                    key: const ValueKey('replay-open-step-trace'),
                    onPressed: widget.onOpenInteractiveTrace,
                    icon: const Icon(Icons.dashboard_customize_rounded),
                    label: const Text('Open Step Trace'),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  String _renderStatusMessage(ReplayStateSnapshot replayState) {
    return switch (replayState.state) {
      ReplayState.queued =>
        'The generated MP4 is queued. Use the interactive trace meanwhile.',
      ReplayState.rendering =>
        'The generated MP4 is rendering. Use the interactive trace meanwhile.',
      ReplayState.failed =>
        'The generated MP4 failed, but the interactive trace is ready.',
      ReplayState.timeout =>
        'The generated MP4 is still running in the background.',
      ReplayState.unavailable =>
        'Interactive replay is available. Generated video is not ready.',
      ReplayState.ready => 'Generated replay video is ready.',
      ReplayState.idle => 'Generated replay video is not ready.',
    };
  }

  Widget _buildReplayVideoControls(
    BuildContext context,
    VideoPlayerController? controller,
    bool isReady,
    bool isPlaying,
    String statusLabel,
    Color statusAccent,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              IconButton.filled(
                onPressed: isReady ? _toggleReplayPlayback : null,
                icon: Icon(
                  isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  _replayTimelineLabel(controller),
                  key: const ValueKey('replay-video-timeline'),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
              const SizedBox(width: 8),
              _statusChip(statusLabel, statusAccent),
              if (isReady) ...[
                const SizedBox(width: 8),
                Text(
                  isPlaying ? 'Playing' : 'Paused',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFFCBD5E1),
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ],
          ),
          if (!isReady &&
              widget.showInteractiveTraceAction &&
              widget.onOpenInteractiveTrace != null) ...[
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton.icon(
                key: const ValueKey('replay-open-step-trace-inline'),
                onPressed: widget.onOpenInteractiveTrace,
                icon: const Icon(Icons.arrow_back_rounded),
                label: const Text('Use interactive trace'),
              ),
            ),
          ],
          const SizedBox(height: 8),
          if (isReady && controller != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: VideoProgressIndicator(
                controller,
                allowScrubbing: true,
                padding: EdgeInsets.zero,
                colors: const VideoProgressColors(
                  playedColor: Color(0xFF38BDF8),
                  bufferedColor: Color(0xFF1D4ED8),
                  backgroundColor: Color(0xFF334155),
                ),
              ),
            )
          else
            Container(
              height: 6,
              decoration: BoxDecoration(
                color: const Color(0xFF334155),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
        ],
      ),
    );
  }

  Widget _statusChip(String label, Color accent) {
    return Container(
      key: const ValueKey('replay-video-status-chip'),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: accent.withValues(alpha: 0.35)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: accent,
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  String _statusChipLabel(bool isReady, ReplayStateSnapshot replayState) {
    if (isReady) {
      return 'Ready';
    }
    if (_isLoading) {
      return 'Loading';
    }
    return switch (replayState.state) {
      ReplayState.queued => 'Queued',
      ReplayState.rendering => 'Rendering',
      ReplayState.failed => 'Failed',
      ReplayState.timeout => 'Running',
      ReplayState.unavailable => 'Unavailable',
      ReplayState.idle => 'Pending',
      ReplayState.ready => 'Ready',
    };
  }

  Color _statusChipColor(bool isReady, ReplayStateSnapshot replayState) {
    if (isReady) {
      return const Color(0xFF34D399);
    }
    if (_isLoading) {
      return const Color(0xFF38BDF8);
    }
    return switch (replayState.state) {
      ReplayState.failed => const Color(0xFFF87171),
      ReplayState.queued ||
      ReplayState.rendering ||
      ReplayState.timeout =>
        const Color(0xFFFBBF24),
      _ => const Color(0xFF94A3B8),
    };
  }

  String _replayTimelineLabel(VideoPlayerController? controller) {
    if (controller == null || !controller.value.isInitialized) {
      return _isLoading ? 'Loading generated replay...' : 'Replay unavailable';
    }
    return '${_formatDuration(controller.value.position)} / ${_formatDuration(controller.value.duration)}';
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }
}
