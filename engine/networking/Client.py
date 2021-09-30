from PodSixNet.Connection import connection, ConnectionListener


class Client(ConnectionListener):
    """ This example client connects to a LagTimeServer which then sends pings back.
    This client responds to 10 pings, and the server measures the round-trip time of each ping and outputs it."""

    running = False
    net_error = []

    def __init__(self, host, port):
        self.Connect((host, port))
        print("LagTimeClient started")

    def Network_ping(self, data):
        print("got:", data)
        connection.Send(data)

    # built in stuff

    def Network_connected(self, data):
        print("Connected to the server")
        self.running = True

    def Network_error(self, data):
        print('error:', data['error'][1])
        self.net_error = data['error'][1]
        connection.Close()
        self.running = False

    def Network_disconnected(self, data):
        print('Server disconnected')
        self.running = False
