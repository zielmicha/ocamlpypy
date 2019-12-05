from __future__ import print_function
import struct, sys, array

trailer_magic = b'Caml1999X011'

def parse_executable(data):
    if not data.endswith(trailer_magic):
        raise Exception('invalid magic %r' % data[-len(trailer_magic):])

    pos = len(data)
    pos -= len(trailer_magic)
    pos -= 4
    num_sections, = struct.unpack('>I', data[pos:pos + 4])

    sections = []
    for i in range(num_sections):
        pos -= 8
        name = data[pos:pos+4].decode()
        length, = struct.unpack('>I', data[pos+4:pos+8])
        sections.append((name, length))

    section_data = {}
    for name, length in sections:
        pos -= length
        section_data[name] = data[pos : pos + length]

    return section_data

Closure_tag = 247
Infix_tag = 249
Val_unit = 0

opcode_list = [ 'OP_ACC0', 'OP_ACC1', 'OP_ACC2', 'OP_ACC3', 'OP_ACC4', 'OP_ACC5', 'OP_ACC6', 'OP_ACC7', 'OP_ACC', 'OP_PUSH', 'OP_PUSHACC0', 'OP_PUSHACC1', 'OP_PUSHACC2', 'OP_PUSHACC3', 'OP_PUSHACC4', 'OP_PUSHACC5', 'OP_PUSHACC6', 'OP_PUSHACC7', 'OP_PUSHACC', 'OP_POP', 'OP_ASSIGN', 'OP_ENVACC1', 'OP_ENVACC2', 'OP_ENVACC3', 'OP_ENVACC4', 'OP_ENVACC', 'OP_PUSHENVACC1', 'OP_PUSHENVACC2', 'OP_PUSHENVACC3', 'OP_PUSHENVACC4', 'OP_PUSHENVACC', 'OP_PUSH_RETADDR', 'OP_APPLY', 'OP_APPLY1', 'OP_APPLY2', 'OP_APPLY3', 'OP_APPTERM', 'OP_APPTERM1', 'OP_APPTERM2', 'OP_APPTERM3', 'OP_RETURN', 'OP_RESTART', 'OP_GRAB', 'OP_CLOSURE', 'OP_CLOSUREREC', 'OP_OFFSETCLOSUREM2', 'OP_OFFSETCLOSURE0', 'OP_OFFSETCLOSURE2', 'OP_OFFSETCLOSURE', 'OP_PUSHOFFSETCLOSUREM2', 'OP_PUSHOFFSETCLOSURE0', 'OP_PUSHOFFSETCLOSURE2', 'OP_PUSHOFFSETCLOSURE', 'OP_GETGLOBAL', 'OP_PUSHGETGLOBAL', 'OP_GETGLOBALFIELD', 'OP_PUSHGETGLOBALFIELD', 'OP_SETGLOBAL', 'OP_ATOM0', 'OP_ATOM', 'OP_PUSHATOM0', 'OP_PUSHATOM', 'OP_MAKEBLOCK', 'OP_MAKEBLOCK1', 'OP_MAKEBLOCK2', 'OP_MAKEBLOCK3', 'OP_MAKEFLOATBLOCK', 'OP_GETFIELD0', 'OP_GETFIELD1', 'OP_GETFIELD2', 'OP_GETFIELD3', 'OP_GETFIELD', 'OP_GETFLOATFIELD', 'OP_SETFIELD0', 'OP_SETFIELD1', 'OP_SETFIELD2', 'OP_SETFIELD3', 'OP_SETFIELD', 'OP_SETFLOATFIELD', 'OP_VECTLENGTH', 'OP_GETVECTITEM', 'OP_SETVECTITEM', 'OP_GETBYTESCHAR', 'OP_SETBYTESCHAR', 'OP_BRANCH', 'OP_BRANCHIF', 'OP_BRANCHIFNOT', 'OP_SWITCH', 'OP_BOOLNOT', 'OP_PUSHTRAP', 'OP_POPTRAP', 'OP_RAISE', 'OP_CHECK_SIGNALS', 'OP_C_CALL1', 'OP_C_CALL2', 'OP_C_CALL3', 'OP_C_CALL4', 'OP_C_CALL5', 'OP_C_CALLN', 'OP_CONST0', 'OP_CONST1', 'OP_CONST2', 'OP_CONST3', 'OP_CONSTINT', 'OP_PUSHCONST0', 'OP_PUSHCONST1', 'OP_PUSHCONST2', 'OP_PUSHCONST3', 'OP_PUSHCONSTINT', 'OP_NEGINT', 'OP_ADDINT', 'OP_SUBINT', 'OP_MULINT', 'OP_DIVINT', 'OP_MODINT', 'OP_ANDINT', 'OP_ORINT', 'OP_XORINT', 'OP_LSLINT', 'OP_LSRINT', 'OP_ASRINT', 'OP_EQ', 'OP_NEQ', 'OP_LTINT', 'OP_LEINT', 'OP_GTINT', 'OP_GEINT', 'OP_OFFSETINT', 'OP_OFFSETREF', 'OP_ISINT', 'OP_GETMETHOD', 'OP_BEQ', 'OP_BNEQ', 'OP_BLTINT', 'OP_BLEINT', 'OP_BGTINT', 'OP_BGEINT', 'OP_ULTINT', 'OP_UGEINT', 'OP_BULTINT', 'OP_BUGEINT', 'OP_GETPUBMET', 'OP_GETDYNMET', 'OP_STOP', 'OP_EVENT', 'OP_BREAK', 'OP_RERAISE', 'OP_RAISE_NOTRACE', 'OP_GETSTRINGCHAR' ]

