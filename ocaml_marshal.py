import my_struct as struct
from ocaml_values import *

PREFIX_SMALL_BLOCK = 0x80
PREFIX_SMALL_INT = 0x40
PREFIX_SMALL_STRING = 0x20
CODE_INT8 = 0x0
CODE_INT16 = 0x1
CODE_INT32 = 0x2
CODE_INT64 = 0x3
CODE_SHARED8 = 0x4
CODE_SHARED16 = 0x5
CODE_SHARED32 = 0x6
CODE_SHARED64 = 0x14
CODE_BLOCK32 = 0x8
CODE_BLOCK64 = 0x13
CODE_STRING8 = 0x9
CODE_STRING32 = 0xA
CODE_STRING64 = 0x15
CODE_DOUBLE_BIG = 0xB
CODE_DOUBLE_LITTLE = 0xC
CODE_DOUBLE_ARRAY8_BIG = 0xD
CODE_DOUBLE_ARRAY8_LITTLE = 0xE
CODE_DOUBLE_ARRAY32_BIG = 0xF
CODE_DOUBLE_ARRAY32_LITTLE = 0x7
CODE_DOUBLE_ARRAY64_BIG = 0x16
CODE_DOUBLE_ARRAY64_LITTLE = 0x17
CODE_CODEPOINTER = 0x10
CODE_INFIXPOINTER = 0x11
CODE_CUSTOM = 0x12
CODE_CUSTOM_LEN = 0x18
CODE_CUSTOM_FIXED = 0x19

trailer_magic = b'Caml1999X011'

def parse_executable(data):
    if not data.endswith(trailer_magic):
        raise Exception('invalid magic %s' % data[max(0, len(data)-len(trailer_magic)):])

    pos = len(data)
    pos -= len(trailer_magic)
    pos -= 4
    assert pos >= 0
    num_sections, = struct.unpack('>I', data[pos:pos + 4])

    sections = []
    for i in range(num_sections):
        pos -= 8
        assert pos >= 0
        name = data[pos:pos+4]
        length, = struct.unpack('>I', data[pos+4:pos+8])
        sections.append((name, length))

    section_data = {}
    for name, length in sections:
        pos -= length
        assert length >= 0
        assert pos >= 0
        section_data[name] = data[pos : pos + length]

    return section_data

class MyStringIO:
    def __init__(self, data_str):
        self.data_str = data_str
        self.pos = 0

    def read(self, n=10000000):
        assert n >= 0
        r = self.data_str[self.pos : self.pos + n]
        self.pos += n
        return r

def unmarshal(data_str):
    data = MyStringIO(data_str)

    header = data.read(20)
    magic, = struct.unpack('>I', header[:4])
    if magic == 0x8495A6BF:
        header += data.read(12)

        #_, data_len, num_objects, whsize = struct.unpack('>ILLL', header[4:])
        data_len, = struct.unpack('>L', header[4 + 4:4 + 12])
        num_objects, = struct.unpack('>L', header[4 + 12:4 + 20])
        whsize, = struct.unpack('>L', header[4 + 20:])
    elif magic == 0x8495A6BE:
        #data_len, num_objects, _, whsize = struct.unpack('>IIII', header[4:])
        data_len, = struct.unpack('>I', header[4:8])
        num_objects, = struct.unpack('>I', header[8:12])
        whsize, = struct.unpack('>I', header[16:20])
    else:
        raise Exception('bad magic')

    v = Unmarshaler().unmarshal(data)
    leftover = data.read()
    #for vv in v._fields: print('-', repr(vv))
    assert not leftover
    return v

