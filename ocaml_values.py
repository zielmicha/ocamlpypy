from rpython.rlib.rarithmetic import r_uint, intmask

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

    def custom_type_id(self):
        return 3

    def _poly_compare(self, other):
        assert isinstance(other, Int64)
        return cmp(self.i, other.i)

def int32_signed_mul(a, b):
    if a >= 2**31: a -= 2**32
    if b >= 2**31: b -= 2**32
    return (a * b) & 0xFFFFFFFF

def int32_signed_div(a, b):
    if a >= 2**31: a -= 2**32
    if b >= 2**31: b -= 2**32
    return (a / b) & 0xFFFFFFFF

def int32_signed_mod(a, b):
    if a >= 2**31: a -= 2**32
    if b >= 2**31: b -= 2**32
    return (a % b) & 0xFFFFFFFF

def int32_signed_rshift(a, b):
    if a >= 2**31: a -= 2**32
    return a >> b

class Int32(Root):
    def __init__(self, i):
        self.i = i & 0xFFFFFFFF

    def __repr__(self):
        return 'Int32(%s)' % self.i

    def hash(self):
        return self.i

    def custom_type_id(self):
        return 4

    def _poly_compare(self, other):
        assert isinstance(other, Int32)
        return cmp(self.i, other.i)

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

    def custom_type_id(self):
        return 1

    def _poly_compare(self, other):
        assert isinstance(other, Block)
        if self._tag != other._tag:
            return cmp(self._tag, other._tag)
        else:
            for i in range(min(len(self._fields), len(other._fields))):
                d = cmp(self._fields[i], other._fields[i])
                if d != 0: return d

            return cmp(len(self._fields), len(other._fields))

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
    return r_uint(a.i) # TODO

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

    def custom_type_id(self):
        return 7

    def _poly_compare(self, other):
        assert isinstance(other, Float)
        return cmp(self.f, other.f)

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

    def custom_type_id(self):
        return 6

    def _poly_compare(self, other):
        assert isinstance(other, String)
        return cmp(self.s, other.s)

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

    def custom_type_id(self):
        return 5

    def _poly_compare(self, other):
        assert isinstance(other, Bytes)
        return cmp(self.s, other.s)

class Int(Root):
    def __init__(self, i):
        self.i = i

    def hash(self):
        return self.i

    def __repr__(self):
        return 'Int(%s)' % self.i

    def __str__(self):
        return 'Int(%s)' % self.i

    def custom_type_id(self):
        return 2

    def _poly_compare(self, other):
        assert isinstance(other, Int)
        return cmp(self.i, other.i)

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

def poly_compare(a, b):
    if a.custom_type_id() != b.custom_type_id():
        return cmp(a.custom_type_id(), b.custom_type_id())
    else:
        return a._poly_compare(b)

Val_unit = make_int(0)

ATOMS = [ Block(tag=i, size=0) for i in range(256) ]
