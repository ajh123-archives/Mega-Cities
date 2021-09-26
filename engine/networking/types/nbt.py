import collections

import functools
import gzip

from ...types.chunk import PackedArray

from ...networking.buffer import Buffer

_kinds = {}
_ids = {}


# Base types ------------------------------------------------------------------

@functools.total_ordering
class _Tag(object):
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

    @classmethod
    def from_bytes(cls, bytes_value):
        return cls.from_buff(Buffer(bytes_value))

    @classmethod
    def from_buff(cls, buff):
        raise NotImplementedError

    def to_bytes(self):
        raise NotImplementedError

    def to_obj(self):
        return self.value

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.value)

    def __eq__(self, other):
        return self.to_obj() == other.to_obj()

    def __lt__(self, other):
        return self.to_obj() < other.to_obj()


class _DataTag(_Tag):
    __slots__ = ()
    fmt = None

    @classmethod
    def from_buff(cls, buff):
        return cls(buff.unpack(cls.fmt))

    def to_bytes(self):
        return Buffer.pack(self.fmt, self.value)


class _ArrayTag(_Tag):
    __slots__ = ()
    width = None

    @classmethod
    def from_buff(cls, buff):
        length = buff.unpack('i')
        data = buff.read(length * (cls.width // 8))
        return cls(PackedArray.from_bytes(data, length, cls.width, cls.width))

    def to_bytes(self):
        data = self.value.to_bytes()
        data = Buffer.pack('i', len(data) // (self.width // 8)) + data
        return data

    def to_obj(self):
        return list(self.value)


# NBT tags --------------------------------------------------------------------

class TagByte(_DataTag):
    __slots__ = ()
    fmt = 'b'


class TagShort(_DataTag):
    __slots__ = ()
    fmt = 'h'


class TagInt(_DataTag):
    __slots__ = ()
    fmt = 'i'


class TagLong(_DataTag):
    __slots__ = ()
    fmt = 'q'


class TagFloat(_DataTag):
    __slots__ = ()
    fmt = 'f'


class TagDouble(_DataTag):
    __slots__ = ()
    fmt = 'd'


class TagString(_Tag):
    __slots__ = ()

    @classmethod
    def from_buff(cls, buff):
        string_length = buff.unpack('H')
        return cls(buff.read(string_length).decode('utf8'))

    def to_bytes(self):
        data = self.value.encode('utf8')
        return Buffer.pack('H', len(data)) + data


class TagByteArray(_ArrayTag):
    __slots__ = ()
    width = 8


class TagIntArray(_ArrayTag):
    __slots__ = ()
    width = 32


class TagLongArray(_ArrayTag):
    __slots__ = ()
    width = 64


class TagList(_Tag):
    __slots__ = ()

    @classmethod
    def from_buff(cls, buff):
        inner_kind_id, array_length = buff.unpack('bi')
        inner_kind = _kinds[inner_kind_id]
        return cls([inner_kind.from_buff(buff) for _ in range(array_length)])

    def to_bytes(self):
        if len(self.value) > 0:
            head = self.value[0]
        else:
            head = TagByte(0)

        return Buffer.pack('bi', _ids[type(head)], len(self.value)) + b"".join(tag.to_bytes() for tag in self.value)

    def to_obj(self):
        return [tag.to_obj() for tag in self.value]


class TagCompound(_Tag):
    __slots__ = ()

    root = False
    preserve_order = False

    @classmethod
    def from_buff(cls, buff):
        if cls.preserve_order:
            value = collections.OrderedDict()
        else:
            value = {}

        while True:
            kind_id = buff.unpack('b')
            if kind_id == 0:
                return cls(value)
            kind = _kinds[kind_id]
            name = TagString.from_buff(buff).value
            tag = kind.from_buff(buff)
            value[name] = tag
            if cls.root:
                return cls(value)

    def to_bytes(self):
        string = b""
        for name, tag in self.value.items():
            string += Buffer.pack('b', _ids[type(tag)])
            string += TagString(name).to_bytes()
            string += tag.to_bytes()

        if len(self.value) == 0 or not self.root:
            string += Buffer.pack('b', 0)

        return string

    def to_obj(self):
        return dict((name, tag.to_obj()) for name, tag in self.value.items())

    def update(self, other_tag):
        for name, new_tag in other_tag.value.items():
            old_tag = self.value.get(name)

            if old_tag and not new_tag:
                del self.value[name]
            elif isinstance(old_tag, TagCompound) \
                    and isinstance(new_tag, TagCompound):
                self.value[name].update(new_tag)
            else:
                self.value[name] = new_tag


class TagRoot(TagCompound):
    __slots__ = ()
    root = True

    @classmethod
    def from_body(cls, body):
        return cls({u"": body})

    @property
    def body(self):
        return self.value[u""]


# Register tags ---------------------------------------------------------------

_kinds[0] = type(None)
_kinds[1] = TagByte
_kinds[2] = TagShort
_kinds[3] = TagInt
_kinds[4] = TagLong
_kinds[5] = TagFloat
_kinds[6] = TagDouble
_kinds[7] = TagByteArray
_kinds[8] = TagString
_kinds[9] = TagList
_kinds[10] = TagCompound
_kinds[11] = TagIntArray
_kinds[12] = TagLongArray
_ids.update({v: k for k, v in _kinds.items()})


# Files -----------------------------------------------------------------------

class NBTFile(object):
    root_tag = None

    def __init__(self, root_tag):
        self.root_tag = root_tag

    @classmethod
    def load(cls, path):
        with gzip.open(path, 'rb') as fd:
            return cls(TagRoot.from_bytes(fd.read()))

    def save(self, path):
        with gzip.open(path, 'wb') as fd:
            fd.write(self.root_tag.to_bytes())


# Debug -----------------------------------------------------------------------

def alt_repr(tag, level=0):
    """
    Returns a human-readable representation of a tag using the same format as
    used the NBT specification.
    """
    name = lambda kind: type(kind).__name__.replace("Tag", "TAG_")

    if isinstance(tag, _ArrayTag):
        return "%s%s: %d entries" % (
            "  " * level,
            name(tag),
            len(tag.value))

    elif isinstance(tag, TagList):
        return "%s%s: %d entries\n%s{\n%s\n%s}" % (
            "  " * level,
            name(tag),
            len(tag.value),
            "  " * level,
            u"\n".join(alt_repr(tag, level + 1) for tag in tag.value),
            "  " * level)

    elif isinstance(tag, TagRoot):
        return u"\n".join(
            alt_repr(tag, level).replace(': ', '("%s"): ' % name, 1)
            for name, tag in tag.value.items())

    elif isinstance(tag, TagCompound):
        return "%s%s: %d entries\n%s{\n%s\n%s}" % (
            "  " * level,
            name(tag),
            len(tag.value),
            "  " * level,
            u"\n".join(
                alt_repr(tag, level + 1).replace(': ', '("%s"): ' % name, 1)
                for name, tag in tag.value.items()),
            "  " * level)

    elif isinstance(tag, TagString):
        return '%s%s: "%s"' % (
            "  " * level,
            name(tag),
            tag.value)

    else:
        return "%s%s: %r" % (
            "  " * level,
            name(tag),
            tag.value)