class Unmarshaler:
    def __init__(self):
        self.intern_table = []
        self._lvl = 0

    def intern(self, o):
        Root.check(o)
        self.intern_table.append(o)
        return o

    def _block(self, data, tag, size):
        if size == 0:
            v = ATOMS[tag]
        else:
            v = self.intern(block_with_values(tag, [
                self.unmarshal(data)
                for _ in range(size)
            ]))

            if tag == Object_tag:
                # TODO: refresh obj id
                #return '_objects_not_supported'
                return v

            return v

    def get_shared(self, id):
        assert id > 0, id
        assert id <= len(self.intern_table), (id, len(self.intern_table))
        return self.intern_table[len(self.intern_table)-id]

    def unmarshal(self, data):
        lvl = self._lvl
        self._lvl += 1

        code, = struct.unpack('<B', data.read(1))

        def _wosize_hd(hd): return hd >> 10
        def _tag_hd(hd): return hd & 0xFF

        if code >= PREFIX_SMALL_INT:
            if code >= PREFIX_SMALL_BLOCK:
                tag = code & 0xF
                size = (code >> 4) & 0x7
                return self._block(data, tag, size)
            else:
                return make_int(code & 0x3F)
        else:
            if code >= PREFIX_SMALL_STRING:
                length = code & 0x1F
                return self.intern(make_string(data.read(length)))
            else:
                if code == CODE_INT8:
                    i, = struct.unpack('>b', data.read(1))
                    return make_int(i)
                if code == CODE_INT16:
                    i, = struct.unpack('>h', data.read(2))
                    return make_int(i)
                if code == CODE_INT32:
                    i, = struct.unpack('>i', data.read(4))
                    return make_int(i)
                if code == CODE_INT64:
                    i, = struct.unpack('>q', data.read(8))
                    return make_int(i)
                if code == CODE_BLOCK32:
                    hd, = struct.unpack('>I', data.read(4))
                    return self._block(data, _tag_hd(hd), _wosize_hd(hd))
                #if code == CODE_BLOCK64:
                #    hd, = struct.unpack('>Q', data.read(8))
                #    return self._block(data, _tag_hd(hd), _wosize_hd(hd))
                if code == CODE_STRING8:
                    len, = struct.unpack('<B', data.read(1))
                    return self.intern(make_string(data.read(len)))
                if code == CODE_STRING32:
                    len, = struct.unpack('>I', data.read(4))
                    return self.intern(make_string(data.read(len)))
                if code == CODE_SHARED8:
                    id, = struct.unpack('<B', data.read(1))
                    return self.get_shared(id)
                if code == CODE_SHARED16:
                    id, = struct.unpack('>H', data.read(2))
                    return self.get_shared(id)
                if code == CODE_SHARED32:
                    id, = struct.unpack('>I', data.read(4))
                    return self.get_shared(id)
                if code == CODE_CUSTOM:
                    id = data.read(3)
                    if id == '_j\0':
                        n, = struct.unpack('<q', data.read(8))
                        return Int64(n)
                    elif id == '_n\0': # nativeint
                        t, = struct.unpack('<B', data.read(1))
                        if t == 2:
                            n, = struct.unpack('>q', data.read(8))
                        elif t == 1:
                            n, = struct.unpack('>i', data.read(4))
                        else:
                            raise Exception('bad tag')
                        # print('nativeint', id, n, t)
                        return Int64(n)
                    elif id == '_i\0':
                        n, = struct.unpack('<i', data.read(4))
                        return Int32(n)
                    else:
                        raise Exception('unknown custom %s' % id)
                if code == CODE_DOUBLE_LITTLE:
                    f = make_float(struct.unpack('<d', data.read(8))[0])
                    return self.intern(f)
                if code == CODE_DOUBLE_ARRAY32_LITTLE:
                    len, = struct.unpack('>I', data.read(32))
                    return self.intern(make_array([
                        make_float(struct.unpack('<d', data.read(8))[0])
                        for i in range(len)
                    ]))
                if code == CODE_DOUBLE_ARRAY8_LITTLE:
                    len, = struct.unpack('>B', data.read(1))
                    return self.intern(make_array([
                        make_float(struct.unpack('<d', data.read(8))[0])
                        for i in range(len)
                    ]))

                raise Exception('code 0x%x' % code)
