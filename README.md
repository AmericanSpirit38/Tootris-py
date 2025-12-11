# Tootris-py

A Tetris-like game built with Python and the Arcade library.

## Overview

- Python (100%)
- Main game logic isin `Game.py`. The game uses `arcade.View` for screens (e.g., Start, Game Over) and manages active/inactive piece grids, line clearing, scoring, and game state transitions.
- High scores are persisted to `score.json`.

## Installation

1. Ensure you have Python 3.9+ installed.
2. Install dependencies:
   ```bash
   pip install arcade
   ```
   If other dependencies are required, add them here or to a `requirements.txt`.

## Running the Game

From the repository root:
```bash
python Game.py
```

This will open a window and show the start screen. From there, you can begin playing.

## Controls

- Left Arrow: Move piece left
- Right Arrow: Move piece right
- Down Arrow: Soft drop
- Up Arrow: Rotate piece
- Q: Rotate piece left
- E: Rotate piece right
- Space: Hard drop (calls `drop()`)

## Scoring

- Lines cleared are detected after a piece locks.
- Score increments via `Logic.SetScore(lines)`.
- High score is stored in `score.json`. On game over, if the current score exceeds the stored high score, `score.json` is updated.

## Game Over

- When pieces stack into the top rows (0 or 1), the game ends.
- The Game Over view displays your final score and maintains a high score.

## Project Structure

- `Game.py`: Main game logic, views, and entry points (`start`, `main`, `game_over`).
- `score.json`: High score persistence file (created/updated at runtime).

## Requirements

- Python
- Arcade
