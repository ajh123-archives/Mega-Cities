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
                            self.titles[value["netId"]] = tile_name + ":" + key
                except KeyError:
                    pass


class TileLookup:
    def __init__(self, tileFile):
        self.tileFile = None
        if isinstance(tileFile, TileFile):
            self.tileFile = tileFile
            return

        raise TypeError("tileFile must be type of TileFile")

    def lookup_from_int(self, netId) -> str:
        """The fastest mode of lookup since the names are stored in a netId indexed array

        :param netId :(int) The associated network id of the tile
        """
        return self.tileFile.titles[netId]

    def lookup_from_title(self, title) -> int:
        """The slowest mode of lookup since the we have to loop the tiles array and compare

        :param title :(str) The associated title of the tile
        :return has_failed_or_id :If the lookup has failed -1 will be returned else the id will be
        """
        for tile in self.tileFile.titles:
            if self.tileFile.titles[tile] == title:
                return tile
        return -1
