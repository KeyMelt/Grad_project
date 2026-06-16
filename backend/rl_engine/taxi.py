from __future__ import annotations

from typing import Any

TAXI_ACTION_LABELS = {
    0: "South",
    1: "North",
    2: "East",
    3: "West",
    4: "Pickup",
    5: "Dropoff",
}

_TAXI_LOCATION_ORDER = ("R", "G", "Y", "B")
_TAXI_LOCATIONS = {
    "R": (0, 0),
    "G": (0, 4),
    "Y": (4, 0),
    "B": (4, 3),
}
_TAXI_WALL_SEGMENTS = (
    {"start": {"row": 0, "column": 1}, "end": {"row": 0, "column": 2}},
    {"start": {"row": 1, "column": 1}, "end": {"row": 1, "column": 2}},
    {"start": {"row": 3, "column": 0}, "end": {"row": 3, "column": 1}},
    {"start": {"row": 4, "column": 0}, "end": {"row": 4, "column": 1}},
    {"start": {"row": 3, "column": 2}, "end": {"row": 3, "column": 3}},
    {"start": {"row": 4, "column": 2}, "end": {"row": 4, "column": 3}},
)


def decode_taxi_state(encoded_state: int) -> tuple[int, int, int, int]:
    destination_index = encoded_state % 4
    remaining = encoded_state // 4
    passenger_index = remaining % 5
    remaining //= 5
    taxi_column = remaining % 5
    taxi_row = remaining // 5
    return taxi_row, taxi_column, passenger_index, destination_index


def taxi_grid_metadata(
    *,
    state: int,
    next_state: int | None = None,
    action: int | None = None,
    reward: float | None = None,
    terminated: bool = False,
    truncated: bool = False,
) -> dict[str, Any]:
    taxi_row, taxi_column, passenger_index, destination_index = decode_taxi_state(int(state))
    next_taxi_row, next_taxi_column, next_passenger_index, _ = (
        decode_taxi_state(int(next_state))
        if next_state is not None
        else (None, None, None, None)
    )
    destination_label = _TAXI_LOCATION_ORDER[destination_index]
    destination_row, destination_column = _TAXI_LOCATIONS[destination_label]
    current_passenger = _taxi_passenger(
        passenger_index=passenger_index,
        taxi_row=taxi_row,
        taxi_column=taxi_column,
    )
    next_passenger = (
        None
        if next_passenger_index is None or next_taxi_row is None or next_taxi_column is None
        else _taxi_passenger(
            passenger_index=next_passenger_index,
            taxi_row=next_taxi_row,
            taxi_column=next_taxi_column,
        )
    )

    return {
        "environment": "Taxi",
        "rows": 5,
        "columns": 5,
        "cells": _taxi_cells(),
        "state": taxi_row * 5 + taxi_column,
        "next_state": (
            None
            if next_taxi_row is None or next_taxi_column is None
            else next_taxi_row * 5 + next_taxi_column
        ),
        "encoded_state": int(state),
        "encoded_next_state": None if next_state is None else int(next_state),
        "state_coordinates": {"row": taxi_row, "column": taxi_column},
        "next_state_coordinates": (
            None
            if next_taxi_row is None or next_taxi_column is None
            else {"row": next_taxi_row, "column": next_taxi_column}
        ),
        "passenger": current_passenger,
        "next_passenger": next_passenger,
        "destination": {
            "label": destination_label,
            "row": destination_row,
            "column": destination_column,
        },
        "walls": list(_TAXI_WALL_SEGMENTS),
        "action": action,
        "action_label": None if action is None or action < 0 else TAXI_ACTION_LABELS.get(action),
        "reward": None if reward is None else round(float(reward), 4),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
    }


def _taxi_cells() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    location_lookup = {coords: label for label, coords in _TAXI_LOCATIONS.items()}
    for row in range(5):
        for column in range(5):
            tile_type = location_lookup.get((row, column), "F")
            cells.append(
                {
                    "state": row * 5 + column,
                    "row": row,
                    "column": column,
                    "tile_type": tile_type,
                    "terminal": False,
                }
            )
    return cells


def _taxi_passenger(
    *,
    passenger_index: int,
    taxi_row: int,
    taxi_column: int,
) -> dict[str, Any]:
    if passenger_index < len(_TAXI_LOCATION_ORDER):
        label = _TAXI_LOCATION_ORDER[passenger_index]
        row, column = _TAXI_LOCATIONS[label]
        return {
            "location": label,
            "row": row,
            "column": column,
            "in_taxi": False,
        }

    return {
        "location": "in_taxi",
        "row": taxi_row,
        "column": taxi_column,
        "in_taxi": True,
    }
