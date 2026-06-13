import 'package:flutter/material.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';

class LessonCard extends StatelessWidget {
  final String title;
  final String description;
  final bool isActive;
  final bool hasVideo;
  final bool backendEnabled;
  final VoidCallback? onTap;

  const LessonCard({
    super.key,
    required this.title,
    required this.description,
    this.isActive = false,
    this.hasVideo = false,
    this.backendEnabled = true,
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
                      color: AppTheme.primaryBlue.withValues(alpha: 0.1),
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
                      if (hasVideo) const SizedBox(width: 4),
                      _buildIconBadge(
                        backendEnabled ? Icons.code : Icons.edit_note_rounded,
                        backendEnabled
                            ? AppTheme.successGreen
                            : const Color(0xFFF59E0B),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              if (!backendEnabled) ...[
                const SizedBox(height: 10),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF7ED),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: const Color(0xFFF59E0B)),
                  ),
                  child: const Text(
                    'Concept lesson',
                    style: TextStyle(
                      color: Color(0xFFB45309),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
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
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Icon(icon, size: 16, color: color),
    );
  }
}
