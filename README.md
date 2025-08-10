# Minisweeper (Terminal)

A tiny terminal Minesweeper clone written in pure Python 3. No external dependencies.

## Features
- Configurable width, height, and mine count
- First move is always safe (never a mine)
- Flood fill reveal of zero-adjacent-mine cells
- Flag/unflag cells
- Win/lose detection
- Simple, readable code

## How to run
Requires Python 3.8+ (standard library only).

```powershell
# With custom board (e.g., 9x9 with 10 mines)
python -m minisweeper  --width 9 --height 9 --mines 10
```

### GUI (Tkinter)
A simple Tk GUI is included. Left click to reveal; right click to flag.

```powershell
Run:
    python -m game 

Controls:
    Reveal: r x y
    Flag: f x y
    Help: h
    Quit: q