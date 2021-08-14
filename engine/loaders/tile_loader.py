from .save_data_handler import Data


class TileFile(Data):
    def __init__(self):
        super(TileFile, self).__init__("images/tiles.json")
        self.images = {}
        self.titles = {}

        for tile_name, tile in self.data["tiles"].items():
            try:
                # print(tile_name, tile["netId"], tile["image"])
                self.images[tile["netId"]] = tile["image"]
                self.titles[tile["netId"]] = tile_name
            except KeyError:
                pass

        print(self.images, self.titles)
