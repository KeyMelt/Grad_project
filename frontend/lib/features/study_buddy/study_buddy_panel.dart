import 'package:flutter/material.dart';

import '../../core/backend_api.dart';
import '../../core/lesson_models.dart';
import '../../core/theme.dart';

class StudyBuddyPanel extends StatelessWidget {
  final LessonDefinition lesson;
  final StudyBuddyIntervention? intervention;
  final bool isLoading;
  final bool isDismissed;
  final List<StudyBuddyChatMessage> chatMessages;
  final bool isChatLoading;
  final String? chatError;
  final VoidCallback onDismiss;
  final VoidCallback onComplete;
  final VoidCallback onReopen;
  final VoidCallback onRefresh;
  final ValueChanged<String> onSendChatMessage;

  const StudyBuddyPanel({
    super.key,
    required this.lesson,
    required this.intervention,
    required this.isLoading,
    required this.isDismissed,
    this.chatMessages = const [],
    this.isChatLoading = false,
    this.chatError,
    required this.onDismiss,
    required this.onComplete,
    required this.onReopen,
    required this.onRefresh,
    required this.onSendChatMessage,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      key: const ValueKey('study-buddy-panel'),
      elevation: 10,
      color: AppTheme.surfaceWhite,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppTheme.borderLight),
        ),
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _StudyBuddyHeader(
              lessonTitle: lesson.title,
              isDismissed: isDismissed,
              onDismiss: onDismiss,
              onReopen: onReopen,
              onRefresh: onRefresh,
            ),
            const SizedBox(height: 14),
            Expanded(
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 220),
                child: _buildBody(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (isDismissed) {
      return _DismissedContent(
        key: const ValueKey('study-buddy-dismissed'),
        onReopen: onReopen,
      );
    }

    Widget coachContent;
    if (isLoading && intervention == null) {
      coachContent = const _LoadingContent(
        key: ValueKey('study-buddy-loading'),
      );
    } else if (intervention != null) {
      coachContent = _InterventionContent(
        key: const ValueKey('study-buddy-intervention'),
        intervention: intervention!,
        onComplete: onComplete,
      );
    } else {
      coachContent = _IdleContent(
        key: const ValueKey('study-buddy-idle'),
        isChatLoading: isChatLoading,
        onQuickRecap: () => onSendChatMessage(
          'Give me a quick recap of the current exercise and what I should focus on next.',
        ),
        onFindBlocker: () => onSendChatMessage(
          'Help me identify the most likely blocker in this exercise and ask me one diagnostic question.',
        ),
      );
    }

    return _ActiveStudyBuddyContent(
      coachContent: coachContent,
      chatMessages: chatMessages,
      isChatLoading: isChatLoading,
      chatError: chatError,
      onSendChatMessage: onSendChatMessage,
    );
  }
}

class StudyBuddyExerciseBrief extends StatelessWidget {
  final LessonDefinition lesson;

  const StudyBuddyExerciseBrief({
    super.key,
    required this.lesson,
  });

