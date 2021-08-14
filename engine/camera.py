import pygame as pg

from .settings import *

from .converter import *


class Camera:
    """Offsets the position of the grid to create a 'camera' oriented on the player."""

    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.iso = Converter()

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.x
        y = -target.y
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(W)+1, x)  # right
        y = max(-(H)+1, y)  # bottom
        x, y = self.iso.convert_cart(x, y)
        self.camera = pg.Rect(
            x + int(WIDTH / 2), y + int(HEIGHT / 2), self.width, self.height
        )
