import 'package:flutter/widgets.dart';

import 'workspace_shell_host_stub.dart'
    if (dart.library.html) 'workspace_shell_host_web.dart'
    if (dart.library.io) 'workspace_shell_host_native.dart';

class WorkspaceShellHost extends StatelessWidget {
  final String? url;
  final bool workspaceReady;
  final String fallbackMessage;

  const WorkspaceShellHost({
    super.key,
    required this.url,
    required this.workspaceReady,
    required this.fallbackMessage,
  });

  @override
  Widget build(BuildContext context) {
    return buildWorkspaceShellHost(
      context: context,
      url: url,
      workspaceReady: workspaceReady,
      fallbackMessage: fallbackMessage,
    );
  }
}
