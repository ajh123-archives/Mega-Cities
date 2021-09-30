from PodSixNet.Channel import Channel
from time import time


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.count = 0
        self.times = []

    def Close(self):
        print(self, 'Client disconnected')

    def Network_ping(self, data):
        print(self, "ping %d round trip time was %f" % (data["count"], time() - self.times[data["count"]]))
        self.Ping()

    def Ping(self):
        print(self, "Ping:", self.count)
        self.times.append(time())
        self.Send({"action": "ping", "count": self.count})
        self.count += 1