  @override
  Widget build(BuildContext context) {
    final exercise = lesson.exercise;
    final taskCount = exercise.tasks.length;

    return LayoutBuilder(
      builder: (context, constraints) {
        final visibleTasks = exercise.tasks
            .take(constraints.maxHeight >= 160 ? 3 : 2)
            .toList(growable: false);

        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.borderLight),
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Current Exercise',
                            style: Theme.of(context)
                                .textTheme
                                .labelLarge
                                ?.copyWith(
                                  color: AppTheme.primaryBlue,
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.2,
                                ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            exercise.title.isNotEmpty
                                ? exercise.title
                                : lesson.title,
                            style: Theme.of(context)
                                .textTheme
                                .titleSmall
                                ?.copyWith(fontWeight: FontWeight.w800),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(color: AppTheme.borderLight),
                      ),
                      child: Text(
                        '$taskCount task${taskCount == 1 ? '' : 's'}',
                        style:
                            Theme.of(context).textTheme.labelMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                  color: AppTheme.textSecondary,
                                ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  exercise.overview.isNotEmpty
                      ? exercise.overview
                      : lesson.description,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.textPrimary,
                        height: 1.45,
                      ),
                ),
                if (visibleTasks.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    'What to do',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 8),
                  ...visibleTasks.map(
                    (task) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Padding(
                            padding: EdgeInsets.only(top: 5),
                            child: Icon(
                              Icons.radio_button_checked_rounded,
                              size: 10,
                              color: AppTheme.primaryBlue,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              task,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(
                                    color: AppTheme.textSecondary,
                                    height: 1.45,
                                  ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}

class _StudyBuddyHeader extends StatelessWidget {
  final String lessonTitle;
  final bool isDismissed;
  final VoidCallback onDismiss;
  final VoidCallback onReopen;
  final VoidCallback onRefresh;

  const _StudyBuddyHeader({
    required this.lessonTitle,
    required this.isDismissed,
    required this.onDismiss,
    required this.onReopen,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 42,
          height: 42,
          decoration: BoxDecoration(
            color: const Color(0xFFE8F0FE),
            borderRadius: BorderRadius.circular(14),
          ),
          child: const Icon(
            Icons.psychology_alt_outlined,
            color: AppTheme.primaryBlue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Study Buddy',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 2),
              Text(
                lessonTitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.textSecondary,
                    ),
              ),
            ],
          ),
        ),
        if (isDismissed)
          IconButton(
            tooltip: 'Open Study Buddy',
            onPressed: onReopen,
            icon: const Icon(Icons.visibility_rounded),
          )
        else ...[
          IconButton(
            tooltip: 'Refresh Study Buddy',
            onPressed: onRefresh,
            icon: const Icon(Icons.refresh_rounded),
          ),
          IconButton(
            tooltip: 'Dismiss Study Buddy',
            onPressed: onDismiss,
            icon: const Icon(Icons.close_rounded),
          ),
        ],
      ],
    );
  }
}

class _LoadingContent extends StatelessWidget {
  const _LoadingContent({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(strokeWidth: 2.4),
            ),
            SizedBox(height: 14),
            Text(
              'Study Buddy is checking for a useful intervention.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _DismissedContent extends StatelessWidget {
  final VoidCallback onReopen;

  const _DismissedContent({
    super.key,
    required this.onReopen,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.psychology_alt_outlined,
              size: 34,
              color: AppTheme.primaryBlue,
            ),
            const SizedBox(height: 12),
            Text(
              'Study Buddy is hidden for now.',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Reopen it any time to get contextual prompts for the current lesson.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onReopen,
              icon: const Icon(Icons.visibility_rounded),
              label: const Text('Open Study Buddy'),
            ),
          ],
        ),
      ),
    );
  }
}

class _IdleContent extends StatelessWidget {
  final bool isChatLoading;
  final VoidCallback onQuickRecap;
  final VoidCallback onFindBlocker;

  const _IdleContent({
    super.key,
    required this.isChatLoading,
    required this.onQuickRecap,
    required this.onFindBlocker,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxHeight < 150;
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI Coach',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                if (!compact) ...[
                  const SizedBox(height: 10),
                  Text(
                    'Study Buddy can recap the current exercise or help isolate a blocker.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppTheme.textPrimary,
                          height: 1.35,
                        ),
                  ),
                ],
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    ActionChip(
                      key: const ValueKey('study-buddy-quick-recap'),
                      tooltip: 'Ask for a quick recap',
                      avatar: const Icon(Icons.summarize_rounded, size: 18),
                      label: const Text('Quick recap'),
                      onPressed: isChatLoading ? null : onQuickRecap,
                    ),
                    ActionChip(
                      key: const ValueKey('study-buddy-find-blocker'),
                      tooltip: 'Ask for blocker help',
                      avatar: const Icon(Icons.troubleshoot_rounded, size: 18),
                      label: const Text('Find blocker'),
                      onPressed: isChatLoading ? null : onFindBlocker,
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _ActiveStudyBuddyContent extends StatelessWidget {
  final Widget coachContent;
  final List<StudyBuddyChatMessage> chatMessages;
  final bool isChatLoading;
  final String? chatError;
  final ValueChanged<String> onSendChatMessage;

  const _ActiveStudyBuddyContent({
    required this.coachContent,
    required this.chatMessages,
    required this.isChatLoading,
    required this.chatError,
    required this.onSendChatMessage,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final showCoach = constraints.maxHeight >= 180;
        return Column(
          children: [
            if (showCoach) ...[
              Flexible(
                flex: 3,
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 220),
                  child: coachContent,
                ),
              ),
              const SizedBox(height: 12),
            ],
            Expanded(
              flex: showCoach ? 7 : 1,
              child: _ChatSurface(
                messages: chatMessages,
                isLoading: isChatLoading,
                error: chatError,
                onSend: onSendChatMessage,
              ),
            ),
          ],
        );
      },
    );
  }
}

