#!/usr/bin/env python3
"""
Tkinter GUI for Minisweeper.

Usage:
  python gui_tk.py [--width W] [--height H] [--mines M]

Left click: reveal
Right click: flag/unflag
"""
from __future__ import annotations
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Tuple

from minisweeper import Board
from difficulty import get_difficulty, list_difficulties

# UI constants
GAME_OVER_TITLE = "Game Over"
WIN_TITLE = "You Win!"
MINE_HIT_MSG = "Boom! You hit a mine."
WIN_MSG = "All safe cells revealed."


NUM_COLORS = {
    1: "#1976d2",  # blue
    2: "#388e3c",  # green
    3: "#d32f2f",  # red
    4: "#7b1fa2",  # purple
    5: "#5d4037",  # brown
    6: "#0097a7",  # cyan-ish
    7: "#455a64",  # blue grey
    8: "#000000",  # black
}


class MinesweeperApp(tk.Tk):
    def __init__(self, width: int = 9, height: int = 9, mines: int = 10):
        super().__init__()
        self.title("Minisweeper (Tk)")
        self.resizable(False, False)

        self.board: Board | None = None
        self.buttons: Dict[Tuple[int, int], tk.Button] = {}
        self.game_over: bool = False

        # Top controls
        top = ttk.Frame(self, padding=(8, 8))
        top.grid(row=0, column=0, sticky="ew")

        # Difficulty chooser
        ttk.Label(top, text="Difficulty:").grid(row=0, column=0, padx=(0, 4))
        self.diff_var = tk.StringVar(value="custom")
        diff_values = ["custom"] + sorted(list_difficulties().keys())
        self.diff_combo = ttk.Combobox(
            top, textvariable=self.diff_var, values=diff_values, width=10, state="readonly"
        )
        self.diff_combo.grid(row=0, column=1, padx=(0, 12))
        self.diff_combo.bind("<<ComboboxSelected>>", self.on_difficulty_changed)

        ttk.Label(top, text="Width:").grid(row=0, column=2, padx=(0, 4))
        self.width_var = tk.IntVar(value=width)
        w_spin = ttk.Spinbox(top, from_=2, to=60, textvariable=self.width_var, width=5)
        w_spin.grid(row=0, column=3, padx=(0, 8))

        ttk.Label(top, text="Height:").grid(row=0, column=4, padx=(0, 4))
        self.height_var = tk.IntVar(value=height)
        h_spin = ttk.Spinbox(top, from_=2, to=40, textvariable=self.height_var, width=5)
        h_spin.grid(row=0, column=5, padx=(0, 8))

        ttk.Label(top, text="Mines:").grid(row=0, column=6, padx=(0, 4))
        self.mines_var = tk.IntVar(value=mines)
        m_spin = ttk.Spinbox(top, from_=1, to=2000, textvariable=self.mines_var, width=6)
        m_spin.grid(row=0, column=7, padx=(0, 8))

        ttk.Button(top, text="New", command=self.new_game_from_inputs).grid(row=0, column=8, padx=(0, 8))
        ttk.Button(top, text="Reset", command=self.reset_game).grid(row=0, column=9)

        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self, textvariable=self.status_var, padding=(8, 0))
        status.grid(row=2, column=0, sticky="w")

        # Board frame
        self.board_frame = ttk.Frame(self, padding=(8, 8))
        self.board_frame.grid(row=1, column=0)

        self.new_game(width, height, mines)

    # --- Game management ---
    def new_game_from_inputs(self):
        # Use difficulty if selected; otherwise use custom inputs
        diff_name = self.diff_var.get().strip().lower()
        if diff_name != "custom":
            try:
                diff = get_difficulty(diff_name)
            except Exception as e:
                messagebox.showerror("Invalid difficulty", str(e))
                return
            w, h, m = diff.width, diff.height, diff.mines
        else:
            try:
                w = int(self.width_var.get())
                h = int(self.height_var.get())
                m = int(self.mines_var.get())
            except Exception:
                messagebox.showerror("Invalid input", "Width, height, and mines must be integers.")
                return
        self.new_game(w, h, m)

    def reset_game(self):
        if self.board is None:
            return
        self.new_game(self.board.w, self.board.h, self.board.mine_target)

    def on_difficulty_changed(self, event=None):
        name = self.diff_var.get()
        if name and name.lower() != "custom":
            try:
                d = get_difficulty(name)
            except Exception:
                return
            # Update spinboxes to reflect preset
            self.width_var.set(d.width)
            self.height_var.set(d.height)
            self.mines_var.set(d.mines)

    def new_game(self, width: int, height: int, mines: int):
        try:
            self.board = Board(width, height, mines)
        except Exception as e:
            messagebox.showerror("New Game Error", str(e))
            return
        self.game_over = False
        self._build_grid()
        self._update_status()

    # --- UI construction ---
    def _build_grid(self):
        # Clear previous
        for child in self.board_frame.winfo_children():
            child.destroy()
        self.buttons.clear()

        assert self.board is not None
        for y in range(self.board.h):
            for x in range(self.board.w):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    width=2,
                    height=1,
                    font=("Segoe UI", 12, "bold"),
                    relief=tk.RAISED,
                )
                btn.grid(row=y, column=x, padx=1, pady=1, sticky="nsew")
                # Left click reveal
                btn.bind("<Button-1>", lambda e, x=x, y=y: self.on_left_click(x, y))
                # Right click flag (support Button-2 for some platforms)
                btn.bind("<Button-3>", lambda e, x=x, y=y: self.on_right_click(x, y))
                btn.bind("<Button-2>", lambda e, x=x, y=y: self.on_right_click(x, y))
                # Double-click chord (optional convenience)
                btn.bind("<Double-Button-1>", lambda e, x=x, y=y: self.on_chord(x, y))
                self.buttons[(x, y)] = btn

        # Make columns/rows expand evenly inside board_frame (optional visual)
        for x in range(self.board.w):
            self.board_frame.grid_columnconfigure(x, weight=1)
        for y in range(self.board.h):
            self.board_frame.grid_rowconfigure(y, weight=1)

        self._refresh_cells()

    # --- Events ---
    def on_left_click(self, x: int, y: int):
        if self.game_over or self.board is None:
            return
        cell = self.board.grid[y][x]
        ok, hit = self.board.reveal(x, y)
        if not ok and cell.revealed and not cell.mine:
            # Treat click on number as chord attempt
            self.on_chord(x, y)
            return
        if hit:
            self.game_over = True
            self._reveal_all()
            self._refresh_cells()
            messagebox.showinfo(GAME_OVER_TITLE, MINE_HIT_MSG)
            return
        if self.board.all_safe_revealed():
            self.game_over = True
            self._reveal_all()
            self._refresh_cells()
            messagebox.showinfo(WIN_TITLE, WIN_MSG)
            return
        self._refresh_cells()

    def on_right_click(self, x: int, y: int):
        if self.game_over or self.board is None:
            return
        if self.board.toggle_flag(x, y):
            self._refresh_cells()
            self._update_status()

    def on_chord(self, x: int, y: int):
        if self.game_over or self.board is None:
            return
        c = self.board.grid[y][x]
        if not c.revealed or c.adj <= 0:
            return
        flagged = 0
        for nx, ny in self.board.neighbors(x, y):
            if self.board.grid[ny][nx].flagged:
                flagged += 1
        if flagged != c.adj:
            return
        # Reveal all neighboring non-flagged cells
        for nx, ny in self.board.neighbors(x, y):
            ncell = self.board.grid[ny][nx]
            if not ncell.flagged and not ncell.revealed:
                _, hit = self.board.reveal(nx, ny)
                if hit:
                    self.game_over = True
                    self._reveal_all()
                    self._refresh_cells()
                    messagebox.showinfo(GAME_OVER_TITLE, MINE_HIT_MSG)
                    return
        if self.board.all_safe_revealed():
            self.game_over = True
            self._reveal_all()
            self._refresh_cells()
            messagebox.showinfo(WIN_TITLE, WIN_MSG)
            return
        self._refresh_cells()

    # --- Rendering ---
    def _reveal_all(self):
        # Only affects rendering; Board already exposes data
        pass  # nothing needed; _refresh_cells reads from board state

    def _refresh_cells(self):
        assert self.board is not None
        for y in range(self.board.h):
            for x in range(self.board.w):
                btn = self.buttons[(x, y)]
                c = self.board.grid[y][x]
                if self.game_over:
                    # Show mines and final state
                    if c.mine:
                        btn.config(text="*", fg="#000", bg="#ffcccb", relief=tk.SUNKEN, state=tk.DISABLED)
                    else:
                        self._render_safe_cell(btn, c)
                else:
                    if c.flagged and not c.revealed:
                        btn.config(text="F", fg="#d32f2f", bg="#ffe0b2", relief=tk.RAISED, state=tk.NORMAL)
                    elif not c.revealed:
                        btn.config(text="", fg="#000", bg="#e0e0e0", relief=tk.RAISED, state=tk.NORMAL)
                    else:
                        self._render_safe_cell(btn, c)
        self._update_status()

    def _render_safe_cell(self, btn: tk.Button, cell):
        if cell.mine:
            btn.config(text="*", fg="#000", bg="#ffcccb", relief=tk.SUNKEN, state=tk.DISABLED)
            return
        if cell.adj == 0:
            btn.config(text="", fg="#000", bg="#cfd8dc", relief=tk.SUNKEN, state=tk.DISABLED)
        else:
            color = NUM_COLORS.get(cell.adj, "#000")
            btn.config(text=str(cell.adj), fg=color, bg="#cfd8dc", relief=tk.SUNKEN, state=tk.DISABLED)

    def _update_status(self):
        if self.board is None:
            self.status_var.set("")
            return
        flags = sum(
            1
            for y in range(self.board.h)
            for x in range(self.board.w)
            if self.board.grid[y][x].flagged
        )
        rem = max(0, self.board.mine_target - flags)
        state = GAME_OVER_TITLE if self.game_over else "Playing"
        self.status_var.set(
            f"Mines: {self.board.mine_target}  Flags: {flags}  Remaining: {rem}  |  {state}"
        )


def parse_args():
    ap = argparse.ArgumentParser(description="Minisweeper Tk GUI")
    ap.add_argument("--width", type=int, default=9)
    ap.add_argument("--height", type=int, default=9)
    ap.add_argument("--mines", type=int, default=10)
    return ap.parse_args()


def main():
    ns = parse_args()
    app = MinesweeperApp(ns.width, ns.height, ns.mines)
    app.mainloop()


if __name__ == "__main__":
    main()
