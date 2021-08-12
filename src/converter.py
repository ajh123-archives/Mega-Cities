from .settings import *

class Converter:
    """Can convert cartesian to isometric coordinates."""
    def __init__(self):
        self.tile_width_half = TILEWIDTH_HALF
        self.tile_height_half = TILEHEIGHT_HALF

    def convert_cart(self, x, y):
        cart_x = x * self.tile_width_half
        cart_y = y * self.tile_height_half
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        return iso_x, iso_y

    def convert_rect(self, rect_x, rect_y):
        cart_x = rect_x * self.tile_width_half
        cart_y = rect_y * self.tile_height_half
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        return iso_x, iso_y
