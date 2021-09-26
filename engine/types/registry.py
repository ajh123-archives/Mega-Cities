class Registry(object):
    """
    Base type for registries.
    """

    #: Number of bits needed to represent the greatest tile ID.
    max_bits = None

    def encode(self, kind, obj):
        """
        Encodes a thing to an integer ID.
        """

        raise NotImplementedError

    def decode(self, kind, val):
        """
        Decodes a thing from an integer ID.
        """

        raise NotImplementedError

    def encode_tile(self, obj):
        """
        Encodes a tile to an integer ID.
        """

        raise NotImplementedError

    def decode_tile(self, val):
        """
        Decodes a tile from an integer ID.
        """

        raise NotImplementedError

    def is_air_tile(self, obj):
        """
        Returns true if the given object is considered air for lighting
        purposes.
        """

        raise NotImplementedError


class OpaqueRegistry(Registry):
    """
    Registry that passes IDs through unchanged. This is the default.
    """

    def __init__(self, max_bits):
        self.max_bits = max_bits

    def encode(self, kind, obj): return obj
    def decode(self, kind, val): return val

    def encode_tile(self, obj): return obj
    def decode_tile(self, val): return val
    def is_air_tile(self, obj): return obj == 0
