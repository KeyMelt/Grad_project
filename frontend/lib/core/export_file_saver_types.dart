class ExportSaveResult {
  final bool success;
  final String message;
  final String? savedPath;

  const ExportSaveResult({
    required this.success,
    required this.message,
    this.savedPath,
  });
}
