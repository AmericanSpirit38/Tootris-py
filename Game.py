import random

import arcade

import Logic
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Tootris"

grid = {
    "rows": 20,
    "columns": 10,
    "cell_size": 36,
    "margin": 5,
    "top_offset": 50,
    "left_offset": 50,
}

class TootrisGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.active_piece_grid_pos = None
        self.inactive_pieces = []
        self.grid_pos = []
        self.setup_grid_pos()
        self.second_counter = 0
        self._second_acc = 0.0

    def setup_grid_pos(self):
        self.grid_pos = []
        for col in range(grid["columns"]):
            row_list = []
            for row in range(grid["rows"]):
                row_list.append((col, row))
            self.grid_pos.append(row_list)

    def get_grid_dimensions(self):
        cs = grid["cell_size"]
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]

        total_w = cols * cs + (cols - 1) * m
        total_h = rows * cs + (rows - 1) * m
        return total_w, total_h

    def get_cell_center(self, col, row):
        cs = grid["cell_size"]
        m = grid["margin"]
        left = grid["left_offset"]
        top_gap = grid["top_offset"]
        rows = grid["rows"]

        _, total_h = self.get_grid_dimensions()
        board_bottom = WINDOW_HEIGHT - top_gap - total_h

        cell_left = left + m + col * (cs + m)
        cell_bottom = board_bottom + m + (rows - 1 - row) * (cs + m)

        x = cell_left
        y = cell_bottom

        return x, y

    def draw_grid(self):
        rows = grid["rows"]
        cols = grid["columns"]
        m = grid["margin"]

        total_w, total_h = self.get_grid_dimensions()

        board_left = grid["left_offset"]
        board_top = WINDOW_HEIGHT - grid["top_offset"]
        board_bottom = board_top - total_h

        arcade.draw_lbwh_rectangle_filled(
            board_left,
            board_bottom,
            total_w,
            total_h,
            arcade.color.DARK_SLATE_GRAY,
        )
        arcade.draw_lbwh_rectangle_filled(
            board_left + m,
            board_bottom + m,
            total_w - 2 * m,
            total_h - 2 * m,
            arcade.color.GRAY,
        )

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
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
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
        pass

    def on_draw(self):
        self.clear()
        self.draw_grid()
        self.draw_square()

    def on_update(self, delta_time):
        self._second_acc += delta_time
        while self._second_acc >= 1.0:
            self._second_acc -= 1.0
            self.second_counter += 1
            self.move_down()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.move_left()
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.move_right()
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.move_down()
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
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            if row < grid["rows"] - 1:
                if (col, row + 1) in self.inactive_pieces:
                    self.inactive_pieces.append((col, row))
                    self.active_piece_grid_pos = None
                    return
                self.active_piece_grid_pos = (col, row + 1)
                print("Move Down to:", self.active_piece_grid_pos)
            else:
                self.inactive_pieces.append((col, row))
                self.inactive_pieces = Logic.check_full_rows(self.inactive_pieces, grid["rows"], grid["columns"])
                self.active_piece_grid_pos = None
                print("Piece Locked at:", (col, row))
    def move_right(self):
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            if col < grid["columns"] - 1:
                self.active_piece_grid_pos = (col + 1, row)
                print("Move Right to:", self.active_piece_grid_pos)
    def move_left(self):
        if self.active_piece_grid_pos:
            col, row = self.active_piece_grid_pos
            if col > 0:
                self.active_piece_grid_pos = (col - 1, row)
                print("Move Left to:", self.active_piece_grid_pos)
    def drop(self):
        while self.active_piece_grid_pos:
            self.move_down()
    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = TootrisGame()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