for _i, _opcode in enumerate(opcode_list):
    globals()[_opcode] = _i

def dbg(*args):
    #print(*args)
    pass

class Prims:
    def __init__(self, names):
        self.names = names

    def call(self, index, *args):
        name = self.names[index]
        getattr(self, name)(*args)

    def caml_register_named_value(self, vname, val):
        print('named:', vname, val)

    def caml_fresh_oo_id(self, _):
        return make_int(666)

    def caml_int64_float_of_bits(self, _):
        return 0 # TODO

    def caml_ml_open_descriptor_in(self, _):
        return 0 # TODO

    def caml_ml_open_descriptor_out(self, _):
        return 0 # TODO

    def caml_ml_out_channels_list(self, _):
        return 0 # TODO

    def caml_ml_output_char(self, channel, ch):
        print('out', channel, chr(ch))

class Block:
    def __init__(self, tag, size):
        self._tag = tag
        self._fields = [None]*size

    def field(self, i):
        return self._fields[i]

    def set_field(self, i, v):
        self._fields[i] = v

    def __repr__(self):
        #return 'Block(%d, s=%d)' % (self._tag, len(self._fields))
        #return 'Block#%x(%d, %s)' % (id(self), self._tag, self._fields)
        return 'Block(%d, %s)' % (self._tag, self._fields)

ATOMS = [ Block(tag=i, size=0) for i in range(256) ]

def make_block(size, tag):
    b = Block(tag, size)
    return b

def is_true(a):
    return bool(a)

def to_int(a):
    return a

def to_uint(a):
    return a # TODO

def make_int(a):
    return a

def set_code_val(block, pc):
    block.set_field(0, make_int(pc & 0xFFFFFFFF))

def code_val(block):
    return to_int(block.field(0)) & 0xFFFFFFFF

