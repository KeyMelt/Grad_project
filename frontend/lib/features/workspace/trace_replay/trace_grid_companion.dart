import 'package:flutter/material.dart';

import '../../../core/backend_api.dart';

typedef TraceTagBuilder = Widget Function(String label, Color accent);

class TraceGridCompanion extends StatelessWidget {
  final TraceGridMetadata grid;
  final TraceTagBuilder tagBuilder;

  const TraceGridCompanion({
    super.key,
    required this.grid,
    required this.tagBuilder,
  });

  @override
  Widget build(BuildContext context) {
    final aspectRatio = grid.rows > 0 ? grid.columns / grid.rows : 1.0;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${grid.environment} grid',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: const Color(0xFF93C5FD),
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 10),
          Builder(
            builder: (context) {
              final gridView = GridView.builder(
                physics: const NeverScrollableScrollPhysics(),
                padding: EdgeInsets.zero,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: grid.columns <= 0 ? 1 : grid.columns,
                  childAspectRatio: 1,
                  mainAxisSpacing: 4,
                  crossAxisSpacing: 4,
                ),
                itemCount: grid.cells.length,
                itemBuilder: (context, index) {
                  return _buildGridCell(grid.cells[index]);
                },
              );
              if (grid.columns > 8) {
                const cell = 38.0;
                return SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: SizedBox(
                    width: grid.columns * cell,
                    height: grid.rows * cell,
                    child: gridView,
                  ),
                );
              }
              return AspectRatio(
                aspectRatio: aspectRatio,
                child: gridView,
              );
            },
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _buildTags(),
          ),
        ],
      ),
    );
  }

  Widget _buildGridCell(TraceGridCell cell) {
    final isCurrent = cell.state == grid.state;
    final isNext = grid.nextState != null && cell.state == grid.nextState;
    final baseBorder = _wallBorder(cell);
    final highlightColor = isCurrent
        ? const Color(0xFF60A5FA)
        : isNext
            ? const Color(0xFF2DD4BF)
            : null;
    final borderRadius = grid.isTaxi ? null : BorderRadius.circular(6);
    return Tooltip(
      message: grid.isTaxi
          ? _taxiTooltip(cell)
          : 'State ${cell.state} (${cell.row}, ${cell.column}) | ${_gridTileLabel(cell.tileType)}',
      child: Container(
        decoration: BoxDecoration(
          color: _tileColor(cell, isCurrent),
          borderRadius: borderRadius,
          border: baseBorder,
        ),
        child: Stack(
          children: [
            if (highlightColor != null)
              Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    borderRadius: borderRadius,
                    border: Border.all(color: highlightColor, width: 2),
                  ),
                ),
              ),
            Positioned(
              top: 4,
              left: 4,
              child: Text(
                '${cell.state}',
                style: const TextStyle(
                  color: Color(0xFFE2E8F0),
                  fontSize: 9,
                  fontFamily: 'Courier',
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            Center(
              child: Text(
                isCurrent
                    ? _actionMarker()
                    : isNext
                        ? 'N'
                        : _tileMarker(cell),
                style: TextStyle(
                  color: Colors.white,
                  fontSize: isCurrent ? 18 : 13,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTags() {
    final widgets = <Widget>[
      tagBuilder(
        'state ${grid.isTaxi ? grid.encodedState ?? grid.state : grid.state}',
        const Color(0xFF93C5FD),
      ),
    ];
    if (grid.nextState != null) {
      widgets.add(
        tagBuilder(
          'next ${grid.isTaxi ? grid.encodedNextState ?? grid.nextState : grid.nextState}',
          const Color(0xFF2DD4BF),
        ),
      );
    }
    if (grid.actionLabel.isNotEmpty) {
      widgets.add(tagBuilder(grid.actionLabel, const Color(0xFF06B6D4)));
    }
    if (grid.reward != null) {
      widgets.add(
        tagBuilder(
          'reward ${grid.reward!.toStringAsFixed(2)}',
          grid.reward! < 0
              ? const Color(0xFFF87171)
              : const Color(0xFFFBBF24),
        ),
      );
    }
    if (grid.terminated || grid.truncated) {
      widgets.add(
        tagBuilder(
          grid.terminated ? 'terminal' : 'truncated',
          const Color(0xFFF87171),
        ),
      );
    }
    if (!grid.isTaxi) {
      return widgets;
    }

    final passenger = grid.passenger;
    final destination = grid.destination;
    if (passenger != null) {
      widgets.add(
        tagBuilder(
          passenger.inTaxi ? 'passenger aboard' : 'passenger @ ${passenger.location}',
          const Color(0xFFA78BFA),
        ),
      );
    }
    if (destination != null) {
      widgets.add(tagBuilder('dest ${destination.label}', const Color(0xFF34D399)));
    }

    final nextPassenger = grid.nextPassenger;
    if (grid.actionLabel == 'Pickup' &&
        passenger != null &&
        nextPassenger != null &&
        !passenger.inTaxi &&
        nextPassenger.inTaxi) {
      widgets.add(tagBuilder('pickup success', const Color(0xFF22C55E)));
    } else if (grid.actionLabel == 'Dropoff' &&
        passenger != null &&
        nextPassenger != null &&
        passenger.inTaxi &&
        !nextPassenger.inTaxi &&
        (grid.reward ?? 0) > 0) {
      widgets.add(tagBuilder('dropoff success', const Color(0xFF22C55E)));
    } else if ((grid.reward ?? 0) <= -10 &&
        (grid.actionLabel == 'Pickup' || grid.actionLabel == 'Dropoff')) {
      widgets.add(
        tagBuilder(
          'illegal ${grid.actionLabel.toLowerCase()}',
          const Color(0xFFF87171),
        ),
      );
    }

    return widgets;
  }

  Border _wallBorder(TraceGridCell cell) {
    const edge = BorderSide(color: Color(0xFF334155), width: 1);
    if (!grid.isTaxi || grid.walls.isEmpty) {
      return const Border.fromBorderSide(edge);
    }

    BorderSide left = edge;
    BorderSide right = edge;
    BorderSide top = edge;
    BorderSide bottom = edge;

    for (final wall in grid.walls) {
      final start = wall.start;
      final end = wall.end;
      if (start.row == end.row && (start.column - end.column).abs() == 1) {
        final wallColumn = start.column < end.column ? start.column : end.column;
        if (cell.row == start.row && cell.column == wallColumn) {
          right = const BorderSide(color: Color(0xFFF87171), width: 3);
        }
        if (cell.row == start.row && cell.column == wallColumn + 1) {
          left = const BorderSide(color: Color(0xFFF87171), width: 3);
        }
      } else if (start.column == end.column && (start.row - end.row).abs() == 1) {
        final wallRow = start.row < end.row ? start.row : end.row;
        if (cell.column == start.column && cell.row == wallRow) {
          bottom = const BorderSide(color: Color(0xFFF87171), width: 3);
        }
        if (cell.column == start.column && cell.row == wallRow + 1) {
          top = const BorderSide(color: Color(0xFFF87171), width: 3);
        }
      }
    }

    return Border(left: left, right: right, top: top, bottom: bottom);
  }

  Color _tileColor(TraceGridCell cell, bool isCurrent) {
    if (!grid.isTaxi) {
      final isCliff = cell.tileType == 'C';
      final isHole = cell.tileType == 'H';
      final isGoal = cell.tileType == 'G';
      return isCliff || isHole
          ? const Color(0xFF7F1D1D)
          : isGoal
              ? const Color(0xFF065F46)
              : cell.tileType == 'S'
                  ? const Color(0xFF1E3A8A)
                  : const Color(0xFF1E293B);
    }

    final destination = grid.destination;
    if (destination != null &&
        cell.row == destination.row &&
        cell.column == destination.column) {
      return const Color(0xFF065F46);
    }
    final passenger = grid.passenger;
    if (passenger != null &&
        !passenger.inTaxi &&
        cell.row == passenger.row &&
        cell.column == passenger.column) {
      return const Color(0xFF4C1D95);
    }
    const locationColors = {
      'R': Color(0xFF7F1D1D),
      'G': Color(0xFF14532D),
      'Y': Color(0xFF713F12),
      'B': Color(0xFF1E3A5F),
    };
    if (isCurrent) {
      return const Color(0xFF1E293B);
    }
    return locationColors[cell.tileType] ?? const Color(0xFF1E293B);
  }

  String _actionMarker() {
    return switch (grid.actionLabel) {
      'Up' || 'North' => '↑',
      'Right' || 'East' => '→',
      'Down' || 'South' => '↓',
      'Left' || 'West' => '←',
      'Pickup' => '⬆',
      'Dropoff' => '⬇',
      _ => 'A',
    };
  }

  String _tileMarker(TraceGridCell cell) {
    if (!grid.isTaxi) {
      return switch (cell.tileType) {
        'S' => 'S',
        'G' => 'G',
        'H' => 'H',
        'C' => '!',
        _ => '',
      };
    }

    final destination = grid.destination;
    if (destination != null &&
        cell.row == destination.row &&
        cell.column == destination.column) {
      return '⊕';
    }
    final passenger = grid.passenger;
    if (passenger != null &&
        !passenger.inTaxi &&
        cell.row == passenger.row &&
        cell.column == passenger.column) {
      return '●';
    }
    if (cell.tileType != 'F') {
      return cell.tileType;
    }
    return '';
  }

  String _taxiTooltip(TraceGridCell cell) {
    final parts = <String>['(${cell.row}, ${cell.column})'];
    if (cell.tileType != 'F') {
      parts.add('pickup ${cell.tileType}');
    }
    final destination = grid.destination;
    if (destination != null &&
        cell.row == destination.row &&
        cell.column == destination.column) {
      parts.add('destination ${destination.label}');
    }
    final passenger = grid.passenger;
    if (passenger != null &&
        !passenger.inTaxi &&
        cell.row == passenger.row &&
        cell.column == passenger.column) {
      parts.add('passenger');
    }
    return parts.join(' | ');
  }

  String _gridTileLabel(String tileType) {
    return switch (tileType) {
      'S' => 'start',
      'G' => 'goal',
      'H' => 'hole',
      'C' => 'cliff',
      'F' => 'frozen/safe',
      _ => tileType.isEmpty ? 'empty' : tileType,
    };
  }
}
