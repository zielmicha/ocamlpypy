from __future__ import print_function
import struct, sys, array, io, os
import colorama
from ocaml_values import *
from ocaml_marshal import unmarshal

trailer_magic = b'Caml1999X011'

def parse_executable(data):
    if not data.endswith(trailer_magic):
        raise Exception('invalid magic %r' % data[-len(trailer_magic):])

    pos = len(data)
    pos -= len(trailer_magic)
    pos -= 4
    assert pos >= 0
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

def trace_call(env, args):
    dbg(lambda: ('call', code_val(env), args))

opcode_list = [ 'OP_ACC0', 'OP_ACC1', 'OP_ACC2', 'OP_ACC3', 'OP_ACC4', 'OP_ACC5', 'OP_ACC6', 'OP_ACC7', 'OP_ACC', 'OP_PUSH', 'OP_PUSHACC0', 'OP_PUSHACC1', 'OP_PUSHACC2', 'OP_PUSHACC3', 'OP_PUSHACC4', 'OP_PUSHACC5', 'OP_PUSHACC6', 'OP_PUSHACC7', 'OP_PUSHACC', 'OP_POP', 'OP_ASSIGN', 'OP_ENVACC1', 'OP_ENVACC2', 'OP_ENVACC3', 'OP_ENVACC4', 'OP_ENVACC', 'OP_PUSHENVACC1', 'OP_PUSHENVACC2', 'OP_PUSHENVACC3', 'OP_PUSHENVACC4', 'OP_PUSHENVACC', 'OP_PUSH_RETADDR', 'OP_APPLY', 'OP_APPLY1', 'OP_APPLY2', 'OP_APPLY3', 'OP_APPTERM', 'OP_APPTERM1', 'OP_APPTERM2', 'OP_APPTERM3', 'OP_RETURN', 'OP_RESTART', 'OP_GRAB', 'OP_CLOSURE', 'OP_CLOSUREREC', 'OP_OFFSETCLOSUREM2', 'OP_OFFSETCLOSURE0', 'OP_OFFSETCLOSURE2', 'OP_OFFSETCLOSURE', 'OP_PUSHOFFSETCLOSUREM2', 'OP_PUSHOFFSETCLOSURE0', 'OP_PUSHOFFSETCLOSURE2', 'OP_PUSHOFFSETCLOSURE', 'OP_GETGLOBAL', 'OP_PUSHGETGLOBAL', 'OP_GETGLOBALFIELD', 'OP_PUSHGETGLOBALFIELD', 'OP_SETGLOBAL', 'OP_ATOM0', 'OP_ATOM', 'OP_PUSHATOM0', 'OP_PUSHATOM', 'OP_MAKEBLOCK', 'OP_MAKEBLOCK1', 'OP_MAKEBLOCK2', 'OP_MAKEBLOCK3', 'OP_MAKEFLOATBLOCK', 'OP_GETFIELD0', 'OP_GETFIELD1', 'OP_GETFIELD2', 'OP_GETFIELD3', 'OP_GETFIELD', 'OP_GETFLOATFIELD', 'OP_SETFIELD0', 'OP_SETFIELD1', 'OP_SETFIELD2', 'OP_SETFIELD3', 'OP_SETFIELD', 'OP_SETFLOATFIELD', 'OP_VECTLENGTH', 'OP_GETVECTITEM', 'OP_SETVECTITEM', 'OP_GETBYTESCHAR', 'OP_SETBYTESCHAR', 'OP_BRANCH', 'OP_BRANCHIF', 'OP_BRANCHIFNOT', 'OP_SWITCH', 'OP_BOOLNOT', 'OP_PUSHTRAP', 'OP_POPTRAP', 'OP_RAISE', 'OP_CHECK_SIGNALS', 'OP_C_CALL1', 'OP_C_CALL2', 'OP_C_CALL3', 'OP_C_CALL4', 'OP_C_CALL5', 'OP_C_CALLN', 'OP_CONST0', 'OP_CONST1', 'OP_CONST2', 'OP_CONST3', 'OP_CONSTINT', 'OP_PUSHCONST0', 'OP_PUSHCONST1', 'OP_PUSHCONST2', 'OP_PUSHCONST3', 'OP_PUSHCONSTINT', 'OP_NEGINT', 'OP_ADDINT', 'OP_SUBINT', 'OP_MULINT', 'OP_DIVINT', 'OP_MODINT', 'OP_ANDINT', 'OP_ORINT', 'OP_XORINT', 'OP_LSLINT', 'OP_LSRINT', 'OP_ASRINT', 'OP_EQ', 'OP_NEQ', 'OP_LTINT', 'OP_LEINT', 'OP_GTINT', 'OP_GEINT', 'OP_OFFSETINT', 'OP_OFFSETREF', 'OP_ISINT', 'OP_GETMETHOD', 'OP_BEQ', 'OP_BNEQ', 'OP_BLTINT', 'OP_BLEINT', 'OP_BGTINT', 'OP_BGEINT', 'OP_ULTINT', 'OP_UGEINT', 'OP_BULTINT', 'OP_BUGEINT', 'OP_GETPUBMET', 'OP_GETDYNMET', 'OP_STOP', 'OP_EVENT', 'OP_BREAK', 'OP_RERAISE', 'OP_RAISE_NOTRACE', 'OP_GETSTRINGCHAR' ]

