from .save_data_handler import Data


class TileFile(Data):
    def __init__(self):
        super(TileFile, self).__init__("images/tiles.json")
        self.images = {}
        self.titles = {}
        self.multi_states = {}
        self.tick_multiplier = {}
        self.loop = {}

        for tile_name, tile in self.data["tiles"].items():
            is_multi_state = tile.get("multiState", False)
            root_inherit = tile.get("inherit", False)
            if not is_multi_state:
                if root_inherit is False:
                    try:
                        self.images[tile["netId"]] = tile["image"]
                        self.titles[tile["netId"]] = tile_name
                        self.multi_states[tile["netId"]] = False
                        self.tick_multiplier[tile["netId"]] = 0
                        self.loop[tile["netId"]] = False
                    except KeyError:
                        pass
                else:
                    if type(root_inherit) is int:
                        try:
                            self.images[tile["netId"]] = self.images[root_inherit]
                            self.titles[tile["netId"]] = tile_name
                            self.multi_states[tile["netId"]] = False
                            self.tick_multiplier[tile["netId"]] = 0
                            self.loop[tile["netId"]] = False
                        except IndexError:
                            raise IndexError(f"JSON tile -> {tile_name}.inherit ({root_inherit})." +
                                             f"Tile {root_inherit} does not exist, Have you defined it before?")
                    else:
                        raise TypeError(f"JSON tile -> {tile_name}.inherit must be type of int or str")
            else:
                try:
                    states = tile["states"]
                    for key, value in states.items():
                        if type(value) is dict:
                            state_inherit = value.get("inherit", False)
                            if state_inherit is False:
                                self.images[value["netId"]] = value["image"]
                                self.titles[value["netId"]] = tile_name + ":" + key
                                self.multi_states[value["netId"]] = True
                                self.tick_multiplier[value["netId"]] = states["tickMultiplier"]
                                self.loop[value["netId"]] = states["loop"]
                            else:
                                if type(state_inherit) is int:
                                    self.images[value["netId"]] = self.images[state_inherit]
                                    self.titles[value["netId"]] = tile_name + ":" + key
                                    self.multi_states[value["netId"]] = True
                                    self.tick_multiplier[value["netId"]] = states["tickMultiplier"]
                                    self.loop[value["netId"]] = states["loop"]
                                else:
                                    raise TypeError(f"JSON tile -> {tile_name}.states.{key}.inherit must be type of "
                                                    f"int or str")
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
