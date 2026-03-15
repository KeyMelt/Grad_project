import 'package:flutter/material.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';

class LessonCard extends StatelessWidget {
  final String title;
  final String description;
  final bool isActive;
  final bool hasVideo;
  final bool hasHardware;
  final VoidCallback? onTap;

  const LessonCard({
    super.key,
    required this.title,
    required this.description,
    this.isActive = false,
    this.hasVideo = false,
    this.hasHardware = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(AppConstants.cardRadius),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.surfaceWhite,
            borderRadius: BorderRadius.circular(AppConstants.cardRadius),
            border: Border.all(
              color: isActive ? AppTheme.primaryBlue : AppTheme.borderLight,
              width: isActive ? 2 : 1,
            ),
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: AppTheme.primaryBlue.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      title,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ),
                  Row(
                    children: [
                      if (hasVideo)
                        _buildIconBadge(Icons.play_arrow, AppTheme.primaryBlue),
                      if (hasHardware) const SizedBox(width: 4),
                      if (hasHardware)
                        _buildIconBadge(Icons.memory, AppTheme.successGreen),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIconBadge(IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Icon(icon, size: 16, color: color),
    );
  }
}
