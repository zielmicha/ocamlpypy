from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.objectmodel import UnboxedValue

Closure_tag = 247
Object_tag = 248
Infix_tag = 249
String_tag = 252

class Root(object):
    __slots__ = ()
    @staticmethod
    def check(x):
        assert isinstance(x, Root), x

class Int64(Root):
    _immutable_ = True
    __slots__ = ('i',)

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
        return cmp_i(self.i, other.i)

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
    __slots__ = ('i',)
    _immutable_ = True

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
        return cmp_i(self.i, other.i)

class InfixBlock(Root):
    __slots__ = ('_field', '_envoffsettop', '_envoffsetdelta')
    def __init__(self, top, delta):
        self._field = None
        self._envoffsettop = top
        self._envoffsetdelta = delta

    def get_tag(self):
        return Infix_tag

    def field(self, i):
        assert i >= 0
        if i == 0:
            return self._field
        else:
            return self._envoffsettop.field(self._envoffsetdelta + i) # TODO: doesn't seem right!

    def set_field(self, i, v):
        Root.check(v)
        assert i == 0
        self._field = v

    def get_fields(self):
        return [self._field]

    def len_fields(self):
        return 1

    def hash(self):
        return self._field.hash()

    def custom_type_id(self):
        return 8

    def _poly_compare(self, other):
        assert isinstance(other, InfixBlock)
        return poly_compare(self._field, other._field)

    def offset_field(self, n):
        f = n + self._envoffsetdelta
        if f == 0:
            return self._envoffsettop
        else:
            return self._envoffsettop.field(f)

class Block(Root):
    def __init__(self, tag, size):
        assert isinstance(tag, int)
        self._tag = tag
        self._fields = [None]*size

    def offset_field(self, n):
        return self.field(n)

    def field(self, i):
        assert i >= 0
        return self._fields[i]

    def set_field(self, i, v):
        Root.check(v)
        assert i >= 0
        self._fields[i] = v

    def get_fields(self):
        return self._fields

    def len_fields(self):
        return len(self._fields)

    def get_tag(self):
        return self._tag

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
            i += f.hash()
            i &= 0xFFFFFFFF
            i *= 31
            i &= 0xFFFFFFFF
        return i

    def custom_type_id(self):
        return 1

    def _poly_compare(self, other):
        assert isinstance(other, Block)
        if self._tag != other.get_tag():
            return cmp_i(self._tag, other.get_tag())
        else:
            for i in range(min(len(self._fields), len(other.get_fields()))):
                d = poly_compare(self._fields[i], other.get_fields()[i])
                if d != 0: return d

            return cmp_i(len(self._fields), other.len_fields())

def is_block(x):
    return isinstance(x, Block)

def make_block(size, tag):
    b = Block(tag, size)
    return b

def block_tag(block):
    return block.get_tag()

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

def make_int_from_uint(a):
    return Int(intmask(a))

def make_bool(a):
    return Int(1 if a else 0)

class Float(Root):
    _immutable_ = True
    __slots__ = ('f',)

    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return 'Float(%s)' % self.f

    def custom_type_id(self):
        return 7

    def _poly_compare(self, other):
        assert isinstance(other, Float)
        return cmp_f(self.f, other.f)

class String(Root):
    __slots__ = ('data',)
    def __init__(self, s):
        # TODO: use RawBuffer
        self.data = [0]*len(s)
        for i in range(len(s)):
            self.data[i] = ord(s[i])

    def __repr__(self):
        return 'String(%s)' % self.to_str()

    def to_str(self):
        return ''.join([ chr(i) for i in self.data ])

    def len(self):
        return len(self.data)

    def set_at(self, index, val):
        assert val >= 0 and val < 256, val
        self.data[index] = val

    def get_at(self, index):
        return self.data[index]

    def hash(self):
        i = 0
        for ch in self.data:
            i += ch
            i &= 0xFFFFFFFF
            i *= 31
            i &= 0xFFFFFFFF
        return i

    def copy(self):
        return String(self.to_str())

    def custom_type_id(self):
        return 6

    def _poly_compare(self, other):
        assert isinstance(other, String)
        return cmp_s(self.data, other.data)

class Int(Root):
    _immutable_ = True
    __slots__ = ('i',)

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
        return cmp_i(self.i, other.i)

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
    return data.to_str()

def make_bytes(data):
    # assert isinstance(data, bytearray)
    # return Bytes(data)
    raise Exception('make_bytes')

def to_bytes(data):
    assert isinstance(data, String)
    return data.to_str()

def poly_compare(a, b):
    if a.custom_type_id() != b.custom_type_id():
        return cmp_i(a.custom_type_id(), b.custom_type_id())
    else:
        return a._poly_compare(b)

def cmp_f(a, b):
    if a == b: return 0
    if a < b: return -1
    return 1

def cmp_i(a, b):
    if a == b: return 0
    if a < b: return -1
    return 1

def cmp_s(a, b):
    for i in range(min(len(a), len(b))):
        if a[i] < b[i]:
            return -1
        if a[i] > b[i]:
            return 1

    return cmp_i(len(a), len(b))

if True:
    def _test_cmp(a, b): assert cmp_s(a,b)==cmp(a,b)
    _test_cmp("", "foo")
    _test_cmp("foo", "foo")
    _test_cmp("aoo", "foo")
    _test_cmp("a", "aaa")

Val_unit = make_int(0)

ATOMS = [ Block(tag=i, size=0) for i in range(256) ]
