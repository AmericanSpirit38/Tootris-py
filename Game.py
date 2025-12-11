import random
from pyglet.graphics import Batch
# Import the arcade library for game development
import arcade
# Import a script that handles game logic
import Logic

# Window configuration
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Tootris"

class StartScreen(arcade.View):
    """
    Start screen view for the game.
    """

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.title_pos = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50)
        self.instruction_pos = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50)
    def on_draw(self) -> bool | None:
        self.clear()
        batch = Batch()
        title_text = "Tootris"
        instruction_text = "Press P to Play"
        text_1 = arcade.Text(title_text, self.title_pos[0], self.title_pos[1],
                             arcade.color.WHITE, font_size=50, anchor_x="center", batch=batch)
        text_2 = arcade.Text(instruction_text, self.instruction_pos[0], self.instruction_pos[1],
                             arcade.color.WHITE, font_size=30, anchor_x="center", batch=batch)
        batch.draw()
        text_1.batch = None
        text_2.batch = None
    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.P:
            main()
# Grid dimensions and layout
grid = {
    "rows": 20,
    "columns": 10,
    "cell_size": 36,
    "margin": 5,
    "top_offset": 50,
    "left_offset": 50,
}

# Block presets defined as local offsets (col_offset, row_offset) from an origin
block_presets = {
    "I": [(0, 0), (-1, 0), (-2, 0), (1, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
}

block_rotations = {
    "I": [ [(0,0), (-1,0), (-2,0), (1,0)],
           [(0,0), (0,-1), (0,-2), (0,1)] ],
    "O": [ [(0,0), (1,0), (0,1), (1,1)] ],
    "T": [ [(0,0), (1,0), (2,0), (1,1)],
           [(1,0), (1,1), (1,2), (0,1)],
           [(0,1), (1,1), (2,1), (1,0)],
           [(1,0), (1,1), (1,2), (2,1)] ],
    "S": [ [(1,0), (2,0), (0,1), (1,1)],
           [(0,0), (0,1), (1,1), (1,2)] ],
}

score = 0

class TootrisGame(arcade.View):
    """
    Main game view containing the game rendering, controls and block movements.
    """

    def __init__(self):
        super().__init__()
        # Set background color
        self.background_color = arcade.color.BLACK

        # Active piece cells: list of \[col, row\]; empty list means no active piece.
        self.active_piece_grid_pos = []

        # Locked cells as a list of tuples in the (collumn, row) format.
        self.inactive_pieces = []

        self.grid_pos = []
        self.setup_grid_pos()

        # Setup time tracking.
        self.second_counter = 0
        self._second_acc = 0.0

        self.current_piece_shape = None

        self.score = 0

        self.score_top_left_pos = (WINDOW_WIDTH - 620, WINDOW_HEIGHT - 40)

        self.game_over = False
        self.game_started = True

        self.spawn()


    def setup_grid_pos(self):
        self.grid_pos = []
        for col in range(grid["columns"]):
            row_list = []
            for row in range(grid["rows"]):
                row_list.append((col, row))
            self.grid_pos.append(row_list)

    def get_grid_dimensions(self):
        """
            Simple function to compute the total width and height of the grid in pixels.
        """
        cs = grid["cell_size"]
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]
        total_w = cols * cs + (cols - 1) * m
        total_h = rows * cs + (rows - 1) * m
        return total_w, total_h

    def get_cell_center(self, col, row):
        """
            Calculate the bottom-left pixel coordinates of a cell given its grid position.
        """
        cs = grid["cell_size"]
        m = grid["margin"]
        left = grid["left_offset"]
        top_gap = grid["top_offset"]
        rows = grid["rows"]

        _, total_h = self.get_grid_dimensions()
        board_bottom = WINDOW_HEIGHT - top_gap - total_h

        cell_left = left + m + col * (cs + m)
        cell_bottom = board_bottom + m + (rows - 1 - row) * (cs + m)
        return cell_left, cell_bottom

    def draw_grid(self):
        """
            Draw the game grid - board background, margin, and all cells.
        """
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]

        total_w, total_h = self.get_grid_dimensions()

        board_left = grid["left_offset"]
        board_top = WINDOW_HEIGHT - grid["top_offset"]
        board_bottom = board_top - total_h

        # Draw board background
        arcade.draw_lbwh_rectangle_filled(
            board_left,
            board_bottom,
            total_w,
            total_h,
            arcade.color.DARK_SLATE_GRAY,
        )
        # Draw margin area
        arcade.draw_lbwh_rectangle_filled(
            board_left + m,
            board_bottom + m,
            total_w - 2 * m,
            total_h - 2 * m,
            arcade.color.GRAY,
        )
        # draw all cells
        inner_width = total_w - 2 * m
        inner_height = total_h - 2 * m
        cell_width = (inner_width - (cols - 1) * m) / cols
        cell_height = (inner_height - (rows - 1) * m) / rows
        for col in range(cols):
            for row in range(rows):
                left = board_left + m + col * (cell_width + m)
                bottom = board_bottom + m + (rows - 1 - row) * (cell_height + m)
                arcade.draw_lbwh_rectangle_filled(
                    left,
                    bottom,
                    cell_width,
                    cell_height,
                    arcade.color.LIGHT_GRAY
                )

    def draw_square(self):
        """
        Draw active pieces as red and inactive(placed) pieces as blue.
        """
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]
        total_w, total_h = self.get_grid_dimensions()
        board_left = grid["left_offset"]
        board_top = WINDOW_HEIGHT - grid["top_offset"]
        board_bottom = board_top - total_h
        inner_width = total_w - 2 * m
        inner_height = total_h - 2 * m
        cell_width = (inner_width - (cols - 1) * m) / cols
        cell_height = (inner_height - (rows - 1) * m) / rows

        def draw_cell(c, r, color):
            # Draw a single cell at grid position (c, r) with the specified color
            left = board_left + m + c * (cell_width + m)
            bottom = board_bottom + m + (rows - 1 - r) * (cell_height + m)
            arcade.draw_lbwh_rectangle_filled(left, bottom, cell_width, cell_height, color)

        # if there is an active piece, draw it
        if self.active_piece_grid_pos:
            for col, row in self.active_piece_grid_pos:
                draw_cell(col, row, arcade.color.RED)
        # if there are inactive pieces, draw them
        if self.inactive_pieces:
            for col, row in self.inactive_pieces:
                draw_cell(col, row, arcade.color.BLUE)
    def draw_score(self):
        """
        Draw the current score on the screen.
        """
        score_text = f"Score: {self.score}"
        top_left_x, top_left_y = self.score_top_left_pos
        batch = Batch()
        text_1 = arcade.Text(score_text, top_left_x, top_left_y, batch=batch)
        # Draw the batch
        batch.draw()
        # Remove a text instance from the batch
        text_1.batch = None
    def reset(self):
        pass

    def on_draw(self):
        # Render the screen.
        self.clear()
        self.draw_grid()
        self.draw_square()
        self.draw_score()

    def on_update(self, delta_time):
        # Check Game Over condition
        if self.game_started:
            if self._check_game_over():
                self.game_over = True
                print("Game Over!")
                game_over(self.score)
                return
        # Update time tracking and move piece down every second, not if manually moved down.
        self._second_acc += delta_time
        while self._second_acc >= 1.0:
            self._second_acc -= 1.0
            self.second_counter += 1
            self.move_down()

    def on_key_press(self, key, modifiers):
        # Handle input to move left
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.move_left()
        # Handle input to move right
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.move_right()
        # Handle input to move down
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.move_down()
            self._second_acc = 0
        # Handle input to rotate piece Left (not implemented)
        if key == arcade.key.Q:
            self.rotate_left()
        # Handle input to rotate piece Right (not implemented)
        elif key == arcade.key.E:
            self.rotate_right()
        # Start the game on P key press
        elif key == arcade.key.P:
            self.game_started = True
            self.spawn()
        # Handle input to hard drop piece
        elif key == arcade.key.SPACE:
            self.drop()

    # Python
    # In `Game.py`, replace these methods:

    def spawn(self, kind=None):
        """
        Spawn a multi-cell piece using `block_rotations` at the top, centered horizontally.
        Tracks rotation index and pivot at offset (0,0).
        """
        if self.game_over:
            return
        if kind is None:
            kind = random.choice(list(block_presets.keys()))

        self.current_piece_shape = kind
        rotations = block_rotations.get(kind, [])
        if not rotations:
            self.active_piece_grid_pos = []
            self.current_rotation_index = None
            self.rotation_origin = None
            return


        # Start with first rotation
        idx = 0
        offsets = rotations[idx]

        # Center horizontally based on offsets span
        min_dx = min(dx for dx, dy in offsets)
        max_dx = max(dx for dx, dy in offsets)
        span = max_dx - min_dx + 1
        start_col = (grid["columns"] - span) // 2 - min_dx
        start_row = 0

        # The pivot is the cell corresponding to offset (0,0)
        pivot_col = start_col
        pivot_row = start_row

        cells = [[pivot_col + dx, pivot_row + dy] for dx, dy in offsets]

        # Validate spawn
        if any(
                c < 0 or c >= grid["columns"] or r < 0 or r >= grid["rows"] or (c, r) in self.inactive_pieces
                for c, r in cells
        ):
            self.active_piece_grid_pos = []
            self.current_rotation_index = None
            self.rotation_origin = None
            return

        self.active_piece_grid_pos = cells
        self.current_rotation_index = idx
        self.rotation_origin = (pivot_col, pivot_row)

    def _apply_move(self, dcol, drow):
        """
        Apply movement vector to all active cells and move the rotation pivot.
        """
        self.active_piece_grid_pos = [[c + dcol, r + drow] for c, r in self.active_piece_grid_pos]
        if getattr(self, "rotation_origin", None) is not None:
            oc, orow = self.rotation_origin
            self.rotation_origin = (oc + dcol, orow + drow)

    def rotate_left(self):
        """
        Rotate the active piece left using `block_rotations` and a tracked pivot.
        Applies simple wall-kicks if needed.
        """
        rotations = block_rotations.get(self.current_piece_shape, [])
        if not rotations or not self.active_piece_grid_pos:
            return

        # Require a tracked index and pivot; if missing, try to initialize
        if getattr(self, "current_rotation_index", None) is None or getattr(self, "rotation_origin", None) is None:
            # Fallback: assume current is index 0 and infer pivot as the cell closest to the origin by matching (0,0)
            # Find a cell that could be the pivot by checking which cell minus offsets matches the set
            current_set = {tuple(p) for p in self.active_piece_grid_pos}
            inferred_idx = None
            inferred_pivot = None
            for idx, pattern in enumerate(rotations):
                for oc, orow in self.active_piece_grid_pos:
                    mapped = {(oc + dx, orow + dy) for dx, dy in pattern}
                    if mapped == current_set:
                        inferred_idx = idx
                        inferred_pivot = (oc, orow)
                        break
                if inferred_idx is not None:
                    break
            if inferred_idx is None:
                # As last resort, treat first cell as pivot and index 0
                inferred_idx = 0
                oc, orow = self.active_piece_grid_pos[0]
                inferred_pivot = (oc, orow)

            self.current_rotation_index = inferred_idx
            self.rotation_origin = inferred_pivot

        cur_idx = self.current_rotation_index
        pivot_col, pivot_row = self.rotation_origin

        next_idx = (cur_idx - 1) % len(rotations)
        new_offsets = rotations[next_idx]

        # Try kicks: no kick, left, right, up, down, extend left/right
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0)]
        for kx, ky in kicks:
            new_positions = [[pivot_col + dx + kx, pivot_row + dy + ky] for dx, dy in new_offsets]
            # Validate
            if all(
                    0 <= c < grid["columns"] and 0 <= r < grid["rows"] and (c, r) not in self.inactive_pieces
                    for c, r in new_positions
            ):
                self.active_piece_grid_pos = new_positions
                self.current_rotation_index = next_idx
                # Update pivot with applied kick
                self.rotation_origin = (pivot_col + kx, pivot_row + ky)
                print("Rotated Left to:", self.active_piece_grid_pos)
                return
        # No valid rotation found; do nothing.
    def rotate_right(self):
        """
        Rotate the active piece right using `block_rotations` and a tracked pivot.
        Applies simple wall-kicks if needed.
        """
        rotations = block_rotations.get(self.current_piece_shape, [])
        if not rotations or not self.active_piece_grid_pos:
            return

        # Require a tracked index and pivot, if missing, try to initialize
        if getattr(self, "current_rotation_index", None) is None or getattr(self, "rotation_origin", None) is None:
            # Fallback: assume current is index 0 and infer pivot as the cell closest to the origin by matching (0,0)
            # Find a cell that could be the pivot by checking which cell minus offsets matches the set
            current_set = {tuple(p) for p in self.active_piece_grid_pos}
            inferred_idx = None
            inferred_pivot = None
            for idx, pattern in enumerate(rotations):
                for oc, orow in self.active_piece_grid_pos:
                    mapped = {(oc + dx, orow + dy) for dx, dy in pattern}
                    if mapped == current_set:
                        inferred_idx = idx
                        inferred_pivot = (oc, orow)
                        break
                if inferred_idx is not None:
                    break
            if inferred_idx is None:
                # As last resort, treat first cell as pivot and index 0
                inferred_idx = 0
                oc, orow = self.active_piece_grid_pos[0]
                inferred_pivot = (oc, orow)

            self.current_rotation_index = inferred_idx
            self.rotation_origin = inferred_pivot
        cur_idx = self.current_rotation_index
        pivot_col, pivot_row = self.rotation_origin
        next_idx = (cur_idx + 1) % len(rotations)
        new_offsets = rotations[next_idx]
        # Try kicks: no kick, left, right, up, down, extend left/right
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0)]
        for kx, ky in kicks:
            new_positions = [[pivot_col + dx + kx, pivot_row + dy + ky] for dx, dy in new_offsets]
            # Validate
            if all(
                    0 <= c < grid["columns"] and 0 <= r < grid["rows"] and (c, r) not in self.inactive_pieces
                    for c, r in new_positions
            ):
                self.active_piece_grid_pos = new_positions
                self.current_rotation_index = next_idx
                # Update pivot with applied kick
                self.rotation_origin = (pivot_col + kx, pivot_row + ky)
                print("Rotated Right to:", self.active_piece_grid_pos)
                return
        # No valid rotation found; do nothing.


    def _can_move(self, dcol, drow):
        """
        Check if active piece can move by (dcol, drow) without collisions or out of bounds.
        """
        if not self.active_piece_grid_pos:
            return False
        for col, row in self.active_piece_grid_pos:
            ncol = col + dcol
            nrow = row + drow
            if ncol < 0 or ncol >= grid["columns"] or nrow < 0 or nrow >= grid["rows"]:
                return False
            if (ncol, nrow) in self.inactive_pieces:
                return False
        return True

    def move_right(self):
        # Move active piece right if possible
        if not self.active_piece_grid_pos:
            return
        if self._can_move(1, 0):
            self._apply_move(1, 0)
            print("Move Right to:", self.active_piece_grid_pos)

    def move_left(self):
        # Move active piece left if possible
        if not self.active_piece_grid_pos:
            return
        if self._can_move(-1, 0):
            self._apply_move(-1, 0)
            print("Move Left to:", self.active_piece_grid_pos)

    def move_down(self):
        """
        Move active piece down; if blocked, lock into inactive and clear full rows.
        """
        if not self.active_piece_grid_pos:
            return
        if self._can_move(0, 1):
            self._apply_move(0, 1)
            print("Move Down to:", self.active_piece_grid_pos)
        else:
            # Lock piece
            for c, r in self.active_piece_grid_pos:
                self.inactive_pieces.append((c, r))
            # Clear full rows and update score
            self.inactive_pieces, lines = Logic.check_full_rows(
                self.inactive_pieces, grid["rows"], grid["columns"]
            )
            self.score += Logic.SetScore(lines)
            print("Piece Locked.")
            # Spawn next piece
            self.active_piece_grid_pos = []
            self.spawn()

    def drop(self):
        """
        Hard drop: move down until blocked, then lock.
        """
        if not self.active_piece_grid_pos:
            return
        while self._can_move(0, 1):
            self._apply_move(0, 1)
        # Lock after drop
        for c, r in self.active_piece_grid_pos:
            self.inactive_pieces.append((c, r))
        self.inactive_pieces, lines = Logic.check_full_rows(
            self.inactive_pieces, grid["rows"], grid["columns"]
        )
        self.score += Logic.SetScore(lines)
        # Spawn next piece
        self.active_piece_grid_pos = []
        self.spawn()


    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass
    def _check_game_over(self):
        if self.inactive_pieces:
            for c, r in self.inactive_pieces:
                if r == 0 or r == 1:
                    score = self.score
                    return True
        return False

