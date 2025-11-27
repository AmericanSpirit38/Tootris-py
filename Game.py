import random

import arcade

import Logic

# Window configuration
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Tootris"

# Grid configuration for the game board
# - rows/columns: logical size of the board
# - cell_size: visual size of each cell in pixels (approx; inner cells are computed)
# - margin: spacing between cells and inner border
# - top_offset/left_offset: padding from window edges to board
grid = {
    "rows": 20,
    "columns": 10,
    "cell_size": 36,
    "margin": 5,
    "top_offset": 50,
    "left_offset": 50,
}


class TootrisGame(arcade.View):
    """
    Main game view for a simplified Tetris-like game.

    Tracks an active falling block (single cell) and a list of inactive pieces
    (locked cells). Handles drawing the grid and cells, input for moving the
    active block, and an automatic gravity tick once per second.
    """

    def __init__(self):
        super().__init__()
        # Background color of the entire view
        self.background_color = arcade.color.BLACK

        # Current active piece position as (col, row). None if no active piece.
        self.active_piece_grid_pos = None

        # Positions of all locked (inactive) pieces as (col, row)
        self.inactive_pieces = []

        # Precomputed grid positions as a 2D list [col][row] => (col, row)
        self.grid_pos = []
        self.setup_grid_pos()

        # A simple second counter and accumulator to trigger gravity once per second
        self.second_counter = 0
        self._second_acc = 0.0

    def setup_grid_pos(self):
        """
        Populate the grid_pos with tuples of (col, row) for quick iteration/access.
        """
        self.grid_pos = []
        for col in range(grid["columns"]):
            row_list = []
            for row in range(grid["rows"]):
                row_list.append((col, row))
            self.grid_pos.append(row_list)

    def get_grid_dimensions(self):
        """
        Compute total pixel width/height of the board including margins between cells.
        Returns: (total_w, total_h)
        """
        cs = grid["cell_size"]
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]

        # Each cell contributes cs; each gap between cells contributes m.
        total_w = cols * cs + (cols - 1) * m
        total_h = rows * cs + (rows - 1) * m
        return total_w, total_h

    def get_cell_center(self, col, row):
        """
        Convert a grid (col, row) to the bottom-left pixel coordinate of the cell
        (named center_x/center_y historically; we actually use bottom-left here).
        """
        cs = grid["cell_size"]
        m = grid["margin"]
        left = grid["left_offset"]
        top_gap = grid["top_offset"]
        rows = grid["rows"]

        _, total_h = self.get_grid_dimensions()
        # Board is placed with a top offset; compute bottom coordinate accordingly
        board_bottom = WINDOW_HEIGHT - top_gap - total_h

        # Position inside inner board: start at left+margin and add col*(cell+gap)
        cell_left = left + m + col * (cs + m)
        # Rows are drawn from top to bottom visually; grid row 0 is the top.
        cell_bottom = board_bottom + m + (rows - 1 - row) * (cs + m)

        x = cell_left
        y = cell_bottom

        return x, y

    def draw_grid(self):
        """
        Draw the board background and the grid of cells.
        The inner cell size is computed so the grid fits perfectly in the board.
        """
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]

        total_w, total_h = self.get_grid_dimensions()

        board_left = grid["left_offset"]
        board_top = WINDOW_HEIGHT - grid["top_offset"]
        board_bottom = board_top - total_h

        # Outer board area
        arcade.draw_lbwh_rectangle_filled(
            board_left,
            board_bottom,
            total_w,
            total_h,
            arcade.color.DARK_SLATE_GRAY,
        )
        # Inner area (slightly inset to create a border)
        arcade.draw_lbwh_rectangle_filled(
            board_left + m,
            board_bottom + m,
            total_w - 2 * m,
            total_h - 2 * m,
            arcade.color.GRAY,
        )

        # Compute exact cell sizes to fill inner area neatly
        inner_width = total_w - 2 * m
        inner_height = total_h - 2 * m
        cell_width = (inner_width - (cols - 1) * m) / cols
        cell_height = (inner_height - (rows - 1) * m) / rows
        for col in range(cols):
            for row in range(rows):
                left = board_left + m + col * (cell_width + m)
                bottom = board_bottom + m + (rows - 1 - row) * (cell_height + m)

                # Base cell color for empty grid cells
                arcade.draw_lbwh_rectangle_filled(
                    left,
                    bottom,
                    cell_width,
                    cell_height,
                    arcade.color.LIGHT_GRAY
                )

    def draw_square(self):
        """
        Draw the active falling cell (red) and all inactive locked cells (blue).
        """
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            # Compute draw positions based on the same math used in draw_grid
            center_x, center_y = self.get_cell_center(col, row)
            total_w, total_h = self.get_grid_dimensions()
            board_left = grid["left_offset"]
            board_top = WINDOW_HEIGHT - grid["top_offset"]
            board_bottom = board_top - total_h
            m = grid["margin"]
            rows = grid["rows"]
            cols = grid["columns"]
            inner_width = total_w - 2 * m
            inner_height = total_h - 2 * m
            cell_width = (inner_width - (cols - 1) * m) / cols
            cell_height = (inner_height - (rows - 1) * m) / rows
            left = board_left + m + col * (cell_width + m)
            bottom = board_bottom + m + (rows - 1 - row) * (cell_height + m)
            arcade.draw_lbwh_rectangle_filled(
                left,
                bottom,
                cell_width,
                cell_height,
                arcade.color.RED
            )
        if self.inactive_pieces:
            for (col, row) in self.inactive_pieces:
                center_x, center_y = self.get_cell_center(col, row)
                total_w, total_h = self.get_grid_dimensions()
                board_left = grid["left_offset"]
                board_top = WINDOW_HEIGHT - grid["top_offset"]
                board_bottom = board_top - total_h
                m = grid["margin"]
                rows = grid["rows"]
                cols = grid["columns"]
                inner_width = total_w - 2 * m
                inner_height = total_h - 2 * m
                cell_width = (inner_width - (cols - 1) * m) / cols
                cell_height = (inner_height - (rows - 1) * m) / rows
                left = board_left + m + col * (cell_width + m)
                bottom = board_bottom + m + (rows - 1 - row) * (cell_height + m)
                arcade.draw_lbwh_rectangle_filled(
                    left,
                    bottom,
                    cell_width,
                    cell_height,
                    arcade.color.BLUE
                )

    def reset(self):
        """
        Reset game state if needed. Currently a placeholder.
        """
        pass

    def on_draw(self):
        """
        Arcade draw callback. Clears the screen and renders the board and pieces.
        """
        self.clear()
        self.draw_grid()
        self.draw_square()

    def on_update(self, delta_time):
        """
        Arcade update callback. Accumulates time to trigger a once-per-second
        gravity tick that moves the active piece down.
        """
        self._second_acc += delta_time
        while self._second_acc >= 1.0:
            self._second_acc -= 1.0
            self.second_counter += 1
            self.move_down()

    def on_key_press(self, key, modifiers):
        """
        Handle keyboard input for movement and spawning:
        - A/Left: move left
        - D/Right: move right
        - S/Down: soft drop (also resets the gravity accumulator)
        - W/Up: rotate (placeholder)
        - P: spawn a new active piece at a random column, row 0
        - Space: hard drop (move down until lock)
        """
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.move_left()
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.move_right()
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.move_down()
            # Reset the second accumulator to avoid an immediate extra tick
            self._second_acc = 0
        elif key == arcade.key.W or key == arcade.key.UP:
            print("Rotate")
        elif key == arcade.key.P:
            col = random.randrange(grid["columns"])
            self.active_piece_grid_pos = (col, 0)
            print("Spawn Piece at:", self.active_piece_grid_pos)
        elif key == arcade.key.SPACE:
            self.drop()

    def move_down(self):
        """
        Move the active piece down by one row if possible. If blocked by bottom
        or another piece, lock it and clear any full rows using Logic.check_full_rows.
        """
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            if row < grid["rows"] - 1:
                # If the next cell below is occupied, lock the current one
                if (col, row + 1) in self.inactive_pieces:
                    self.inactive_pieces.append((col, row))
                    self.active_piece_grid_pos = None
                    return
                self.active_piece_grid_pos = (col, row + 1)
                print("Move Down to:", self.active_piece_grid_pos)
            else:
                # Reached bottom: lock the piece and process line clears
                self.inactive_pieces.append((col, row))
                self.inactive_pieces = Logic.check_full_rows(self.inactive_pieces, grid["rows"], grid["columns"])
                self.active_piece_grid_pos = None
                print("Piece Locked at:", (col, row))

    def move_right(self):
        """
        Move the active piece one column to the right if within bounds.
        """
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            if col < grid["columns"] - 1:
                self.active_piece_grid_pos = (col + 1, row)
                print("Move Right to:", self.active_piece_grid_pos)

    def move_left(self):
        """
        Move the active piece one column to the left if within bounds.
        """
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            if col > 0:
                self.active_piece_grid_pos = (col - 1, row)
                print("Move Left to:", self.active_piece_grid_pos)

    def drop(self):
        """
        Hard drop: repeatedly move down until the active piece locks.
        """
        while self.active_piece_grid_pos:
            self.move_down()

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Mouse move callback. Currently unused.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Mouse press callback. Currently unused.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Mouse release callback. Currently unused.
        """
        pass


def main():
    """
    Create the window, show the game view, and start the Arcade event loop.
    """
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = TootrisGame()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
