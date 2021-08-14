import pygame as pg

from .settings import *
from .converter import *


class Player(pg.sprite.Sprite):
    """Class that holds everything for the Player Character."""

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load(
            "images/player_tile.png"
        ).convert_alpha()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.iso = Converter()

    def move(self, dx=0, dy=0):
        """Moves the position of the player in cartesian coordinates."""
        self.x += dx
        self.y += dy

    def update(self):
        """Updates the isometric position of the player."""
        self.rect.x, self.rect.y = self.iso.convert_cart(self.x, self.y)

    def current_position(self):
        """Current position of the player in isometric coordinates."""
        return self.x, self.y


class Tile(pg.sprite.Sprite):
    """All entities that make up the grid background
    is currently handled in this class."""

    def __init__(self, grid, game, data, x, y):
        super(Tile, self).__init__()
        self.data = data
        self.game = game
        self.grid = grid

        # Flags to check if other processes are needed.
        self.flag = False
        self.sprite_init = True
        self.multi_states = False
        self.x, self.y = x, y

        self.tile_data = None
        self.tile_string = None

        if self.data is not None and self.data != 0:
            self.check_data()
            self.init_sprite()
            self.load_sprite()

    def init_sprite(self):
        """Creates a sprite."""
        groups = self.game.tiles
        pg.sprite.Sprite.__init__(self, groups)
        self.sprite_init = False

    def load_sprite(self):
        """Gives the sprite an image to show."""
        self.check_data()
        self.image = pg.image.load(f"""images/{self.tile_data}.png""").convert_alpha()
        self.rect = self.image.get_rect()
        iso = Converter()
        # Convert cartesian to isometric coordinates
        self.rect.x, self.rect.y = iso.convert_cart(self.x, self.y)

    def check_data(self):
        """Checks the data in the Tile object
        and selects the image to display."""
        self.tile_data = self.game.TileFile.images[self.data]
        self.tile_string = self.game.TileFile.titles[self.data]

    def update_tile_image(self):
        """Updates the tile with a new image and
        checks to see if the tile needs a sprite now."""
        if self.sprite_init:
            self.init_sprite()
            self.load_sprite()
            self.flag = False
        else:
            self.check_data()
            self.image = pg.image.load(
                f"""images/{self.tile_data}.png"""
            ).convert_alpha()
            self.flag = False


class Grid:
    def __init__(self, game, width, height):
        """Initialize a grid object with dimensions width x height that contains
        Tile objects with specified data. All the tile objects are held in a list
        array."""
        self.game = game
        self.w = width
        self.h = height
        self.width = width * TILEWIDTH
        self.height = height * TILEHEIGHT
        self.grid_data = [[Tile(None, game, None, None, None) for _ in range(self.w)] for _ in range(self.h)]

    def create_grid(self, data):
        """Creates a grid with specified data population."""
        self.grid_data = [[data for _ in range(self.w)] for _ in range(self.h)]
        for row_nb, row in enumerate(self.grid_data):
            for col_nb, tile in enumerate(row):
                self.grid_data[row_nb][col_nb] = Tile(
                    self, self.game, data, row_nb, col_nb
                )

    def load_grid(self, grid_list):
        self.grid_data = [
            [0 for _ in range(self.w)] for _ in range(self.h)
        ]
        """Saves games states by saving tile_data in a list array."""
        for row_nb, row in enumerate(grid_list):
            for col_nb, tile in enumerate(row):
                if isinstance(col_nb, int) and isinstance(row_nb, int):
                    self.grid_data[row_nb][col_nb] = Tile(
                        self, self.game, grid_list[row_nb][col_nb], row_nb, col_nb
                    )
                    continue

                raise TypeError(f"row_nb: {row_nb} & col_nb:{col_nb} must be type of int")

    def update_tile(self, data, x, y):
        """Updates a tile at the specified coordinates."""
        tile = self.grid_data[x][y]
        if isinstance(tile, Tile):
            tile.flag = True
            tile.data = data
            return

        raise TypeError("tile must be type of Tile")

    def check_update_grid(self):
        """Check if the grid needs to be updated."""
        for row_nb, row in enumerate(self.grid_data):
            for col_nb, tile in enumerate(row):
                if isinstance(tile, Tile):
                    if tile.flag:
                        tile.update_tile_image()
                    continue

                raise TypeError(f"tile {row_nb}:{col_nb} must be type of Tile")

    def grid_list(self):
        grid_list = [
            [0 for _ in range(len(self.grid_data[1]))]
            for _ in range(len(self.grid_data))
        ]
        """Saves games states by saving tile_data in a list array."""
        for row_nb, row in enumerate(self.grid_data):
            for col_nb, tile in enumerate(row):
                tile = self.grid_data[row_nb][col_nb]
                if isinstance(tile, Tile):
                    grid_list[row_nb][col_nb] = tile.data
                    continue

                raise TypeError(f"tile {row_nb}:{col_nb} must be type of Tile")
        return grid_list
