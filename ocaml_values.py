
Closure_tag = 247
Object_tag = 248
Infix_tag = 249
String_tag = 252
Val_unit = 0

class Root(object):
    @staticmethod
    def check(x):
        assert isinstance(x, Root), x

class Int64(Root):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'Int64(%s)' % self.i

class Int32(Root):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'Int32(%s)' % self.i

class Block(Root):
    def __init__(self, tag, size):
        assert isinstance(tag, int)
        self._tag = tag
        self._fields = [None]*size
        self._envoffsettop = None
        self._envoffsetdelta = None

    def field(self, i):
        if i >= len(self._fields):
            raise IndexError('field %d out of %d, top=%d/%s' % (i, len(self._fields), self._envoffsetdelta, self._envoffsettop))
            return self._envoffsettop.field(i + self._envoffsetdelta).field(0)
        return self._fields[i]

    def set_field(self, i, v):
        Root.check(v)
        self._fields[i] = v

    def __repr__(self):
        #return 'Block(%d, s=%d)' % (self._tag, len(self._fields))
        #return 'Block#%x(%d, %s)' % (id(self), self._tag, self._fields)
        return 'Block(%d, %s)' % (self._tag, self._fields)

    def __hash__(self):
        return hash((self._tag, self._fields))

def is_block(x):
    return isinstance(x, Block)

ATOMS = [ Block(tag=i, size=0) for i in range(256) ]

def make_block(size, tag):
    b = Block(tag, size)
    return b

def block_tag(block):
    return block._tag

def is_true(a):
    return a != Int(0)

def to_int(a):
    assert isinstance(a, Int), repr(a)
    return a.i

def to_uint(a):
    assert isinstance(a, Int), repr(a)
    return a.i # TODO

def make_int(a):
    assert isinstance(a, (int, long)), a
    return Int(a)

class Float(Root):
    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return 'Float(%s)' % self.f

class String(Root):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return 'String(%r)' % self.s

class Bytes(Root):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return 'Bytes(%r)' % str(self.s)

class Int(Root):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'Int(%s)' % self.i

    def __eq__(self, a):
        if not isinstance(a, Int): return False
        return self.i == a.i

    def __cmp__(self, a):
        raise Exception('not supported')

    def __ne__(self, a):
        if not isinstance(a, Int): return False
        return self.i != a.i

    def __lt__(self, a):
        assert isinstance(a, Int)
        return self.i < a.i

    def __gt__(self, a):
        assert isinstance(a, Int)
        return self.i > a.i

    def __le__(self, a):
        assert isinstance(a, Int)
        return self.i <= a.i

    def __ge__(self, a):
        assert isinstance(a, Int)
        return self.i >= a.i

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
    assert type(data) == str
    return String(data)

def to_str(data):
    assert isinstance(data, String)
    return data.s

def make_bytes(data):
    assert type(data) == bytearray
    return String(data)

def to_bytes(data):
    assert type(data) == Bytes
    return data.s
