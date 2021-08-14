from .save_data_handler import Data


class TileFile(Data):
    def __init__(self):
        super(TileFile, self).__init__("images/tiles.json")
        self.images = {}
        self.titles = {}

        for tile_name, tile in self.data["tiles"].items():
            is_multi_state = tile.get("multiState", False)
            if not is_multi_state:
                try:
                    self.images[tile["netId"]] = tile["image"]
                    self.titles[tile["netId"]] = tile_name
                except KeyError:
                    pass
            else:
                try:
                    states = tile["states"]
                    for key, value in states.items():
                        if type(value) is dict:
                            self.images[value["netId"]] = value["image"]
                            self.titles[value["netId"]] = tile_name+":"+key
                except KeyError:
                    pass
