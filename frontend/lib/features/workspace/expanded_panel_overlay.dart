import 'dart:ui';

import 'package:flutter/material.dart';

import '../../core/theme.dart';

class ExpandedPanelBackdrop extends StatelessWidget {
  final bool isActive;
  final Widget child;

  const ExpandedPanelBackdrop({
    super.key,
    required this.isActive,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    if (!isActive) {
      return child;
    }
    return IgnorePointer(
      child: ImageFiltered(
        imageFilter: ImageFilter.blur(sigmaX: 11, sigmaY: 11),
        child: child,
      ),
    );
  }
}

class ExpandedDrawerOverlay extends StatelessWidget {
  final Widget child;

  const ExpandedDrawerOverlay({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: Container(
        color: AppTheme.navy.withValues(alpha: 0.24),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final compactWidth = constraints.maxWidth < 760;
            final compactHeight = constraints.maxHeight < 620;
            return Center(
              child: FractionallySizedBox(
                widthFactor: compactWidth ? 0.94 : 0.82,
                heightFactor: compactHeight ? 0.92 : 0.86,
                child: Material(
                  elevation: 18,
                  color: AppTheme.surfaceWhite,
                  surfaceTintColor: AppTheme.surfaceWhite,
                  borderRadius: BorderRadius.circular(8),
                  clipBehavior: Clip.antiAlias,
                  child: child,
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class DrawerPanelResizeButton extends StatelessWidget {
  final bool isExpanded;
  final String expandTooltip;
  final String minimizeTooltip;
  final VoidCallback onPressed;

  const DrawerPanelResizeButton({
    super.key,
    required this.isExpanded,
    required this.expandTooltip,
    required this.minimizeTooltip,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      visualDensity: VisualDensity.compact,
      tooltip: isExpanded ? minimizeTooltip : expandTooltip,
      onPressed: onPressed,
      icon: Icon(
        isExpanded
            ? Icons.close_fullscreen_rounded
            : Icons.open_in_full_rounded,
        size: 20,
      ),
    );
  }
}
