import importlib
import importlib.util
import os


class PluginLoader:
    # We are going to receive a list of plugins as parameter
    def __init__(self, game, plugins=None):
        # Checking if plugin were sent
        self._plugins = []
        if plugins:
            print("Loading plugins")
            # create a list of plugins
            for plugin_path in plugins:
                mod = importlib.import_module(plugin_path, "plugins")
                self._plugins.append(mod)
                mod.Plugin(game)

    def run(self):
        # We is were magic happens, and all the plugins are going to be printed
        for plugin in self._plugins:
            pass
