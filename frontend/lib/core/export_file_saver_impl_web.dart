// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use

import 'dart:html' as html;

import 'export_file_saver_types.dart';

Future<ExportSaveResult> saveExportFile({
  required String fileName,
  required List<int> bytes,
}) async {
  try {
    final blob = html.Blob([bytes]);
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.AnchorElement(href: url)
      ..download = fileName
      ..style.display = 'none';

    html.document.body?.children.add(anchor);
    anchor.click();
    anchor.remove();
    html.Url.revokeObjectUrl(url);

    return const ExportSaveResult(
      success: true,
      message: 'Excel export downloaded through the browser.',
    );
  } catch (error) {
    return ExportSaveResult(
      success: false,
      message: 'Could not download export file: $error',
    );
  }
}
