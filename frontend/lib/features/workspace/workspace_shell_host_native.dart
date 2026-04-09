import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

import 'workspace_shell_host_stub.dart' as stub;

Widget buildWorkspaceShellHost({
  required BuildContext context,
  required String? url,
  required bool workspaceReady,
  required String fallbackMessage,
}) {
  if (kIsWeb || defaultTargetPlatform != TargetPlatform.macOS || url == null) {
    return stub.buildWorkspaceShellHost(
      context: context,
      url: url,
      workspaceReady: workspaceReady,
      fallbackMessage: fallbackMessage,
    );
  }

  return _MacWorkspaceShellHost(
    url: url,
    fallbackMessage: fallbackMessage,
  );
}

class _MacWorkspaceShellHost extends StatefulWidget {
  final String url;
  final String fallbackMessage;

  const _MacWorkspaceShellHost({
    required this.url,
    required this.fallbackMessage,
  });

  @override
  State<_MacWorkspaceShellHost> createState() => _MacWorkspaceShellHostState();
}

class _MacWorkspaceShellHostState extends State<_MacWorkspaceShellHost> {
  late final WebViewController _controller;
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
            if (mounted) {
              setState(() {
                _pageLoaded = true;
              });
            }
          },
          onWebResourceError: (_) {
            if (mounted) {
              setState(() {
                _loadFailed = true;
              });
            }
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.url));
  }

  @override
  void didUpdateWidget(covariant _MacWorkspaceShellHost oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.url != widget.url) {
      _loadFailed = false;
      _pageLoaded = false;
      _controller.loadRequest(Uri.parse(widget.url));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loadFailed) {
      return stub.buildWorkspaceShellHost(
        context: context,
        url: null,
        workspaceReady: false,
        fallbackMessage: widget.fallbackMessage,
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
              fallbackMessage: widget.fallbackMessage,
            ),
          ),
      ],
    );
  }
}
