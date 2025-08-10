#!/usr/bin/env python3
"""
Difficulty presets for Minisweeper.

Provides a simple API:
- get_difficulty(name) -> Difficulty
- list_difficulties() -> dict[name, Difficulty]
- normalize_name(name) -> canonical key

Levels:
- easy:    9x9, 10 mines
- medium:  16x16, 40 mines
- hard:    30x16, 99 mines
- too hard: 30x24, 180 mines
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Difficulty:
    name: str
    width: int
    height: int
    mines: int


_LEVELS: Dict[str, Difficulty] = {
    "easy": Difficulty("easy", 9, 9, 10),
    "medium": Difficulty("medium", 16, 16, 40),
    "hard": Difficulty("hard", 30, 16, 99),
    "too hard": Difficulty("too hard", 30, 24, 180),
}


def normalize_name(name: str) -> str:
    key = name.strip().lower().replace("_", " ").replace("-", " ")
    # collapse multiple spaces
    key = " ".join(part for part in key.split() if part)
    return key


def get_difficulty(name: str) -> Difficulty:
    key = normalize_name(name)
    if key not in _LEVELS:
        raise ValueError(f"Unknown difficulty: {name}. Available: {', '.join(sorted(_LEVELS))}")
    return _LEVELS[key]


def list_difficulties() -> Dict[str, Difficulty]:
    return dict(_LEVELS)