class TootrisGameOver(arcade.View):
    """
    Game Over view to display when the game ends.
    """

    def __init__(self, final_score):
        super().__init__()
        self.final_score = final_score
        self.background_color = arcade.color.BLACK
        print(self.final_score)
        if self.final_score is None:
            score_text = "Final Score: 0"
        try:
            with open('score.json', 'r+') as f:
                content = f.read().strip()
                try:
                    current = int(content) if content else 0
                except ValueError:
                    current = 0
                final = int(self.final_score or 0)
                if final > current:
                    f.seek(0)
                    f.truncate()
                    f.write(str(final))
                    self.high_score = final
                else:
                    self.high_score = current
        except FileNotFoundError:
            final = int(self.final_score or 0)
            with open('score.json', 'w') as f:
                f.write(str(final))
            self.high_score = final

    def on_draw(self):
        self.clear()
        game_over_text = "Game Over"
        score_text = f"Final Score: {self.final_score}"
        arcade.draw_text(
            game_over_text,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 50,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )
        arcade.draw_text(
            score_text,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 50,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
        )
def start():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start_view = StartScreen()
    window.show_view(start_view)
    arcade.run()
def main():
    # Create the main window and start the game
    window = arcade.get_window()
    game = TootrisGame()
    window.show_view(game)
    arcade.run()
def game_over(final_score):
    window = arcade.get_window()
    game_over_view = TootrisGameOver(final_score)
    window.show_view(game_over_view)

if __name__ == "__main__":
    start()
