import arcade

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

        inner_left = left + m
        inner_top = WINDOW_HEIGHT - top_gap - m

        x = inner_left + col * (cs + m) + cs / 2
        y = inner_top - row * (cs + m) - cs / 2

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

        for row in range(rows):
            for col in range(cols):
                left = board_left + m + col * (cell_width + m)
                bottom = board_bottom + m + (rows - 1 - row) * (cell_height + m)

                arcade.draw_lbwh_rectangle_filled(
                    left,
                    bottom,
                    cell_width,
                    cell_height,
                    arcade.color.LIGHT_GRAY
                )

    def reset(self):
        pass

    def on_draw(self):
        self.clear()
        self.draw_grid()

    def on_update(self, delta_time):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.LEFT:
            print("Left")
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            print("Right")
        elif key == arcade.key.S or key == arcade.key.DOWN:
            print("Down")
        elif key == arcade.key.W or key == arcade.key.UP:
            print("Rotate")

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
