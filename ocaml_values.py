
Closure_tag = 247
Object_tag = 248
Infix_tag = 249
String_tag = 252

class Root(object):
    @staticmethod
    def check(x):
        assert isinstance(x, Root), x

class Int64(Root):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'Int64(%s)' % self.i

    def hash(self):
        return self.i

class Int32(Root):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'Int32(%s)' % self.i

    def hash(self):
        return self.i

class Block(Root):
    def __init__(self, tag, size):
        assert isinstance(tag, int)
        self._tag = tag
        self._fields = [None]*size
        self._envoffsettop = Val_unit
        self._envoffsetdelta = -1

    def field(self, i):
        assert i >= 0
        return self._fields[i]

    def set_field(self, i, v):
        Root.check(v)
        assert i >= 0
        self._fields[i] = v

    def __repr__(self):
        return 'Block(%d, %s)' % (self._tag, self._fields)

    def __str__(self):
        return 'Block(%d, %s)' % (self._tag, self._fields)

    def hash(self):
        i = 0
        i += self._tag
        i &= 0xFFFFFFFF
        i *= 31
        i &= 0xFFFFFFFF
        for f in self._fields:
            i+= f.hash()
            i &= 0xFFFFFFFF
            i *= 31
            i &= 0xFFFFFFFF
        return i

def is_block(x):
    return isinstance(x, Block)

def make_block(size, tag):
    b = Block(tag, size)
    return b

def block_tag(block):
    return block._tag

def is_true(a):
    if isinstance(a, Int):
        return to_int(a) != 0
    return True

def to_int(a):
    assert isinstance(a, Int), a
    return a.i

def to_uint(a):
    assert isinstance(a, Int), a
    return a.i # TODO

def make_int(a):
    assert isinstance(a, int) or isinstance(a, long), a
    return Int(a)

def make_bool(a):
    return Int(1 if a else 0)

class Float(Root):
    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return 'Float(%s)' % self.f

class String(Root):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return 'String(%s)' % self.s

    def hash(self):
        i = 0
        for ch in self.s:
            i += ord(ch)
            i &= 0xFFFFFFFF
            i *= 31
            i &= 0xFFFFFFFF
        return i

class Bytes(Root):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return 'Bytes(...)'

    def hash(self):
        i = 0
        for ch in self.s:
            i += ord(ch)
            i &= 0xFFFFFFFF
            i *= 31
            i &= 0xFFFFFFFF
        return i

class Int(Root):
    def __init__(self, i):
        self.i = i

    def hash(self):
        return self.i

    def __repr__(self):
        return 'Int(%s)' % self.i

    def __str__(self):
        return 'Int(%s)' % self.i

def eq(a, b):
    if isinstance(a, Int) and isinstance(b, Int):
        return a.i == b.i
    else:
        return a is b

def make_float(f):
    assert isinstance(f, float), f
    return Float(f)

def to_float(f):
    assert isinstance(f, Float), f
    return f.f

def is_int(a):
    Root.check(a)
    return isinstance(a, Int)

def block_with_values(tag, arr):
    b = Block(tag=tag, size=len(arr))
    b._fields = list(arr)
    return b

def make_array(arr):
    return block_with_values(tag=0, arr=arr)

def make_string(data):
    assert isinstance(data, str)
    return String(data)

def to_str(data):
    assert isinstance(data, String)
    return data.s

def make_bytes(data):
    # assert isinstance(data, bytearray)
    # return Bytes(data)
    raise Exception('make_bytes')

def to_bytes(data):
    assert isinstance(data, Bytes)
    return data.s

Val_unit = make_int(0)

ATOMS = [ Block(tag=i, size=0) for i in range(256) ]
