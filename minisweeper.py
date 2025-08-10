#!/usr/bin/env python3
"""
Minisweeper - a minimal terminal Minesweeper clone.

Usage:
    python minisweeper.py [--width W] [--height H] [--mines M]

Controls:
    r x y   reveal cell (x,y)
    f x y   flag/unflag cell (x,y)
    h       help
    q       quit

Coordinates are 0-indexed. x is column, y is row.
"""
from __future__ import annotations
import argparse
import random
from dataclasses import dataclass
from typing import List, Tuple, Iterable


@dataclass
class Cell:
    mine: bool = False
    revealed: bool = False
    flagged: bool = False
    adj: int = 0  # adjacent mines


class Board:
    def __init__(self, width: int, height: int, mines: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        max_mines = width * height - 1  # leave at least one safe
        if not (0 < mines <= max_mines):
            raise ValueError(f"mines must be 1..{max_mines}")
        self.w = width
        self.h = height
        self.mine_target = mines
        self.grid: List[List[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]
        self.mines_placed = False
        self.revealed_count = 0

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def neighbors(self, x: int, y: int) -> Iterable[Tuple[int, int]]:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    yield nx, ny

    def place_mines_excluding(self, safe_x: int, safe_y: int) -> None:
        """Place mines randomly, avoiding the first clicked cell and its neighbors for fairness."""
        all_coords = [(x, y) for y in range(self.h) for x in range(self.w)]
        # Exclude the safe cell and its neighbors
        excluded = {(safe_x, safe_y), *self.neighbors(safe_x, safe_y)}
        candidates = [c for c in all_coords if c not in excluded]
        if len(candidates) < self.mine_target:
            # Fallback: if board is very small, at least exclude the first cell
            candidates = [(x, y) for (x, y) in all_coords if (x, y) != (safe_x, safe_y)]
        mines = random.sample(candidates, self.mine_target)
        for x, y in mines:
            self.grid[y][x].mine = True
        # compute adjacencies
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x].mine:
                    continue
                self.grid[y][x].adj = sum(1 for nx, ny in self.neighbors(x, y) if self.grid[ny][nx].mine)
        self.mines_placed = True

    def reveal(self, x: int, y: int) -> Tuple[bool, bool]:
        """Reveal a cell. Returns (ok, hit_mine). ok=False if invalid move.
        Performs flood fill for zero-adjacent cells.
        """
        if not self.in_bounds(x, y):
            return False, False
        cell = self.grid[y][x]
        if cell.flagged:
            return False, False
        if cell.revealed:
            # Idempotent reveal: allowed and not a mine
            return True, False
        if not self.mines_placed:
            self.place_mines_excluding(x, y)
        cell.revealed = True
        self.revealed_count += 1
        if cell.mine:
            return True, True
        if cell.adj == 0:
            # flood fill
            stack = [(x, y)]
            visited = set(stack)
            while stack:
                cx, cy = stack.pop()
                for nx, ny in self.neighbors(cx, cy):
                    ncell = self.grid[ny][nx]
                    if ncell.revealed or ncell.flagged:
                        continue
                    if ncell.mine:
                        continue
                    ncell.revealed = True
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                    self.revealed_count += 1
                    if ncell.adj == 0:
                        stack.append((nx, ny))
        return True, False

    def toggle_flag(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        cell = self.grid[y][x]
        if cell.revealed:
            return False
        cell.flagged = not cell.flagged
        return True

    def all_safe_revealed(self) -> bool:
        total_cells = self.w * self.h
        return self.revealed_count == total_cells - self.mine_target

    def render(self, reveal_all: bool = False) -> str:
        # header
        header = "   " + " ".join(f"{x:2d}" for x in range(self.w))
        lines = [header]
        for y in range(self.h):
            row = [f"{y:2d}"]
            for x in range(self.w):
                c = self.grid[y][x]
                ch = "#"
                if reveal_all:
                    if c.mine:
                        ch = "*"
                    elif c.adj == 0:
                        ch = "."
                    else:
                        ch = str(c.adj)
                else:
                    if c.flagged and not c.revealed:
                        ch = "F"
                    elif not c.revealed:
                        ch = "#"
                    else:
                        if c.mine:
                            ch = "*"
                        elif c.adj == 0:
                            ch = "."
                        else:
                            ch = str(c.adj)
                row.append(f" {ch:2s}")
            lines.append(" ".join(row))
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minisweeper - tiny terminal Minesweeper")
    p.add_argument("--width", type=int, default=9)
    p.add_argument("--height", type=int, default=9)
    p.add_argument("--mines", type=int, default=10)
    return p.parse_args()


def print_help() -> None:
    print("Commands:")
    print("  r x y   reveal cell (x,y)")
    print("  f x y   flag/unflag cell (x,y)")
    print("  h       help")
    print("  q       quit")


def main() -> None:
    ns = parse_args()
    random.seed()
    board = Board(ns.width, ns.height, ns.mines)
    print("Minisweeper - type 'h' for help. Coordinates are 0-indexed (x y).\n")
    while True:
        print(board.render())
        cmd = input("> ").strip()
        if not cmd:
            continue
        if cmd.lower() in {"q", "quit", "exit"}:
            print("Bye!")
            return
        if cmd.lower() in {"h", "help"}:
            print_help()
            continue
        parts = cmd.split()
        if parts and parts[0].lower() in {"r", "f"}:
            if len(parts) != 3:
                print("Invalid format. Use: r x y or f x y")
                continue
            try:
                x, y = int(parts[1]), int(parts[2])
            except ValueError:
                print("x and y must be integers")
                continue
            if parts[0].lower() == "f":
                if not board.toggle_flag(x, y):
                    print("Can't flag there.")
                continue
            ok, hit = board.reveal(x, y)
            if not ok:
                print("Can't reveal there.")
                continue
            if hit:
                print(board.render(reveal_all=True))
                print("Boom! You hit a mine.")
                return
            if board.all_safe_revealed():
                print(board.render(reveal_all=True))
                print("You win! All safe cells revealed.")
                return
        else:
            print("Unknown command. Type 'h' for help.")


if __name__ == "__main__":
    main()
