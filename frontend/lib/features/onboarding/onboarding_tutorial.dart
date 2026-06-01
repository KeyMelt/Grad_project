import 'package:flutter/material.dart';

import '../../core/theme.dart';
import '../../core/workbench_state.dart';

Future<void> showOnboardingTutorial(
  BuildContext context, {
  required ValueChanged<AppSection> onNavigate,
  String role = 'guest',
}) {
  return showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (_) => _OnboardingTutorialDialog(
      onNavigate: onNavigate,
      role: role,
    ),
  );
}

class _OnboardingTutorialDialog extends StatefulWidget {
  final ValueChanged<AppSection> onNavigate;
  final String role;

  const _OnboardingTutorialDialog({
    required this.onNavigate,
    required this.role,
  });

  @override
  State<_OnboardingTutorialDialog> createState() =>
      _OnboardingTutorialDialogState();
}

class _OnboardingTutorialDialogState extends State<_OnboardingTutorialDialog> {
  int _index = 0;

  static const List<_TutorialStep> _coreSteps = [
    _TutorialStep(
      title: 'Home dashboard',
      body: 'Sign in, review lessons, and check progress.',
      section: AppSection.home,
      icon: Icons.home_outlined,
    ),
    _TutorialStep(
      title: 'Workspace',
      body: 'Use Concept, Code, and Replay tabs to learn and run code.',
      section: AppSection.workspace,
      icon: Icons.workspaces_outline,
    ),
    _TutorialStep(
      title: 'Quiz and N-gain',
      body: 'Take pre/post quizzes to track N-gain.',
      section: AppSection.quiz,
      icon: Icons.quiz_outlined,
    ),
  ];

  List<_TutorialStep> get _steps {
    final role = widget.role.toLowerCase();
    if (role == 'instructor' || role == 'admin') {
      return [
        ..._coreSteps,
        _TutorialStep(
          title: 'Authoring tools',
          body: role == 'admin'
              ? 'Manage lessons and admin evaluation exports.'
              : 'Manage lesson content in the authoring workspace.',
          section: AppSection.admin,
          icon: Icons.admin_panel_settings_outlined,
        ),
      ];
    }
    return _coreSteps;
  }

  @override
  Widget build(BuildContext context) {
    final step = _steps[_index];
    final isLast = _index == _steps.length - 1;

    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 640),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      color: AppTheme.tealSurface,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(step.icon, color: AppTheme.primaryBlue),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Platform onboarding',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Skip'),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              Text(
                'Step ${_index + 1} of ${_steps.length}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: const Color(0xFF6B7280),
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                step.title,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 10),
              Text(
                step.body,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.5,
                    ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => widget.onNavigate(step.section),
                  icon: const Icon(Icons.open_in_new_rounded),
                  label: Text('Open ${_sectionLabel(step.section)}'),
                ),
              ),
              const SizedBox(height: 18),
              Row(
                children: [
                  for (var i = 0; i < _steps.length; i++)
                    Expanded(
                      child: Container(
                        margin: EdgeInsets.only(
                            right: i == _steps.length - 1 ? 0 : 8),
                        height: 5,
                        decoration: BoxDecoration(
                          color: i <= _index
                              ? AppTheme.primaryBlue
                              : AppTheme.borderLight,
                          borderRadius: BorderRadius.circular(999),
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 18),
              Row(
                children: [
                  OutlinedButton(
                    onPressed:
                        _index == 0 ? null : () => setState(() => _index -= 1),
                    child: const Text('Back'),
                  ),
                  const Spacer(),
                  FilledButton(
                    onPressed: () {
                      if (isLast) {
                        Navigator.of(context).pop();
                        return;
                      }
                      setState(() => _index += 1);
                    },
                    child: Text(isLast ? 'Finish' : 'Next'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _sectionLabel(AppSection section) {
    switch (section) {
      case AppSection.home:
        return 'Home';
      case AppSection.workspace:
        return 'Workspace';
      case AppSection.flashcards:
        return 'Flashcards';
      case AppSection.quiz:
        return 'Quiz';
      case AppSection.admin:
        return 'Authoring';
    }
  }
}

class _TutorialStep {
  final String title;
  final String body;
  final AppSection section;
  final IconData icon;

  const _TutorialStep({
    required this.title,
    required this.body,
    required this.section,
    required this.icon,
  });
}