for _i, _opcode in enumerate(opcode_list):
    globals()[_opcode] = _i

if os.environ.get('DEBUG'):
    def dbg(f):
        print(*f())
else:
    def dbg(f):
        pass

class Prims:
    def __init__(self, names):
        self.names = names

    def call(self, index, *args):
        name = self.names[index]
        dbg(lambda: ('ccall', name, args))
        return getattr(self, name)(*args)

    def caml_register_named_value(self, vname, val):
        # print('named:', vname, val)
        return ATOMS[0]

    def caml_fresh_oo_id(self, _):
        return make_int(666)

    def caml_int64_float_of_bits(self, _):
        return make_float(0.666) # TODO

    def caml_ml_open_descriptor_in(self, _):
        return '_stdin' # TODO

    def caml_ml_open_descriptor_out(self, _):
        return '_stdout' # TODO

    def caml_ml_out_channels_list(self, _):
        return make_int(0) # TODO

    def caml_ml_output_char(self, channel, ch):
        # print('out', channel, chr(ch))
        sys.stdout.write(chr(to_int(ch)))
        return make_int(0)

    def caml_ml_flush(self, channel):
        sys.stdout.flush()

    def caml_create_bytes(self, length):
        return bytearray(to_int(length))

    def caml_sys_get_argv(self, _):
        return make_array(["ocamlpypy", make_array(['ocamlpypy'] + [
            make_string(arg) for arg in sys.argv[2:]
        ])])

    def caml_sys_getenv(self, name):
        return make_string(os.environ.get(to_str(name), ''))

    def caml_sys_get_config(self, _):
        return make_array([
            'pypy',
            make_int(64), # bits
            make_int(0) # little endian
        ])

    def caml_sys_const_backend_type(self, _):
        return make_int(1) # bytecode

    def caml_sys_const_big_endian(self, _):
        return make_int(0)

    def caml_sys_const_word_size(self, _):
        return make_int(64)

    def caml_sys_const_int_size(self, _):
        return make_int(64) # make_int(63) ??

    def caml_sys_const_ostype_unix(self, _):
        return make_int(1)

    def caml_sys_const_ostype_win32(self, _):
        return make_int(0)

    def caml_sys_const_ostype_cygwin(self, _):
        return make_int(0)

    def caml_sys_const_max_wosize(self, _):
        return make_int(2**20)

    def caml_ml_string_length(self, s):
        return make_int(len(s))

    def caml_ml_output(self, stream, data, ofs, length):
        data = data[to_int(ofs) : to_int(ofs) + to_int(length)]
        sys.stdout.write(data)

    def caml_format_int(self, fmt, n):
        #print('fmt', fmt)
        return make_string(fmt % (to_int(n)))

    def caml_nativeint_shift_left(self, a, b):
        assert isinstance(a, Int64), a
        return Int64((a.i << to_int(b)) & 0xFFFFFFFF)

    def caml_nativeint_to_int(self, n):
        assert isinstance(n, Int64), n
        #print('caml_nativeint_to_int', n)
        return make_int(n.i)

    def caml_nativeint_sub(self, a, b):
        assert isinstance(a, Int64), a
        assert isinstance(b, Int64), b
        return Int64(a.i - b.i)

    def caml_make_vect(self, size, init):
        return make_array([ init for i in range(size) ])

    def caml_obj_block(self, tag, size):
        b = make_block(tag, size)
        for i in range(size): b.set_field(i, make_int(0))
        return b

    def caml_obj_dup(self, o):
        b = make_block(tag=o._tag, size=len(o._fields))
        for i in range(len(o._fields)): b.set_field(i, b.field(i))
        return b

    def caml_ensure_stack_capacity(self, space):
        pass

    def caml_fill_bytes(self, s, offset, len, init):
        #print(offset, len, init)
        for i in range(offset, offset + len):
            s[i] = init

    def caml_string_notequal(self, a, b):
        assert type(a) == type(b)
        return a != b

    def caml_int_of_string(self, n):
        return make_int(int(to_str(n)))

    def caml_string_equal(self, a, b):
        assert type(a) == type(b)
        return a == b

    def caml_neg_float(self, a):
        return make_float(-to_float(a))

    def caml_div_float(self, a, b):
        return make_float(to_float(a) / to_float(b))

    def caml_mul_float(self, a, b):
        return make_float(to_float(a) * to_float(b))

    def caml_int_of_float(self, n):
        return make_int(int(n))

    def caml_float_of_int(self, n):
        return float(to_int(n))

    def caml_array_sub(self, a, ofs, len):
        return make_array(a._fields[ofs : ofs+len])

    def caml_make_array(self, init):
        return init

    def caml_hash(self, count, limit, seed, obj):
        return make_int(hash(obj)) # TODO

    def caml_array_get_addr(self, array, index):
        return array.field(index)

    def caml_array_set_addr(self, array, index, val):
        array.set_field(index, val)

    def caml_array_get(self, array, index):
        return array.field(index)

    def caml_array_set(self, array, index, val):
        array.set_field(index, val)

    def caml_weak_create(self, len):
        return '__weak' # TODO

    def caml_greaterequal(self, a, b):
        return a >= b # TODO

    def caml_equal(self, a, b):
        return a == b # TODO

    def caml_eq_float(self, a, b):
        return to_float(a) == to_float(b)

    def caml_gc_full_major(self, _):
        pass

