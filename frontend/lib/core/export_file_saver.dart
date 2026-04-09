import 'export_file_saver_types.dart';
import 'export_file_saver_impl_stub.dart'
    if (dart.library.io) 'export_file_saver_impl_io.dart'
    if (dart.library.html) 'export_file_saver_impl_web.dart' as impl;

Future<ExportSaveResult> saveExportFile({
  required String fileName,
  required List<int> bytes,
}) {
  return impl.saveExportFile(
    fileName: fileName,
    bytes: bytes,
  );
}
