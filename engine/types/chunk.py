from collections import Sequence, MutableSequence
from bitstring import BitArray, Bits
import math


def get_width(length, full_width):
    """
    Returns the number of bits used by Mega Cities to represent indices into a
    list of the given length.
    """

    width = int(math.ceil(math.log(length, 2)))
    if width < 4:
        return 4
    elif width > 8:
        return full_width
    else:
        return width


class PackedArray(Sequence):
    """
    This class provides support for an array where values are tightly packed
    into a number of bits (such as 4 bits for light or 9 bits for height).
    All operations associated with fixed-size mutable sequences are supported,
    such as slicing.
    You may need to adjust the *length* and *value_width* of packed arrays from
    NBT data, where these fields are not conveyed.
    Several constructors are available for specific uses of packed arrays:
    - Light data used 4-bit values and 8-bit sectors
    - Height data uses 9-bit values and 64-bit sectors
    - tile data uses 64-bit sectors
    """

    #: The ``bitstring.BitArray`` object used for storage.
    storage = None

    #: The number of entries in the array
    length = None

    #: The width in bits of sectors. Used in (de)serialization.
    sector_width = None

    #: The width in bits of values.
    value_width = None

    def __repr__(self):
        return "<PackedArray length=%d sector_width=%d value_width=%d>" \
               % (self.length,
                  self.sector_width,
                  self.value_width)

    # Constructors ------------------------------------------------------------

    def __init__(self, storage, length, sector_width, value_width):
        self.storage = storage
        self.length = length
        self.sector_width = sector_width
        self.value_width = value_width

    @classmethod
    def empty(cls, length, sector_width, value_width):
        """
        Creates an empty array.
        """

        obj = cls(BitArray(), length, sector_width, value_width)
        obj.purge()
        return obj

    @classmethod
    def empty_light(cls):
        """
        Creates an empty array suitable for storing light data.
        """

        return cls.empty(4096, 8, 4)

    @classmethod
    def empty_tile(cls):
        """
        Creates an empty array suitable for storing tile data.
        """

        return cls.empty(4096, 64, 4)

    @classmethod
    def empty_height(cls):
        """
        Creates an empty array suitable for storing height data.
        """

        return cls.empty(256, 64, 9)

    @classmethod
    def from_bytes(cls, bytes_value, length, sector_width, value_width):
        """
        Deserialize a packed array from the given bytes.
        """

        storage = BitArray(bytes=bytes_value)
        return cls(storage, length, sector_width, value_width)

    @classmethod
    def from_light_bytes(cls, bytes_value):
        """
        Deserialize a packed array from the given light data bytes.
        """

        return cls.from_bytes(bytes_value, 4096, 8, 4)

    @classmethod
    def from_tile_bytes(cls, bytes_value, value_width):
        """
        Deserialize a packed array from the given tile data bytes.
        """

        return cls.from_bytes(bytes_value, 4096, 64, value_width)

    @classmethod
    def from_height_bytes(cls, bytes_value):
        """
        Deserialize a packed array from the given height data bytes.
        """

        return cls.from_bytes(bytes_value, 256, 64, 9)

    # Instance methods --------------------------------------------------------

    def to_bytes(self):
        """
        Serialize this packed array to bytes.
        """

        return self.storage.bytes

    def purge(self):
        """
        Initializes the storage.
        You should not need to call this method.
        """

        values_per_sector = self.sector_width // self.value_width
        sector_count = 1 + (self.length - 1) // values_per_sector
        self.storage.clear()
        self.storage.append(self.sector_width * sector_count)

    def pos(self, idx):
        """
        Returns the bit position of the value at the given index.
        You should not need to call this method.
        """

        sector, value = divmod(idx, self.sector_width // self.value_width)
        pos = (1 + sector) * self.sector_width - \
              (1 + value) * self.value_width
        return pos, pos + self.value_width

    def is_empty(self):
        """
        Returns true if this packed array is entirely zeros.
        """

        return not self.storage.any(True)

    # Sequence methods --------------------------------------------------------

    def __len__(self):
        return self.length

    def __iter__(self):
        for i in range(self.length):
            yield self.storage._slice(*self.pos(i)).uint

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [self.storage._slice(*self.pos(idx)).uint
                    for idx in range(*item.indices(len(self)))]
        else:
            if not 0 <= item < len(self):
                raise IndexError(item)
            return self.storage._slice(*self.pos(item)).uint

    def __setitem__(self, item, value):
        if isinstance(item, slice):
            for idx, value in zip(range(*item.indices(len(self))), value):
                self.storage._overwrite(
                    bs=Bits(uint=value, length=self.value_width),
                    pos=self.pos(idx)[0])
        else:
            self.storage._overwrite(
                bs=Bits(uint=value, length=self.value_width),
                pos=self.pos(item)[0])


class TileArray(Sequence):
    """
    This class provides support for tile arrays. It wraps a
    :class:`PackedArray` object and implements tile encoding/decoding,
    palettes, and counting of non-air tiles for lighting purposes. It stores
    precisely 4096 (16x16x16) values.
    All operations associated with fixed-size mutable sequences are supported,
    such as slicing.
    A palette is used when there are fewer than 256 unique values; the value
    width varies from 4 to 8 bits depending on the size of the palette, and is
    automatically adjusted upwards as necessary. Use :meth:`~tileArray.repack`
    to reclaim space by eliminating unused entries.
    When 256 or more unique values are present, the palette is unused and
    values are stored directly.
    """

    #: The :class:`PackedArray` object used for storage.
    storage = None

    #: List of encoded tile values. Empty when palette is not used.
    palette = None

    #: The `Registry` object used to encode/decode tiles
    registry = None

    #: The number of non-air tiles
    non_air = None

    def __repr__(self):
        return "<tileArray palette=%d storage=%r>" \
               % (len(self.palette), self.storage)

    # Constructors ------------------------------------------------------------

    def __init__(self, storage, palette, registry, non_air=-1):
        self.storage = storage
        self.palette = palette
        self.registry = registry
        self._non_air = non_air

    @classmethod
    def empty(cls, registry, non_air=-1):
        """
        Creates an empty tile array.
        """

        storage = PackedArray.empty(4096, 64, 4)
        palette = [0]
        return cls(storage, palette, registry, non_air)

    @classmethod
    def from_bytes(cls, bytes_value, value_width, registry, palette, non_air=-1):
        """
        Deserialize a tile array from the given bytes.
        """
        storage = PackedArray.from_tile_bytes(bytes_value, value_width)
        return cls(storage, palette, registry, non_air)

    @classmethod
    def from_nbt(cls, section, registry, non_air=-1):
        """
        Creates a tile array that uses the given NBT section tag as storage
        for tile data and the palette.
        """

        nbt_palette = section.value['Palette']
        if isinstance(nbt_palette.value, _NBTPaletteProxy):
            proxy = nbt_palette.value
        else:
            proxy = _NBTPaletteProxy(registry)
            for entry in nbt_palette.value:
                proxy.append(entry)
            nbt_palette.value = proxy

        storage = section.value["tileStates"].value
        palette = proxy.palette
        storage.length = 4096
        storage.value_width = get_width(len(proxy), registry.max_bits)
        return cls(storage, palette, registry, non_air)

    # Instance methods --------------------------------------------------------

    def to_bytes(self):
        """
        Serialize this tile array to bytes.
        """

        return self.storage.to_bytes()

    def is_empty(self):
        """
        Returns true if this tile array is entirely air.
        """

        if self.palette == [0]:
            return True
        else:
            return self.non_air == 0

    @property
    def non_air(self):
        if self._non_air == -1:
            self._non_air = [
                self.registry.is_air_tile(obj) for obj in self].count(False)
        return self._non_air

    def repack(self, reserve=None):
        """
        Re-packs internal data to use the smallest possible bits-per-tile by
        eliminating unused palette entries. This operation is slow as it walks
        all tiles to determine the new palette.
        """

        # If no reserve is given, we re-compute the palette by walking tiles
        if reserve is None:
            palette = sorted(set(self))
            palette_len = len(palette)

        # Otherwise we just ensure we have enough space to store new entries.
        elif self.palette:
            palette = self.palette[:]
            palette_len = len(palette) + reserve

        # Reserving space in an unpaletted array is a no-op.
        else:
            return

        # Compute new value width
        value_width = get_width(palette_len, self.registry.max_bits)

        # Exit if there's no change in value width needed
        if value_width == self.storage.value_width:
            return

        # Switch to unpaletted operation if necessary
        if value_width > 8:
            palette = []

        # Save contents
        values = self[:]

        # Update internals
        self.storage.value_width = value_width
        self.storage.purge()
        self.palette[:] = palette

        # Load contents
        self[:] = values

    # Sequence methods --------------------------------------------------------

    def __len__(self):
        return 4096

    def __getitem__(self, item):
        if isinstance(item, slice):
            values = []
            for value in self.storage[item.start:item.stop:item.step]:
                if self.palette:
                    value = self.palette[value]
                value = self.registry.decode_tile(value)
                values.append(value)
            return values
        else:
            value = self.storage[item]
            if self.palette:
                value = self.palette[value]
            value = self.registry.decode_tile(value)
            return value

    def __setitem__(self, item, value):
        if isinstance(item, slice):
            for idx in range(*item.indices(4096)):
                self[idx] = value[idx]
            return

        if self._non_air != -1:
            self._non_air += int(self.registry.is_air_tile(self[item])) - \
                             int(self.registry.is_air_tile(value))

        value = self.registry.encode_tile(value)

        if self.palette:
            try:
                value = self.palette.index(value)
            except ValueError:
                self.repack(reserve=1)

                if self.palette:
                    self.palette.append(value)
                    value = len(self.palette) - 1

        self.storage[item] = value

    def __iter__(self):
        for value in self.storage:
            if self.palette:
                value = self.palette[value]
            value = self.registry.decode_tile(value)
            yield value

    def __contains__(self, value):
        if self.palette:
            if self.registry.encode_tile(value) not in self.palette:
                return False
        return super(TileArray, self).__contains__(value)

    def index(self, value, start=0, stop=None):
        if self.palette:
            if self.registry.encode_tile(value) not in self.palette:
                raise ValueError
        return super(TileArray, self).index(value, start, stop)

    def count(self, value):
        if self.palette:
            if self.registry.encode_tile(value) not in self.palette:
                return 0
        return super(TileArray, self).count(value)


class _NBTPaletteProxy(MutableSequence):
    def __init__(self, registry):
        self.registry = registry
        self.palette = []

    def insert(self, idx, value):
        # FIXME: NBT chunk sections are *always* paletted, and so the format
        # diverges for palettes longer than 255 entries.
        if len(self.palette) >= 255:
            raise ValueError("Can't add more than 255 entries to NBT palette "
                             "proxy.")
        self.palette.insert(idx, None)
        self[idx] = value

    def __len__(self):
        return len(self.palette)

    def __delitem__(self, idx):
        del self.palette[idx]

    def __getitem__(self, idx):
        from ..networking.types import nbt

        tile = self.registry.decode_tile(self.palette[idx])
        entry = nbt.TagCompound({'Name': nbt.TagString(tile['name'])})
        if len(tile) > 1:
            entry.value['Properties'] = nbt.TagCompound({
                key: nbt.TagString(value)
                for key, value in tile.items()
                if key != "name"})

        return entry

    def __setitem__(self, idx, tag):
        tile = {'name': tag.value['Name'].value}
        properties = tag.value.get('Properties')
        if properties:
            tile.update(properties.to_obj())

        self.palette[idx] = self.registry.encode_tile(tile)
