from PodSixNet.Server import Server
from .ClientChannel import ClientChannel


class ServerMain(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        super().__init__(localaddr=("0.0.0.0", 35565), *args, **kwargs)
        print("Server setup")

    def Connected(self, channel, addr):
        print('new connection:', addr)
        channel.Ping()
