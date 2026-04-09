import 'export_file_saver_types.dart';

Future<ExportSaveResult> saveExportFile({
  required String fileName,
  required List<int> bytes,
}) async {
  return const ExportSaveResult(
    success: false,
    message: 'File export is not supported on this platform.',
  );
}
