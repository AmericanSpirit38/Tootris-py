import random
# Import the arcade library for game development
import arcade
# Import a script that handles game logic
import Logic

# Window configuration
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Tootris"

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
    "I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
}


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

        self.score = 0

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
        arcade.draw_text(
            score_text,
            10,
            WINDOW_HEIGHT - 30,
            arcade.color.WHITE,
            16
        )
    def reset(self):
        pass

    def on_draw(self):
        # Render the screen.
        self.clear()
        self.draw_grid()
        self.draw_square()
        self.draw_score()

    def on_update(self, delta_time):
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
            print("Rotate Left")
        # Handle input to rotate piece Right (not implemented)
        elif key == arcade.key.E:
            print("Rotate Right")
        # Handle input to spawn a random piece (testing only) to be implemented automatically
        elif key == arcade.key.P:
            # Randomly spawn a preset piece
            kind = random.choice(list(block_presets.keys()))
            self.spawn(kind)
            print("Spawn Piece:", kind, "at", self.active_piece_grid_pos)
        # Handle input to hard drop piece
        elif key == arcade.key.SPACE:
            self.drop()

    def spawn(self, kind=None):
        """
        Spawn a multi-cell piece from block_presets at the top, centered horizontally.
        """
        if kind is None:
            kind = random.choice(list(block_presets.keys()))
        offsets = block_presets.get(kind, [])
        if not offsets:
            self.active_piece_grid_pos = []
            return

        # Compute horizontal span to center piece
        min_dx = min(dx for dx, dy in offsets)
        max_dx = max(dx for dx, dy in offsets)
        span = max_dx - min_dx + 1
        start_col = (grid["columns"] - span) // 2 - min_dx
        start_row = 0  # top row

        # Translate offsets to absolute grid positions
        cells = [[start_col + dx, start_row + dy] for dx, dy in offsets]

        # If any cell is occupied at spawn, do not spawn (game over condition placeholder)
        if any((c, r) in self.inactive_pieces or c < 0 or c >= grid["columns"] or r < 0 or r >= grid["rows"] for c, r in cells):
            self.active_piece_grid_pos = []
            return

        self.active_piece_grid_pos = cells

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

    def _apply_move(self, dcol, drow):
        """
        Apply movement vector to all active cells.
        """
        self.active_piece_grid_pos = [[c + dcol, r + drow] for c, r in self.active_piece_grid_pos]

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
            # Clear full rows
            self.inactive_pieces = Logic.check_full_rows(self.inactive_pieces, grid["rows"], grid["columns"])
            self.active_piece_grid_pos = []
            print("Piece Locked.")

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
        self.inactive_pieces = Logic.check_full_rows(self.inactive_pieces, grid["rows"], grid["columns"])
        self.active_piece_grid_pos = []

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass


def main():
    # Create the main window and start the game
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = TootrisGame()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    # run the main function to start the game
    main()