class _ChatSurface extends StatelessWidget {
  final List<StudyBuddyChatMessage> messages;
  final bool isLoading;
  final String? error;
  final ValueChanged<String> onSend;

  const _ChatSurface({
    required this.messages,
    required this.isLoading,
    required this.error,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const ValueKey('study-buddy-chat'),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final showThread = constraints.maxHeight >= 88;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (showThread)
                Expanded(
                  child: messages.isEmpty && !isLoading
                      ? _EmptyChatPrompt()
                      : ListView(
                          reverse: true,
                          padding: EdgeInsets.zero,
                          children: [
                            if (isLoading) const _TypingBubble(),
                            ...messages.reversed.map(_ChatBubble.new),
                          ],
                        ),
                ),
              if (showThread) const SizedBox(height: 10),
              if ((error ?? '').isNotEmpty) ...[
                Text(
                  error!,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.red.shade700,
                        fontWeight: FontWeight.w600,
                      ),
                ),
                const SizedBox(height: 8),
              ],
              _ChatComposer(
                isLoading: isLoading,
                onSend: onSend,
              ),
            ],
          );
        },
      ),
    );
  }
}

class _EmptyChatPrompt extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        'Ask Study Buddy about the current exercise.',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppTheme.textSecondary,
              height: 1.35,
            ),
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final StudyBuddyChatMessage message;

  const _ChatBubble(this.message);

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 260),
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
        decoration: BoxDecoration(
          color: isUser ? AppTheme.primaryBlue : const Color(0xFFF1F5F9),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Text(
          message.content,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: isUser ? Colors.white : AppTheme.textPrimary,
                height: 1.35,
              ),
        ),
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  const _TypingBubble();

  @override
  Widget build(BuildContext context) {
    return const Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.only(bottom: 8),
        child: SizedBox(
          width: 18,
          height: 18,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      ),
    );
  }
}

class _ChatComposer extends StatefulWidget {
  final bool isLoading;
  final ValueChanged<String> onSend;

  const _ChatComposer({
    required this.isLoading,
    required this.onSend,
  });

  @override
  State<_ChatComposer> createState() => _ChatComposerState();
}

class _ChatComposerState extends State<_ChatComposer> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _send() {
    final value = _controller.text.trim();
    if (value.isEmpty || widget.isLoading) {
      return;
    }
    widget.onSend(value);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      key: const ValueKey('study-buddy-chat-input'),
      controller: _controller,
      minLines: 1,
      maxLines: 3,
      enabled: !widget.isLoading,
      textInputAction: TextInputAction.send,
      onSubmitted: (_) => _send(),
      decoration: InputDecoration(
        hintText: 'Ask Study Buddy...',
        isDense: true,
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 11,
        ),
        suffixIcon: IconButton(
          tooltip: 'Send message',
          onPressed: widget.isLoading ? null : _send,
          icon: const Icon(Icons.send_rounded),
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: AppTheme.borderLight),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: AppTheme.borderLight),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: AppTheme.primaryBlue),
        ),
      ),
    );
  }
}

class _InterventionContent extends StatelessWidget {
  final StudyBuddyIntervention intervention;
  final VoidCallback onComplete;

  const _InterventionContent({
    super.key,
    required this.intervention,
    required this.onComplete,
  });

  @override
  Widget build(BuildContext context) {
    final content = intervention.content;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderLight),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              content.title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 10),
            Text(
              content.message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textPrimary,
                    height: 1.45,
                  ),
            ),
            if (content.diagnosticQuestion.isNotEmpty) ...[
              const SizedBox(height: 14),
              Text(
                content.diagnosticQuestion,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ],
            if (content.choices.isNotEmpty) ...[
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: content.choices.take(3).map((choice) {
                  return ActionChip(
                    label: Text(choice),
                    onPressed: onComplete,
                  );
                }).toList(growable: false),
              ),
            ],
            if ((content.checkpoint ?? '').isNotEmpty) ...[
              const SizedBox(height: 14),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.borderLight),
                ),
                child: Text(content.checkpoint!),
              ),
            ],
            const SizedBox(height: 14),
            Text(
              content.nextStep,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onComplete,
              icon: const Icon(Icons.check_rounded),
              label: const Text('Done'),
            ),
          ],
        ),
      ),
    );
  }
}