def set_code_val(block, pc):
    block.set_field(0, make_int(pc & 0xFFFFFFFF))

def code_val(block):
    return to_int(block.field(0)) & 0xFFFFFFFF

def to_pc(x):
    return to_int(x) & 0xFFFFFFFF

def offset_field(v, n):
    dbg(lambda: ('offset_field', v._envoffsettop, n,'+', v._envoffsetdelta))
    f = n + v._envoffsetdelta
    if f == 0:
        return v._envoffsettop
    else:
        return v._envoffsettop.field(f)

def eval_bc(prims, global_data, bc, stack):
    accu = 0
    extra_args = 0
    env = 'rootenv'
    pc = 0
    trap_sp = -1

    def unsupp():
        raise Exception('unsupported instr %d = %s' % (instr, opcode_list[instr]))

    def push(v):
        Root.check(v)
        stack.append(v)

    def sp(k):
        return stack[len(stack) - 1 - k]

    def sp_set(k, v):
        stack[len(stack) - 1 - k] = v

    def pop():
        return stack.pop()

    def c_call(n, *args):
        return prims.call(n, *args)

    def _set_code_val(b, pc):
        assert pc >= 0 and pc < len(bc)
        set_code_val(b, pc)

    while True:
        instr = bc[pc]
        dbg(lambda: (colorama.Fore.RED + 'pc', pc, 'instr', opcode_list[instr], colorama.Style.RESET_ALL + 'accu', repr(accu)[:6000], 'stack', '(' + repr(stack)[-100:] + ')', '__env', repr(env)[:100]))
        #print(colorama.Fore.RED + 'pc', pc, 'instr', opcode_list[instr], colorama.Style.RESET_ALL)
        pc += 1

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
            push(env)
            push(pc + bc[pc])
            pc += 1
        elif instr == OP_APPLY:
            extra_args = bc[pc]-1
            trace_call(accu, None)
            pc = code_val(accu)
            env = accu
        elif instr == OP_APPLY1:
            arg1 = pop()
            push(make_int(extra_args))
            push(env)
            push(make_int(pc))
            push(arg1)
            trace_call(accu, [arg1])
            pc = code_val(accu)
            env = accu
            extra_args = 0
        elif instr == OP_APPLY2:
            arg1 = pop()
            arg2 = pop()
            trace_call(accu, [arg1, arg2])
            push(make_int(extra_args))
            push(env)
            push(make_int(pc))
            push(arg2)
            push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args = 1
        elif instr == OP_APPLY3:
            arg1 = pop()
            arg2 = pop()
            arg3 = pop()
            trace_call(accu, [arg1, arg2, arg3])
            push(make_int(extra_args))
            push(env)
            push(make_int(pc))
            push(arg3)
            push(arg2)
            push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args = 2
        elif instr == OP_APPTERM:
            nargs = bc[pc]
            pc += 1
            slotsize = bc[pc]
            newsp = slotsize - nargs

            for i in range(nargs): dbg(lambda: ('arg', sp(i)))

            def set_sp(target, src):
                stack[len(stack) - 1 - target] = sp(src)

            i = nargs - 1
            while i >= 0:
                set_sp(newsp + i, i)
                i -= 1
            for _ in range(newsp): pop()
            trace_call(accu, None)
            pc = code_val(accu)
            env = accu
            extra_args += nargs - 1
        elif instr == OP_APPTERM1:
            arg1 = sp(0)
            trace_call(accu, [arg1])
            for _ in range(bc[pc]): pop()
            push(arg1)
            pc = code_val(accu)
            env = accu
        elif instr == OP_APPTERM2:
            arg1 = sp(0)
            arg2 = sp(1)
            trace_call(accu, [arg1, arg2])
            for _ in range(bc[pc]): pop()
            push(arg2)
            push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args += 1
        elif instr == OP_APPTERM3:
            arg1 = sp(0)
            arg2 = sp(1)
            arg3 = sp(2)
            trace_call(accu, [arg1, arg2, arg3])
            for _ in range(bc[pc]): pop()
            push(arg3)
            push(arg2)
            push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args += 2
        elif instr == OP_RETURN:
            npop = bc[pc]
            pc += 1
            for _ in range(npop): pop()

            if extra_args > 0:
                extra_args -= 1
                pc = code_val(accu)
                env = accu
            else:
                pc = to_pc(pop())
                env = pop()
                extra_args = to_int(pop())
        elif instr == OP_RESTART:
            num_args = len(env._fields) - 2
            assert num_args >= 0, env
            for i in range(num_args):
                push(env.field((num_args - i - 1) + 2))
            env = env.field(1)
            extra_args += num_args
        elif instr == OP_GRAB:
            required = bc[pc]
            pc += 1
            if extra_args >= required:
                extra_args -= required
            else:
                num_args = 1 + extra_args
                # print(stack, num_args)
                accu = make_block(num_args + 2, Closure_tag)
                accu.set_field(1, env)
                for i in range(num_args):
                    accu.set_field(i + 2, pop())
                set_code_val(accu, pc - 3)
                pc = to_pc(pop())
                env = pop()
                extra_args = to_int(pop())
        elif instr == OP_CLOSURE:
            nvars = bc[pc]
            pc += 1

            if nvars > 0:
                push(accu)

            accu = make_block(1 + nvars, Closure_tag)
            dbg(lambda: ('closure', accu, nvars, pc + bc[pc]))
            for i in range(nvars):
                dbg(lambda: ('closure var', sp(0)))
                accu.set_field(i + 1, sp(0))
                pop()

            _set_code_val(accu, pc + bc[pc])
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
                accu.set_field(nfuncs * 2 - 1 + i, sp(0))
                pop()

            dbg(lambda: ('init', pc + bc[pc]))
            _set_code_val(accu, pc + bc[pc])
            push(accu)
            accu._envoffsettop = accu
            accu._envoffsetdelta = 0
            for i in range(1, nfuncs):
                b = make_block(1, Infix_tag)
                b._envoffsettop = accu
                b._envoffsetdelta = i * 2
                b.set_field(0, make_int(pc + bc[pc + i]))
                push(b)
                accu.set_field(i * 2, b)
                accu.set_field(i * 2 - 1, 'closureoffsettaint')
            pc += nfuncs

        elif instr == OP_OFFSETCLOSUREM2:
            unsupp()
        elif instr == OP_OFFSETCLOSURE0:
            accu = env
        elif instr == OP_OFFSETCLOSURE2:
            accu = offset_field(env, 2) # offset_field
        elif instr == OP_OFFSETCLOSURE:
            n = bc[pc]
            pc += 1
            accu = offset_field(env, n) # offset_field
        elif instr == OP_PUSHOFFSETCLOSUREM2:
            unsupp()
        elif instr == OP_PUSHOFFSETCLOSURE0:
            push(accu)
            accu = env
        elif instr == OP_PUSHOFFSETCLOSURE2:
            push(accu)
            accu = offset_field(env, 2) # offset_field
        elif instr == OP_PUSHOFFSETCLOSURE:
            push(accu)
            n = bc[pc]
            pc += 1
            accu = offset_field(env, n) # offset_field
        elif instr == OP_GETGLOBAL:
            n = bc[pc]
            pc += 1
            accu = global_data[n]
        elif instr == OP_PUSHGETGLOBAL:
            push(accu)
            n = bc[pc]
            pc += 1
            accu = global_data[n]
            # print(n, global_data[n - 2 : n + 3])
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
            n = bc[pc]
            pc += 1
            #dbg(lambda: ('__ field', n, accu.field(n)))
            accu = accu.field(n)
        elif instr == OP_SETGLOBAL:
            n = bc[pc]
            pc += 1
            global_data[n] = accu
            dbg(lambda: ('global', n, accu))
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
            b.set_field(1, pop())
            accu = b
        elif instr == OP_MAKEBLOCK3:
            tag = bc[pc]
            pc += 1
            b = make_block(3, tag)
            b.set_field(0, accu)
            b.set_field(1, pop())
            b.set_field(2, pop())
            accu = b
        elif instr == OP_MAKEFLOATBLOCK:
            n = bc[pc]
            pc += 1
            b = make_block(tag=0, size=pc)
            b.set_field(0, accu)
            for i in range(1, n):
                b.set_field(i, pop())
            accu = b
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
            n = bc[pc]
            pc += 1
            accu.set_field(n, pop())
            accu = Val_unit
        elif instr == OP_VECTLENGTH:
            accu = len(accu._fields)
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
            dbg(lambda: (accu, is_true(accu)))
            if not is_true(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_SWITCH:
            sizes = bc[pc]
            pc += 1
            dbg(lambda: ('switch', accu))
            if is_block(accu):
                index = block_tag(accu)
                assert index < (sizes >> 16)
                dbg(lambda: ('switch_block', sizes & 0xFFFF, index))
                pc += bc[pc + (sizes & 0xFFFF) + index]
            else:
                index = to_int(accu)
                assert index < (sizes & 0xFFFF)
                pc += bc[pc + index]
            dbg(lambda: ('switch_pc', pc))
        elif instr == OP_BOOLNOT:
            accu = make_int(1 - to_int(accu))
        elif instr == OP_PUSHTRAP:
            n = bc[pc]
            pc += 1

            push(make_int(extra_args))
            push(env)
            push(make_int(trap_sp))
            push(make_int(pc - 1 + n))
            trap_sp = len(stack)
        elif instr == OP_POPTRAP:
            trap_sp = sp(1)
            assert trap_sp <= len(stack)
            for _ in range(4): pop()
        elif instr == OP_RAISE:
            if trap_sp == -1:
                raise Exception('terminated with exception %s' % accu)

            assert trap_sp <= len(stack), (trap_sp, len(stack))
            while len(stack) > trap_sp:
                stack.pop()

            pc = to_int(pop())
            trap_sp = to_int(pop())
            env = pop()
            extra_args = to_int(pop())
        elif instr == OP_CHECK_SIGNALS:
            pass
        elif instr == OP_C_CALL1:
            dbg(lambda: ('stack', stack))
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
            accu = make_int(to_int(accu) << to_int(pop()))
        elif instr == OP_LSRINT:
            accu = make_int(to_uint(accu) >> to_int(pop())) # TODO: logical shift
        elif instr == OP_ASRINT:
            accu = make_int(to_int(accu) >> to_int(pop())) # TODO: artmetic shift
        elif instr == OP_EQ:
            accu = make_int(pop() == accu)
        elif instr == OP_NEQ:
            accu = make_int(pop() != accu)
        elif instr == OP_LTINT:
            accu = make_int(accu < pop())
        elif instr == OP_LEINT:
            accu = make_int(accu <= pop())
        elif instr == OP_GTINT:
            accu = make_int(accu > pop())
        elif instr == OP_GEINT:
            accu = make_int(accu >= pop())
        elif instr == OP_OFFSETINT:
            accu = make_int(to_int(accu) + bc[pc])
            pc += 1
        elif instr == OP_OFFSETREF:
            accu.set_field(0, make_int(to_int(accu.field(0)) + bc[pc]))
            pc += 1
            accu = Val_unit
        elif instr == OP_ISINT:
            accu = make_int(1 if is_int(accu) else 0)
        elif instr == OP_GETMETHOD:
            unsupp()
        elif instr == OP_BEQ:
            n = bc[pc]
            pc += 1
            if n == to_int(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_BNEQ:
            n = bc[pc]
            pc += 1
            if n != to_int(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_BLTINT:
            n = bc[pc]
            pc += 1
            if n < to_int(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_BLEINT:
            n = bc[pc]
            pc += 1
            if n <= to_int(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_BGTINT:
            n = bc[pc]
            pc += 1
            if n > to_int(accu):
                pc += bc[pc]
            else:
                pc += 1
        elif instr == OP_BGEINT:
            n = bc[pc]
            pc += 1
            if n >= to_int(accu):
                pc += bc[pc]
            else:
                pc += 1
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

def entry_point(argv):
    exe_dict = parse_executable(open(argv[1], 'rb').read())
    bytecode = array.array('i', exe_dict['CODE'])
    prims = Prims(exe_dict['PRIM'].decode().split('\0'))
    global_data = unmarshal(io.BytesIO(exe_dict['DATA']))._fields

    stack = []
    eval_bc(prims=prims, global_data=global_data, bc=bytecode, stack=stack)

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    entry_point(sys.argv)
