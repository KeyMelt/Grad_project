// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use

import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

import 'package:flutter/material.dart';

import 'workspace_shell_host_stub.dart' as stub;

Widget buildWorkspaceShellHost({
  required BuildContext context,
  required String? url,
  required bool workspaceReady,
  required String fallbackMessage,
}) {
  if (url == null) {
    return stub.buildWorkspaceShellHost(
      context: context,
      url: url,
      workspaceReady: workspaceReady,
      fallbackMessage: fallbackMessage,
    );
  }

  return _WebWorkspaceShellHost(url: url);
}

class _WebWorkspaceShellHost extends StatefulWidget {
  final String url;

  const _WebWorkspaceShellHost({
    required this.url,
  });

  @override
  State<_WebWorkspaceShellHost> createState() => _WebWorkspaceShellHostState();
}

class _WebWorkspaceShellHostState extends State<_WebWorkspaceShellHost> {
  late String _viewType;
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _viewType = _registerView(widget.url);
  }

  @override
  void didUpdateWidget(covariant _WebWorkspaceShellHost oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.url != widget.url) {
      _loaded = false;
      _viewType = _registerView(widget.url);
    }
  }

  String _registerView(String url) {
    final viewType =
        'workspace-shell-${DateTime.now().microsecondsSinceEpoch}-${url.hashCode}';
    ui_web.platformViewRegistry.registerViewFactory(viewType, (int viewId) {
      final frame = html.IFrameElement()
        ..src = url
        ..style.border = '0'
        ..style.width = '100%'
        ..style.height = '100%'
        ..allow = 'clipboard-read; clipboard-write'
        ..setAttribute('sandbox',
            'allow-scripts allow-same-origin allow-forms allow-modals allow-downloads');
      frame.onLoad.listen((_) {
        if (mounted) {
          setState(() {
            _loaded = true;
          });
        }
      });
      return frame;
    });
    return viewType;
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: HtmlElementView(viewType: _viewType),
        ),
        if (!_loaded)
          Positioned.fill(
            child: stub.buildWorkspaceShellHost(
              context: context,
              url: null,
              workspaceReady: false,
              fallbackMessage: 'Loading workspace shell...',
            ),
          ),
      ],
    );
  }
}
