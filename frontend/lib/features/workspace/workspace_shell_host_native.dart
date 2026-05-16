import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import 'workspace_shell_host_stub.dart' as stub;

Widget buildWorkspaceShellHost({
  required BuildContext context,
  required String? url,
  required bool workspaceReady,
  required bool isLoading,
  required String placeholderMessage,
}) {
  if (kIsWeb ||
      (defaultTargetPlatform != TargetPlatform.macOS &&
          defaultTargetPlatform != TargetPlatform.iOS) ||
      url == null) {
    return stub.buildWorkspaceShellHost(
      context: context,
      url: url,
      workspaceReady: workspaceReady,
      isLoading: isLoading,
      placeholderMessage: placeholderMessage,
    );
  }

  return _MacWorkspaceShellHost(
    url: url,
    placeholderMessage: placeholderMessage,
  );
}

class _MacWorkspaceShellHost extends StatefulWidget {
  final String url;
  final String placeholderMessage;

  const _MacWorkspaceShellHost({
    required this.url,
    required this.placeholderMessage,
  });

  @override
  State<_MacWorkspaceShellHost> createState() => _MacWorkspaceShellHostState();
}

class _MacWorkspaceShellHostState extends State<_MacWorkspaceShellHost> {
  late final WebViewController _controller;
  Timer? _loadTimeout;
  bool _loadFailed = false;
  bool _pageLoaded = false;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (_) {
            _loadTimeout?.cancel();
            if (mounted) {
              setState(() {
                _pageLoaded = true;
                _loadFailed = false;
              });
            }
          },
          onWebResourceError: (_) {
            _loadTimeout?.cancel();
            if (mounted) {
              setState(() {
                _loadFailed = true;
              });
            }
          },
        ),
      );
    _loadUrl(widget.url);
  }

  @override
  void didUpdateWidget(covariant _MacWorkspaceShellHost oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.url != widget.url) {
      _loadUrl(widget.url);
    }
  }

  void _loadUrl(String url) {
    _loadTimeout?.cancel();
    _loadFailed = false;
    _pageLoaded = false;
    _loadTimeout = Timer(const Duration(seconds: 10), () {
      if (mounted && !_pageLoaded) {
        setState(() {
          _loadFailed = true;
        });
      }
    });
    _controller.loadRequest(Uri.parse(url));
  }

  @override
  void dispose() {
    _loadTimeout?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loadFailed) {
      return stub.buildWorkspaceShellHost(
        context: context,
        url: null,
        workspaceReady: false,
        isLoading: false,
        placeholderMessage: 'Connection failed, Try again.',
      );
    }
    return Stack(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: WebViewWidget(controller: _controller),
        ),
        if (!_pageLoaded)
          Positioned.fill(
            child: stub.buildWorkspaceShellHost(
              context: context,
              url: null,
              workspaceReady: false,
              isLoading: true,
              placeholderMessage: widget.placeholderMessage,
            ),
          ),
      ],
    );
  }
}
