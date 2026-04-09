import 'dart:io';

import 'export_file_saver_types.dart';

Future<ExportSaveResult> saveExportFile({
  required String fileName,
  required List<int> bytes,
}) async {
  try {
    final homePath = Platform.environment['HOME'];
    final downloadDir =
        homePath == null ? Directory.current : Directory('$homePath/Downloads');

    if (!downloadDir.existsSync()) {
      downloadDir.createSync(recursive: true);
    }

    final outputFile = File('${downloadDir.path}/$fileName');
    await outputFile.writeAsBytes(bytes, flush: true);
    return ExportSaveResult(
      success: true,
      message: 'Excel export saved.',
      savedPath: outputFile.path,
    );
  } catch (error) {
    return ExportSaveResult(
      success: false,
      message: 'Could not save export file: $error',
    );
  }
}
