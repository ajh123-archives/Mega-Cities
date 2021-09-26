import uuid


class UUID(uuid.UUID):
    @classmethod
    def from_hex(cls, hex_value):
        return cls(hex=hex_value)

    @classmethod
    def from_bytes(cls, bytes_value):
        return cls(bytes=bytes_value)

    @classmethod
    def from_offline_player(cls, display_name):
        class FakeNamespace(object):
            bytes = b'OfflinePlayer:'
        base_uuid = uuid.uuid3(FakeNamespace(), display_name)
        return cls(bytes=base_uuid.bytes)

    @classmethod
    def random(cls):
        return cls(bytes=uuid.uuid4().bytes)

    def to_hex(self, with_dashes=True):
        if with_dashes:
            return "%s" % self
        else:
            return self.hex

    def to_bytes(self):
        return self.bytes
