import arcade

square_positions = []

def draw_square(position, color=arcade.color.RED, size=20):
    x, y = position
    arcade.draw_rectangle_filled(
        x + size / 2,
        y + size / 2,
        size,
        size,
        color
    )