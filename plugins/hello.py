class Plugin:
    def __init__(self, game, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.game = game
        print("Hello World plugin initialized")

    def execute(self, *args, **kwargs):
        #print(self.args, self.kwargs, args, kwargs)
        pass


def hi() -> int:
    return 0
