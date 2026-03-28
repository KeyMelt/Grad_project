import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:video_player/video_player.dart';

import '../../core/theme.dart';
import '../../core/workbench_state.dart';

class VideoPlayerTab extends StatefulWidget {
  final LessonDefinition lesson;

  const VideoPlayerTab({
    super.key,
    required this.lesson,
  });

  @override
  State<VideoPlayerTab> createState() => _VideoPlayerTabState();
}

class _VideoPlayerTabState extends State<VideoPlayerTab>
    with AutomaticKeepAliveClientMixin {
  VideoPlayerController? _controller;
  bool _isLoading = false;
  String? _errorMessage;

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
    if (oldWidget.lesson.conceptVideo.assetPath !=
        widget.lesson.conceptVideo.assetPath) {
      _disposeController();
      _initializeVideo();
    }
  }

  @override
  void dispose() {
    _disposeController();
    super.dispose();
  }

  Future<void> _initializeVideo() async {
    if (_isLoading) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final controller = await _buildControllerWithFallback(
        widget.lesson.conceptVideo.assetPath,
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
      if (!mounted) {
        return;
      }

      final details = _extractVideoErrorDetails(error, stackTrace);
      setState(() {
        _isLoading = false;
        _errorMessage = details;
      });
    }
  }

  Future<VideoPlayerController> _buildControllerWithFallback(
    String assetPath,
  ) async {
    try {
      final controller = VideoPlayerController.asset(assetPath);
      await controller.initialize().timeout(const Duration(seconds: 45));
      await controller.setLooping(false);
      controller.addListener(_onControllerChanged);
      return controller;
    } catch (_) {
      if (kIsWeb) {
        rethrow;
      }

      final fallbackController = await _buildFileBackedController(assetPath);
      await fallbackController
          .initialize()
          .timeout(const Duration(seconds: 45));
      await fallbackController.setLooping(false);
      fallbackController.addListener(_onControllerChanged);
      return fallbackController;
    }
  }

  Future<VideoPlayerController> _buildFileBackedController(
      String assetPath) async {
    final ByteData data = await rootBundle.load(assetPath);
    final bytes =
        data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
    final safeName =
        assetPath.split('/').last.replaceAll(RegExp(r'[^A-Za-z0-9_.-]'), '_');
    final file = File('${Directory.systemTemp.path}/rl_ide_$safeName');
    await file.writeAsBytes(bytes, flush: true);
    return VideoPlayerController.file(file);
  }

  String _extractVideoErrorDetails(Object error, StackTrace stackTrace) {
    final raw = error.toString();
    final message = raw.length > 180 ? '${raw.substring(0, 180)}...' : raw;
    debugPrint('Concept video load failure: $raw');
    debugPrint(stackTrace.toString());
    return 'Video failed to load: $message';
  }

  void _onControllerChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _togglePlayback() async {
    final controller = _controller;
    if (controller == null) {
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

  void _disposeController() {
    _controller?.removeListener(_onControllerChanged);
    _controller?.dispose();
    _controller = null;
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final lessonVideo = widget.lesson.conceptVideo;
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(18, 16, 18, 10),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Concept lesson video',
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                      ),
                    ),
                    _InfoPill(
                      label: lessonVideo.durationLabel,
                      icon: Icons.ondemand_video_outlined,
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: SizedBox(
                    height: heroHeight,
                    child: Container(
                      color: const Color(0xFF07111F),
                      child: _buildVideoSurface(
                        context,
                        isInitialized: isInitialized,
                        isPlaying: isPlaying,
                      ),
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 10),
                child: _buildControlBar(
                  context,
                  controller: controller,
                  isInitialized: isInitialized,
                  isPlaying: isPlaying,
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                child: ExpansionTile(
                  tilePadding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
                  collapsedBackgroundColor: const Color(0xFFF8FAFC),
                  backgroundColor: const Color(0xFFF8FAFC),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: const BorderSide(color: AppTheme.borderLight),
                  ),
                  collapsedShape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: const BorderSide(color: AppTheme.borderLight),
                  ),
                  title: const Text(
                    'Lesson notes',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  subtitle: Text(
                    lessonVideo.summary,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(14, 0, 14, 10),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            lessonVideo.summary,
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: AppTheme.textPrimary,
                                  height: 1.45,
                                ),
                          ),
                          const SizedBox(height: 10),
                          ...lessonVideo.highlights.map(
                            (highlight) => Padding(
                              padding: const EdgeInsets.only(bottom: 8),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Padding(
                                    padding: EdgeInsets.only(top: 4),
                                    child: Icon(
                                      Icons.circle,
                                      size: 7,
                                      color: AppTheme.primaryBlue,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      highlight,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.copyWith(
                                            color: AppTheme.textPrimary,
                                            height: 1.4,
                                          ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildVideoSurface(
    BuildContext context, {
    required bool isInitialized,
    required bool isPlaying,
  }) {
    if (isInitialized && _controller != null) {
      return Stack(
        fit: StackFit.expand,
        children: [
          ColoredBox(
            color: Colors.black,
            child: FittedBox(
              fit: BoxFit.contain,
              child: SizedBox(
                width: _controller!.value.size.width,
                height: _controller!.value.size.height,
                child: VideoPlayer(_controller!),
              ),
            ),
          ),
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
        ],
      );
    }

    return _VideoPlaceholder(
      title: widget.lesson.title,
      isLoading: _isLoading,
      errorMessage: _errorMessage,
      onRetry: _initializeVideo,
    );
  }

  Widget _buildControlBar(
    BuildContext context, {
    required VideoPlayerController? controller,
    required bool isInitialized,
    required bool isPlaying,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: Column(
        children: [
          Row(
            children: [
              IconButton.filled(
                onPressed: isInitialized ? _togglePlayback : null,
                icon: Icon(
                  isPlaying ? Icons.pause_rounded : Icons.play_arrow_rounded,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  _timelineLabel(controller),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                isPlaying ? 'Playing' : 'Paused',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.textSecondary,
                      fontWeight: FontWeight.w600,
                    ),
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
                  bufferedColor: Color(0xFFBBD2F6),
                  backgroundColor: Color(0xFFE5E7EB),
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

  String _timelineLabel(VideoPlayerController? controller) {
    if (controller == null || !controller.value.isInitialized) {
      if (_isLoading) {
        return 'Preparing lesson video...';
      }
      return _errorMessage ?? 'Preview unavailable';
    }
    return '${_formatDuration(controller.value.position)} / ${_formatDuration(controller.value.duration)}';
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }
}

class _VideoPlaceholder extends StatelessWidget {
  final String title;
  final bool isLoading;
  final String? errorMessage;
  final VoidCallback onRetry;

  const _VideoPlaceholder({
    required this.title,
    required this.isLoading,
    required this.errorMessage,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        DecoratedBox(
          decoration: const BoxDecoration(
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
        Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.movie_creation_outlined,
                    color: Colors.white,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      title,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                  ),
                ],
              ),
              const Spacer(),
              Text(
                errorMessage ?? 'Pre-rendered lesson explainer',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 10),
              Text(
                errorMessage ??
                    'Watch lesson video here. Replay is in Replay tab.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: const Color(0xFFD7E3F4),
                      height: 1.45,
                    ),
              ),
              const SizedBox(height: 18),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  _OverlayPill(
                    label: 'Gymnasium visuals',
                    icon: Icons.grid_view_rounded,
                  ),
                  _OverlayPill(
                    label: 'Code trace',
                    icon: Icons.code_rounded,
                  ),
                  _OverlayPill(
                    label: 'Mathematics',
                    icon: Icons.functions_rounded,
                  ),
                ],
              ),
              const SizedBox(height: 24),
              if (isLoading)
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.hourglass_bottom_rounded,
                      color: Colors.white,
                      size: 22,
                    ),
                    const SizedBox(width: 10),
                    Text(
                      'Loading video...',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ],
                ),
              if (!isLoading && errorMessage != null) ...[
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('Retry video'),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _OverlayPill extends StatelessWidget {
  final String label;
  final IconData icon;

  const _OverlayPill({
    required this.label,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: Colors.white24),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: Colors.white),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoPill extends StatelessWidget {
  final String label;
  final IconData icon;

  const _InfoPill({
    required this.label,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F0FE),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: AppTheme.primaryBlue, size: 18),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.primaryBlue,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