def eval_bc(prims, global_data, bc, stack):
    accu = 0
    extra_args = 0
    env = None
    pc = 0

    def unsupp():
        raise Exception('unsupported instr %d = %s' % (instr, opcode_list[instr]))

    def push(v):
        stack.append(v)

    def sp(k):
        return stack[len(stack) - 1 - k]

    def pop():
        return stack.pop()

    def c_call(n, *args):
        return prims.call(n, *args)

    while True:
        instr = bc[pc]
        pc += 1
        dbg('pc', pc, 'instr', opcode_list[instr], 'accu', accu)

        if instr == OP_ACC0:
            accu = sp(0)
        elif instr == OP_ACC1:
            accu = sp(1)
        elif instr == OP_ACC2:
            accu = sp(2)
        elif instr == OP_ACC3:
            accu = sp(3)
        elif instr == OP_ACC4:
            accu = sp(4)
        elif instr == OP_ACC5:
            accu = sp(5)
        elif instr == OP_ACC6:
            accu = sp(6)
        elif instr == OP_ACC7:
            accu = sp(7)
        elif instr == OP_ACC:
            accu = sp(bc[pc])
            pc += 1
        elif instr == OP_PUSH:
            push(accu)
        elif instr == OP_PUSHACC0:
            push(accu)
        elif instr == OP_PUSHACC1:
            push(accu)
            accu = sp(1)
        elif instr == OP_PUSHACC2:
            push(accu)
            accu = sp(2)
        elif instr == OP_PUSHACC3:
            push(accu)
            accu = sp(3)
        elif instr == OP_PUSHACC4:
            push(accu)
            accu = sp(4)
        elif instr == OP_PUSHACC5:
            push(accu)
            accu = sp(5)
        elif instr == OP_PUSHACC6:
            push(accu)
            accu = sp(6)
        elif instr == OP_PUSHACC7:
            push(accu)
            accu = sp(7)
        elif instr == OP_PUSHACC:
            push(accu)
            accu = sp(bc[pc])
            pc += 1
        elif instr == OP_POP:
            for i in range(bc[pc]):
                pop()
            pc += 1
        elif instr == OP_ASSIGN:
            sp_set(bc[pc], accu)
            pc += 1
            accu = Val_unit
        elif instr == OP_ENVACC1:
            accu = env.field(1)
        elif instr == OP_ENVACC2:
            accu = env.field(2)
        elif instr == OP_ENVACC3:
            accu = env.field(3)
        elif instr == OP_ENVACC4:
            accu = env.field(4)
        elif instr == OP_ENVACC:
            accu = env.field(bc[pc])
            pc += 1
        elif instr == OP_PUSHENVACC1:
            push(accu)
            accu = env.field(1)
        elif instr == OP_PUSHENVACC2:
            push(accu)
            accu = env.field(2)
        elif instr == OP_PUSHENVACC3:
            push(accu)
            accu = env.field(3)
        elif instr == OP_PUSHENVACC4:
            push(accu)
            accu = env.field(4)
        elif instr == OP_PUSHENVACC:
            push(accu)
            accu = env.field(bc[pc])
            pc += 1
        elif instr == OP_PUSH_RETADDR:
            push(extra_args)
            push(Env)
            push(pc + bc[pc])
            pc += 1
        elif instr == OP_APPLY:
            extra_args = bc[pc]-1
            pc = code_val(accu)
            env = accu
        elif instr == OP_APPLY1:
            arg1 = sp(0)
            pop()
            push(make_int(extra_args))
            push(env)
            push(make_int(pc))
            push(arg1)
            dbg('calling', accu)
            pc = code_val(accu)
            env = accu
            extra_args = 0
        elif instr == OP_APPLY2:
            unsupp()
        elif instr == OP_APPLY3:
            unsupp()
        elif instr == OP_APPTERM:
            nargs = bc[pc]
            pc += 1
            slotsize = bc[pc]
            newsp = slotsize - nargs
            i = nargs - 1
            while i >= 0:
                set_sp(newsp + i, i)
                i -= 1
            for _ in range(newsp): pop()
            pc = code_val(accu)
            env = accu
            extra_args += nargs - 1
        elif instr == OP_APPTERM1:
            arg1 = sp(0)
            for _ in range(bc[pc]): pop()
            push(arg1)
            dbg('calling', accu)
            pc = code_val(accu)
            env = accu
        elif instr == OP_APPTERM2:
            unsupp()
        elif instr == OP_APPTERM3:
            unsupp()
        elif instr == OP_RETURN:
            npop = bc[pc]
            pc += 1
            for _ in range(npop): pop()

            if extra_args > 0:
                extra_args -= 1
                pc = code_val(accu)
                env = accu
            else:
                pc = pop()
                env = pop()
                extra_args = to_int(pop())
        elif instr == OP_RESTART:
            unsupp()
        elif instr == OP_GRAB:
            unsupp()
        elif instr == OP_CLOSURE:
            nvars = bc[pc]
            pc += 1

            if nvars > 0:
                push(accu)

            accu = make_block(1 + nvars, Closure_tag)
            dbg('closure', accu, nvars, pc + bc[pc])
            for i in range(nvars):
                dbg('closure var', sp(0))
                accu.set_field(i + 1, sp(0))
                pop()

            set_code_val(accu, pc + bc[pc])
            pc += 1
        elif instr == OP_CLOSUREREC:
            nfuncs = bc[pc]
            pc += 1
            nvars = bc[pc]
            pc += 1

            blksize = nfuncs * 2 - 1 + nvars
            if nvars > 0:
                push(accu)

            accu = make_block(blksize, Closure_tag)
            for i in range(nvars):
                accu.set_field(nfucs * 2 - 1 + i, sp(0))
                pop()

            accu.set_field(0, pc + bc[pc])
            push(accu)
            # TODO: not accurate
            for i in range(1, nfuncs):
                b = make_block(1, Infix_tag)
                b.set_field(0, bc[pc + i])
                push(b)
            pc += nfuncs

        elif instr == OP_OFFSETCLOSUREM2:
            unsupp()
        elif instr == OP_OFFSETCLOSURE0:
            unsupp()
        elif instr == OP_OFFSETCLOSURE2:
            unsupp()
        elif instr == OP_OFFSETCLOSURE:
            unsupp()
        elif instr == OP_PUSHOFFSETCLOSUREM2:
            unsupp()
        elif instr == OP_PUSHOFFSETCLOSURE0:
            unsupp()
        elif instr == OP_PUSHOFFSETCLOSURE2:
            unsupp()
        elif instr == OP_PUSHOFFSETCLOSURE:
            unsupp()
        elif instr == OP_GETGLOBAL:
            n = bc[pc]
            pc += 1
            accu = global_data[n]
        elif instr == OP_PUSHGETGLOBAL:
            push(accu)
            n = bc[pc]
            pc += 1
            accu = global_data[n]
        elif instr == OP_GETGLOBALFIELD:
            n = bc[pc]
            pc += 1
            accu = global_data[n]
            n = bc[pc]
            pc += 1
            accu = accu.field(n)
        elif instr == OP_PUSHGETGLOBALFIELD:
            push(accu)
            n = bc[pc]
            pc += 1
            accu = global_data[n]
            dbg('get', n, '->', accu)
            n = bc[pc]
            pc += 1
            dbg('__ field', n, accu.field(n))
            accu = accu.field(n)
        elif instr == OP_SETGLOBAL:
            n = bc[pc]
            pc += 1
            global_data[n] = accu
            dbg('global', n, accu)
            accu = Val_unit
        elif instr == OP_ATOM0:
            accu = ATOMS[0]
        elif instr == OP_ATOM:
            n = bc[pc]
            pc += 1
            accu = ATOMS[n]
        elif instr == OP_PUSHATOM0:
            push(accu)
            accu = ATOMS[0]
        elif instr == OP_PUSHATOM:
            push(accu)
            n = bc[pc]
            pc += 1
            accu = ATOMS[n]
        elif instr == OP_MAKEBLOCK:
            wosize = bc[pc]
            pc += 1
            tag = bc[pc]
            pc += 1

            b = make_block(wosize, tag)
            b.set_field(0, accu)
            for i in range(1, wosize):
                b.set_field(i, pop())
            accu = b
        elif instr == OP_MAKEBLOCK1:
            tag = bc[pc]
            pc += 1
            b = make_block(1, tag)
            b.set_field(0, accu)
            accu = b
        elif instr == OP_MAKEBLOCK2:
            tag = bc[pc]
            pc += 1
            b = make_block(2, tag)
            b.set_field(0, accu)
            b.set_field(0, pop())
            accu = b
        elif instr == OP_MAKEBLOCK3:
            tag = bc[pc]
            pc += 1
            b = make_block(3, tag)
            b.set_field(0, accu)
            b.set_field(0, pop())
            b.set_field(0, pop())
            accu = b
        elif instr == OP_MAKEFLOATBLOCK:
            1/0
        elif instr == OP_GETFIELD0:
            accu = accu.field(0)
        elif instr == OP_GETFIELD1:
            accu = accu.field(1)
        elif instr == OP_GETFIELD2:
            accu = accu.field(2)
        elif instr == OP_GETFIELD3:
            accu = accu.field(3)
        elif instr == OP_GETFIELD:
            n = bc[pc]
            pc += 1
            accu = accu.field(n)
        elif instr == OP_GETFLOATFIELD:
            1/0
        elif instr == OP_SETFIELD0:
            accu.set_field(0, sp(0))
            pop()
            accu = Val_unit
        elif instr == OP_SETFIELD1:
            accu.set_field(1, sp(0))
            pop()
            accu = Val_unit
        elif instr == OP_SETFIELD2:
            accu.set_field(2, sp(0))
            pop()
            accu = Val_unit
        elif instr == OP_SETFIELD3:
            accu.set_field(3, sp(0))
            pop()
            accu = Val_unit
        elif instr == OP_SETFIELD:
            n = bc[pc]
            pc += 1
            accu.set_field(n, sp(0))
            pop()
            accu = Val_unit
        elif instr == OP_SETFLOATFIELD:
            unsupp()
        elif instr == OP_VECTLENGTH:
            unsupp()
        elif instr == OP_GETVECTITEM:
            unsupp()
        elif instr == OP_SETVECTITEM:
            unsupp()
        elif instr == OP_GETBYTESCHAR:
            unsupp()
        elif instr == OP_SETBYTESCHAR:
            unsupp()
        elif instr == OP_BRANCH:
            pc += bc[pc]
        elif instr == OP_BRANCHIF:
            if is_true(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_BRANCHIFNOT:
            if not is_true(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_SWITCH:
            sizes = bc[pc]
            pc += 1
            if is_block(accu):
                index = block_tag(accu)
                assert index < (sizes >> 16)
                pc += pc[(sizes & 0xFFFF) + index]
            else:
                index = to_int(accu)
                assert index < (sizes & 0xFFFF)
                pc += bc[pc + index]
        elif instr == OP_BOOLNOT:
            accu = make_int(1 - to_int(accu))
        elif instr == OP_PUSHTRAP:
            unsupp()
        elif instr == OP_POPTRAP:
            unsupp()
        elif instr == OP_RAISE:
            unsupp()
        elif instr == OP_CHECK_SIGNALS:
            unsupp()
        elif instr == OP_C_CALL1:
            n = bc[pc]
            pc += 1
            accu = c_call(n, accu)
        elif instr == OP_C_CALL2:
            n = bc[pc]
            pc += 1
            accu = c_call(n, accu, sp(0))
            pop()
        elif instr == OP_C_CALL3:
            n = bc[pc]
            pc += 1
            accu = c_call(n, accu, sp(0), sp(1))
            pop()
            pop()
        elif instr == OP_C_CALL4:
            n = bc[pc]
            pc += 1
            accu = c_call(n, accu, sp(0), sp(1), sp(2))
            pop()
            pop()
            pop()
        elif instr == OP_C_CALL5:
            n = bc[pc]
            pc += 1
            accu = c_call(n, accu, sp(0), sp(1), sp(2), sp(3))
            pop()
            pop()
            pop()
            pop()
        elif instr == OP_C_CALLN:
            unsupp()
        elif instr == OP_CONST0:
            accu = make_int(0)
        elif instr == OP_CONST1:
            accu = make_int(1)
        elif instr == OP_CONST2:
            accu = make_int(2)
        elif instr == OP_CONST3:
            accu = make_int(3)
        elif instr == OP_CONSTINT:
            accu = make_int(bc[pc])
            pc += 1
        elif instr == OP_PUSHCONST0:
            push(accu)
            accu = make_int(0)
        elif instr == OP_PUSHCONST1:
            push(accu)
            accu = make_int(1)
        elif instr == OP_PUSHCONST2:
            push(accu)
            accu = make_int(2)
        elif instr == OP_PUSHCONST3:
            push(accu)
            accu = make_int(3)
        elif instr == OP_PUSHCONSTINT:
            push(accu)
            accu = make_int(bc[pc])
            pc += 1
        elif instr == OP_NEGINT:
            accu = make_int(0 if is_true(accu) else 1)
        elif instr == OP_ADDINT:
            accu = make_int(to_int(accu) + to_int(pop()))
        elif instr == OP_SUBINT:
            accu = make_int(to_int(accu) - to_int(pop()))
        elif instr == OP_MULINT:
            accu = make_int(to_int(accu) * to_int(pop()))
        elif instr == OP_DIVINT:
            accu = make_int(to_int(accu) / to_int(pop()))
        elif instr == OP_MODINT:
            accu = make_int(to_int(accu) % to_int(pop()))
        elif instr == OP_ANDINT:
            accu = make_int(to_int(accu) & to_int(pop()))
        elif instr == OP_ORINT:
            accu = make_int(to_int(accu) | to_int(pop()))
        elif instr == OP_XORINT:
            accu = make_int(to_int(accu) ^ to_int(pop()))
        elif instr == OP_LSLINT:
            accu = make_int(to_int(accu) << pop())
        elif instr == OP_LSRINT:
            accu = make_int(to_uint(accu) >> pop()) # TODO: logical shift
        elif instr == OP_ASRINT:
            accu = make_int(to_int(accu) >> pop()) # TODO: artmetic shift
        elif instr == OP_EQ:
            unsupp()
        elif instr == OP_NEQ:
            unsupp()
        elif instr == OP_LTINT:
            unsupp()
        elif instr == OP_LEINT:
            unsupp()
        elif instr == OP_GTINT:
            unsupp()
        elif instr == OP_GEINT:
            unsupp()
        elif instr == OP_OFFSETINT:
            accu += bc[pc]
            pc += 1
        elif instr == OP_OFFSETREF:
            accu.set_field(0, accu.get_field(0) + bc[pc])
            pc += 1
            accu = Val_unit
        elif instr == OP_ISINT:
            unsupp()
        elif instr == OP_GETMETHOD:
            unsupp()
        elif instr == OP_BEQ:
            unsupp()
        elif instr == OP_BNEQ:
            unsupp()
        elif instr == OP_BLTINT:
            unsupp()
        elif instr == OP_BLEINT:
            unsupp()
        elif instr == OP_BGTINT:
            unsupp()
        elif instr == OP_BGEINT:
            unsupp()
        elif instr == OP_ULTINT:
            unsupp()
        elif instr == OP_UGEINT:
            unsupp()
        elif instr == OP_BULTINT:
            unsupp()
        elif instr == OP_BUGEINT:
            unsupp()
        elif instr == OP_GETPUBMET:
            unsupp()
        elif instr == OP_GETDYNMET:
            unsupp()
        elif instr == OP_STOP:
            return accu
        elif instr == OP_EVENT:
            unsupp()
        elif instr == OP_BREAK:
            unsupp()
        elif instr == OP_RERAISE:
            unsupp()
        elif instr == OP_RAISE_NOTRACE:
            unsupp()
        elif instr == OP_GETSTRINGCHAR:
            unsupp()
        else:
            raise Exception('invalid opcode %d' % instr)

if __name__ == '__main__':
    exe_dict = parse_executable(open(sys.argv[1], 'rb').read())
    bytecode = array.array('I', exe_dict['CODE'])
    prims = Prims(exe_dict['PRIM'].decode().split('\0'))
    print( { k:len(v) for k,v in exe_dict.items() })
    stack = []
    global_data = [ 'globaltaint%d' % i for i in range(100) ]
    eval_bc(prims=prims, global_data=global_data, bc=bytecode, stack=stack)
