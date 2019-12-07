#from __future__ import print_function
import struct, sys, array, StringIO, os
import colorama
from ocaml_values import *
from ocaml_marshal import unmarshal, parse_executable

def trace_call(env, args):
    if dbg:
        dbg('call', code_val(env), args)

opcode_list = [ 'OP_ACC0', 'OP_ACC1', 'OP_ACC2', 'OP_ACC3', 'OP_ACC4', 'OP_ACC5', 'OP_ACC6', 'OP_ACC7', 'OP_ACC', 'OP_PUSH', 'OP_PUSHACC0', 'OP_PUSHACC1', 'OP_PUSHACC2', 'OP_PUSHACC3', 'OP_PUSHACC4', 'OP_PUSHACC5', 'OP_PUSHACC6', 'OP_PUSHACC7', 'OP_PUSHACC', 'OP_POP', 'OP_ASSIGN', 'OP_ENVACC1', 'OP_ENVACC2', 'OP_ENVACC3', 'OP_ENVACC4', 'OP_ENVACC', 'OP_PUSHENVACC1', 'OP_PUSHENVACC2', 'OP_PUSHENVACC3', 'OP_PUSHENVACC4', 'OP_PUSHENVACC', 'OP_PUSH_RETADDR', 'OP_APPLY', 'OP_APPLY1', 'OP_APPLY2', 'OP_APPLY3', 'OP_APPTERM', 'OP_APPTERM1', 'OP_APPTERM2', 'OP_APPTERM3', 'OP_RETURN', 'OP_RESTART', 'OP_GRAB', 'OP_CLOSURE', 'OP_CLOSUREREC', 'OP_OFFSETCLOSUREM2', 'OP_OFFSETCLOSURE0', 'OP_OFFSETCLOSURE2', 'OP_OFFSETCLOSURE', 'OP_PUSHOFFSETCLOSUREM2', 'OP_PUSHOFFSETCLOSURE0', 'OP_PUSHOFFSETCLOSURE2', 'OP_PUSHOFFSETCLOSURE', 'OP_GETGLOBAL', 'OP_PUSHGETGLOBAL', 'OP_GETGLOBALFIELD', 'OP_PUSHGETGLOBALFIELD', 'OP_SETGLOBAL', 'OP_ATOM0', 'OP_ATOM', 'OP_PUSHATOM0', 'OP_PUSHATOM', 'OP_MAKEBLOCK', 'OP_MAKEBLOCK1', 'OP_MAKEBLOCK2', 'OP_MAKEBLOCK3', 'OP_MAKEFLOATBLOCK', 'OP_GETFIELD0', 'OP_GETFIELD1', 'OP_GETFIELD2', 'OP_GETFIELD3', 'OP_GETFIELD', 'OP_GETFLOATFIELD', 'OP_SETFIELD0', 'OP_SETFIELD1', 'OP_SETFIELD2', 'OP_SETFIELD3', 'OP_SETFIELD', 'OP_SETFLOATFIELD', 'OP_VECTLENGTH', 'OP_GETVECTITEM', 'OP_SETVECTITEM', 'OP_GETBYTESCHAR', 'OP_SETBYTESCHAR', 'OP_BRANCH', 'OP_BRANCHIF', 'OP_BRANCHIFNOT', 'OP_SWITCH', 'OP_BOOLNOT', 'OP_PUSHTRAP', 'OP_POPTRAP', 'OP_RAISE', 'OP_CHECK_SIGNALS', 'OP_C_CALL1', 'OP_C_CALL2', 'OP_C_CALL3', 'OP_C_CALL4', 'OP_C_CALL5', 'OP_C_CALLN', 'OP_CONST0', 'OP_CONST1', 'OP_CONST2', 'OP_CONST3', 'OP_CONSTINT', 'OP_PUSHCONST0', 'OP_PUSHCONST1', 'OP_PUSHCONST2', 'OP_PUSHCONST3', 'OP_PUSHCONSTINT', 'OP_NEGINT', 'OP_ADDINT', 'OP_SUBINT', 'OP_MULINT', 'OP_DIVINT', 'OP_MODINT', 'OP_ANDINT', 'OP_ORINT', 'OP_XORINT', 'OP_LSLINT', 'OP_LSRINT', 'OP_ASRINT', 'OP_EQ', 'OP_NEQ', 'OP_LTINT', 'OP_LEINT', 'OP_GTINT', 'OP_GEINT', 'OP_OFFSETINT', 'OP_OFFSETREF', 'OP_ISINT', 'OP_GETMETHOD', 'OP_BEQ', 'OP_BNEQ', 'OP_BLTINT', 'OP_BLEINT', 'OP_BGTINT', 'OP_BGEINT', 'OP_ULTINT', 'OP_UGEINT', 'OP_BULTINT', 'OP_BUGEINT', 'OP_GETPUBMET', 'OP_GETDYNMET', 'OP_STOP', 'OP_EVENT', 'OP_BREAK', 'OP_RERAISE', 'OP_RAISE_NOTRACE', 'OP_GETSTRINGCHAR' ]

for _i, _opcode in enumerate(opcode_list):
    globals()[_opcode] = _i

if os.environ.get('DEBUG'):
    def dbg(*f):
        print(' '.join(map(str, f)))
else:
    dbg = None

class Prims:
    def __init__(self, names, argv):
        self.names = names
        self.argv = argv

    for i in range(1, 6):
        exec '''
def call%d(self, index, *args):
    # TODO: avoid dict lookup
    name = self.names[index]
    if dbg:
        dbg('ccall', name, args)
    if self.funcs%d:
       res = self.funcs%d[name](self, *args)
    else:
       raise Exception("no functions of this arity")
    Root.check(res)
    return res''' % (i, i, i)

    def caml_register_named_value(self, vname, val):
        # print('named:', vname, val)
        return ATOMS[0]

    def caml_fresh_oo_id(self, _):
        return make_int(666)

    def caml_int64_float_of_bits(self, _):
        return make_float(0.666) # TODO

    def caml_ml_open_descriptor_in(self, _):
        return String('_stdin')

    def caml_ml_open_descriptor_out(self, _):
        return String('_stdout')

    def caml_ml_out_channels_list(self, _):
        return make_int(0) # TODO

    def caml_ml_output_char(self, channel, ch):
        # print('out', channel, chr(ch))
        # TODO: buffering
        os.write(1, chr(to_int(ch)))
        return make_int(0)

    def caml_ml_flush(self, channel):
        return make_int(0)

    def caml_create_bytes(self, length):
        # return make_bytes(bytearray(to_int(length)))
        return make_string('\0' * to_int(length))

    def caml_sys_get_argv(self, _):
        return make_array([make_string("ocamlpypy"), make_array([make_string('ocamlpypy')] + [
            make_string(arg) for arg in self.argv
        ])])

    def caml_sys_getenv(self, name):
        return make_string(os.environ.get(to_str(name)) or '')

    def caml_sys_get_config(self, _):
        return make_array([
            make_string('pypy'),
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
        return make_int(len(to_str(s)))

    def caml_ml_output(self, stream, data, ofs_, length_):
        ofs = to_int(ofs_)
        len = to_int(length_)
        assert ofs >= 0
        assert len >= 0
        data = to_str(data)[ofs : ofs + len]
        os.write(1, data)
        return make_int(0)

    def caml_format_int(self, fmt, n_):
        fmt_s = to_str(fmt)
        n = to_int(n_)
        if fmt_s == '%d':
            return make_string('%d' % n)
        else:
            raise Exception('unknown format %s' % fmt_s)

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
        return make_array([ init for i in range(to_int(size)) ])

    def caml_obj_block(self, tag, size):
        b = make_block(to_int(tag), to_int(size))
        for i in range(to_int(size)): b.set_field(i, make_int(0))
        return b

    def caml_obj_dup(self, o):
        b = make_block(tag=o._tag, size=len(o._fields))
        for i in range(len(o._fields)): b.set_field(i, b.field(i))
        return b

    def caml_ensure_stack_capacity(self, space):
        return Val_unit

    def caml_fill_bytes(self, s, offset_, len_, init_):
        #offset = to_int(offset_)
        #len = to_int(offset_)
        #init = to_int(init_)
        #assert offset >= 0
        #assert len >= 0
        #assert isinstance(s, Bytes)
        #for i in range(offset, offset + len):
        #    s.s[i] = init
        #return Val_unit
        raise Exception('unsupp')

    def caml_string_equal(self, a, b):
        if isinstance(a, String):
            assert isinstance(b, String)
        else:
            assert isinstance(a, Bytes)
            assert isinstance(b, Bytes)
        return make_bool(a == b)

    def caml_int_of_string(self, n):
        return make_int(int(to_str(n)))

    def caml_string_equal(self, a, b):
        return not self.caml_string_equal(a, b)

    def caml_neg_float(self, a):
        return make_float(-to_float(a))

    def caml_div_float(self, a, b):
        return make_float(to_float(a) / to_float(b))

    def caml_mul_float(self, a, b):
        return make_float(to_float(a) * to_float(b))

    def caml_int_of_float(self, n):
        return make_int(int(to_float(n)))

    def caml_float_of_int(self, n):
        return make_float(float(to_int(n)))

    def caml_array_sub(self, a, ofs_, len_):
        ofs = to_int(ofs_)
        len = to_int(len_)
        assert ofs >= 0
        assert len >= 0
        return make_array(a._fields[ofs : ofs+len])

    def caml_make_array(self, init):
        return init

    def caml_hash(self, count, limit, seed, obj):
        return make_int(obj.hash()) # TODO

    def caml_array_get_addr(self, array, index):
        return array.field(to_int(index))

    def caml_array_set_addr(self, array, index, val):
        array.set_field(to_int(index), val)

    def caml_array_get(self, array, index):
        return array.field(to_int(index))

    def caml_array_set(self, array, index, val):
        array.set_field(to_int(index), val)

    def caml_weak_create(self, len):
        return make_string('__weak') # TODO

    def caml_greaterequal(self, a, b):
        #return make_bool(a >= b) # TODO
        raise Exception('unsupp')

    def caml_equal(self, a, b):
        #return make_bool(a == b) # TODO
        raise Exception('unsupp')

    def caml_eq_float(self, a, b):
        return make_bool(to_float(a) == to_float(b))

    def caml_gc_full_major(self, _):
        return Val_unit

    funcs1 = {}
    funcs2 = {}
    funcs3 = {}
    funcs4 = {}
    funcs5 = {}
    for _k, _v in locals().items():
        if _k.startswith('caml_'):
            _cnt = _v.func_code.co_argcount-1
            locals()['funcs%d' % _cnt][_k] = _v

def set_code_val(block, pc):
    block.set_field(0, make_int(pc & 0xFFFFFFFF))

def code_val(block):
    return to_int(block.field(0)) & 0xFFFFFFFF

def to_pc(x):
    return to_int(x) & 0xFFFFFFFF

def offset_field(v, n):
    f = n + v._envoffsetdelta
    if f == 0:
        return v._envoffsettop
    else:
        return v._envoffsettop.field(f)

from rpython.rlib.objectmodel import always_inline

class Stack:
    def __init__(self):
        self._arr = []

    def push(self, v):
        Root.check(v)
        self._arr.append(v)

    def pop(self):
        return self._arr.pop()

    def sp_swap(self, target, src):
        self._arr[len(self._arr) - 1 - target] = self.sp(src)

    def sp_set(self, k, val):
        self._arr[len(self._arr) - 1 - k] = val

    def sp(self, k):
        return self._arr[len(self._arr) - 1 - k]

    def len(self):
        return len(self._arr)

from rpython.rlib.jit import JitDriver
jitdriver = JitDriver(
    greens=['pc', 'trap_sp', 'extra_args', 'bc'],
    reds=['stack', 'accu', 'env', 'global_data', 'prims'])

def eval_bc(prims, global_data, bc):
    accu = make_int(0)
    extra_args = 0
    env = make_string('rootenv')
    pc = 0
    trap_sp = -1

    def unsupp():
        raise Exception('unsupported instr')# %d = %s' % (instr, opcode_list[instr]))

    stack = Stack()

    while True:
        jitdriver.jit_merge_point(
            pc=pc, bc=bc, trap_sp=trap_sp, extra_args=extra_args, prims=prims,
            stack=stack, accu=accu, env=env, global_data=global_data)
        instr = bc[pc]
        #if dbg: dbg(colorama.Fore.RED + 'pc', pc, 'instr', opcode_list[instr], colorama.Style.RESET_ALL + 'accu', repr(accu)[:6000])
        #print 'pc', pc, 'instr', opcode_list[instr], 'accu', accu
        pc += 1

        assert isinstance(trap_sp, int)
        Root.check(accu)

        if instr == OP_ACC0:
            accu = stack.sp(0)
        elif instr == OP_ACC1:
            accu = stack.sp(1)
        elif instr == OP_ACC2:
            accu = stack.sp(2)
        elif instr == OP_ACC3:
            accu = stack.sp(3)
        elif instr == OP_ACC4:
            accu = stack.sp(4)
        elif instr == OP_ACC5:
            accu = stack.sp(5)
        elif instr == OP_ACC6:
            accu = stack.sp(6)
        elif instr == OP_ACC7:
            accu = stack.sp(7)
        elif instr == OP_ACC:
            accu = stack.sp(bc[pc])
            pc += 1
        elif instr == OP_PUSH:
            stack.push(accu)
        elif instr == OP_PUSHACC0:
            stack.push(accu)
        elif instr == OP_PUSHACC1:
            stack.push(accu)
            accu = stack.sp(1)
        elif instr == OP_PUSHACC2:
            stack.push(accu)
            accu = stack.sp(2)
        elif instr == OP_PUSHACC3:
            stack.push(accu)
            accu = stack.sp(3)
        elif instr == OP_PUSHACC4:
            stack.push(accu)
            accu = stack.sp(4)
        elif instr == OP_PUSHACC5:
            stack.push(accu)
            accu = stack.sp(5)
        elif instr == OP_PUSHACC6:
            stack.push(accu)
            accu = stack.sp(6)
        elif instr == OP_PUSHACC7:
            stack.push(accu)
            accu = stack.sp(7)
        elif instr == OP_PUSHACC:
            stack.push(accu)
            accu = stack.sp(bc[pc])
            pc += 1
        elif instr == OP_POP:
            for i in range(bc[pc]):
                stack.pop()
            pc += 1
        elif instr == OP_ASSIGN:
            stack.sp_set(bc[pc], accu)
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
            stack.push(accu)
            accu = env.field(1)
        elif instr == OP_PUSHENVACC2:
            stack.push(accu)
            accu = env.field(2)
        elif instr == OP_PUSHENVACC3:
            stack.push(accu)
            accu = env.field(3)
        elif instr == OP_PUSHENVACC4:
            stack.push(accu)
            accu = env.field(4)
        elif instr == OP_PUSHENVACC:
            stack.push(accu)
            accu = env.field(bc[pc])
            pc += 1
        elif instr == OP_PUSH_RETADDR:
            stack.push(make_int(extra_args))
            stack.push(env)
            stack.push(make_int(pc + bc[pc]))
            pc += 1
        elif instr == OP_APPLY:
            extra_args = bc[pc]-1
            trace_call(accu, None)
            pc = code_val(accu)
            env = accu
        elif instr == OP_APPLY1:
            arg1 = stack.pop()
            stack.push(make_int(extra_args))
            stack.push(env)
            stack.push(make_int(pc))
            stack.push(arg1)
            trace_call(accu, [arg1])
            pc = code_val(accu)
            env = accu
            extra_args = 0
        elif instr == OP_APPLY2:
            arg1 = stack.pop()
            arg2 = stack.pop()
            trace_call(accu, [arg1, arg2])
            stack.push(make_int(extra_args))
            stack.push(env)
            stack.push(make_int(pc))
            stack.push(arg2)
            stack.push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args = 1
        elif instr == OP_APPLY3:
            arg1 = stack.pop()
            arg2 = stack.pop()
            arg3 = stack.pop()
            trace_call(accu, [arg1, arg2, arg3])
            stack.push(make_int(extra_args))
            stack.push(env)
            stack.push(make_int(pc))
            stack.push(arg3)
            stack.push(arg2)
            stack.push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args = 2
        elif instr == OP_APPTERM:
            nargs = bc[pc]
            pc += 1
            slotsize = bc[pc]
            newsp = slotsize - nargs

            if dbg:
                for i in range(nargs): dbg('arg', stack.sp(i))

            i = nargs - 1
            while i >= 0:
                stack.sp_swap(newsp + i, i)
                i -= 1
            for _ in range(newsp): stack.pop()
            trace_call(accu, None)
            pc = code_val(accu)
            env = accu
            extra_args += nargs - 1
        elif instr == OP_APPTERM1:
            arg1 = stack.sp(0)
            trace_call(accu, [arg1])
            for _ in range(bc[pc]): stack.pop()
            stack.push(arg1)
            pc = code_val(accu)
            env = accu
        elif instr == OP_APPTERM2:
            arg1 = stack.sp(0)
            arg2 = stack.sp(1)
            trace_call(accu, [arg1, arg2])
            for _ in range(bc[pc]): stack.pop()
            stack.push(arg2)
            stack.push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args += 1
        elif instr == OP_APPTERM3:
            arg1 = stack.sp(0)
            arg2 = stack.sp(1)
            arg3 = stack.sp(2)
            trace_call(accu, [arg1, arg2, arg3])
            for _ in range(bc[pc]): stack.pop()
            stack.push(arg3)
            stack.push(arg2)
            stack.push(arg1)
            pc = code_val(accu)
            env = accu
            extra_args += 2
        elif instr == OP_RETURN:
            npop = bc[pc]
            pc += 1
            for _ in range(npop): stack.pop()

            if extra_args > 0:
                extra_args -= 1
                pc = code_val(accu)
                env = accu
            else:
                pc = to_pc(stack.pop())
                env = stack.pop()
                extra_args = to_int(stack.pop())
        elif instr == OP_RESTART:
            num_args = len(env._fields) - 2
            assert num_args >= 0, env
            for i in range(num_args):
                stack.push(env.field((num_args - i - 1) + 2))
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
                    accu.set_field(i + 2, stack.pop())
                set_code_val(accu, pc - 3)
                pc = to_pc(stack.pop())
                env = stack.pop()
                extra_args = to_int(stack.pop())
        elif instr == OP_CLOSURE:
            nvars = bc[pc]
            pc += 1

            if nvars > 0:
                stack.push(accu)

            accu = make_block(1 + nvars, Closure_tag)
            for i in range(nvars):
                accu.set_field(i + 1, stack.sp(0))
                stack.pop()

            set_code_val(accu, pc + bc[pc])
            pc += 1
        elif instr == OP_CLOSUREREC:
            nfuncs = bc[pc]
            pc += 1
            nvars = bc[pc]
            pc += 1

            blksize = nfuncs * 2 - 1 + nvars
            if nvars > 0:
                stack.push(accu)

            accu = make_block(blksize, Closure_tag)
            for i in range(nvars):
                accu.set_field(nfuncs * 2 - 1 + i, stack.sp(0))
                stack.pop()

            set_code_val(accu, pc + bc[pc])
            stack.push(accu)
            accu._envoffsettop = accu
            accu._envoffsetdelta = 0
            for i in range(1, nfuncs):
                b = make_block(1, Infix_tag)
                b._envoffsettop = accu
                b._envoffsetdelta = i * 2
                b.set_field(0, make_int(pc + bc[pc + i]))
                stack.push(b)
                accu.set_field(i * 2, b)
                accu.set_field(i * 2 - 1, make_string('closureoffsettaint'))
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
            stack.push(accu)
            accu = env
        elif instr == OP_PUSHOFFSETCLOSURE2:
            stack.push(accu)
            accu = offset_field(env, 2) # offset_field
        elif instr == OP_PUSHOFFSETCLOSURE:
            stack.push(accu)
            n = bc[pc]
            pc += 1
            accu = offset_field(env, n) # offset_field
        elif instr == OP_GETGLOBAL:
            n = bc[pc]
            pc += 1
            accu = global_data[n]
        elif instr == OP_PUSHGETGLOBAL:
            stack.push(accu)
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
            stack.push(accu)
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
            accu = Val_unit
        elif instr == OP_ATOM0:
            accu = ATOMS[0]
        elif instr == OP_ATOM:
            n = bc[pc]
            pc += 1
            accu = ATOMS[n]
        elif instr == OP_PUSHATOM0:
            stack.push(accu)
            accu = ATOMS[0]
        elif instr == OP_PUSHATOM:
            stack.push(accu)
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
                b.set_field(i, stack.pop())
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
            b.set_field(1, stack.pop())
            accu = b
        elif instr == OP_MAKEBLOCK3:
            tag = bc[pc]
            pc += 1
            b = make_block(3, tag)
            b.set_field(0, accu)
            b.set_field(1, stack.pop())
            b.set_field(2, stack.pop())
            accu = b
        elif instr == OP_MAKEFLOATBLOCK:
            n = bc[pc]
            pc += 1
            b = make_block(tag=0, size=pc)
            b.set_field(0, accu)
            for i in range(1, n):
                b.set_field(i, stack.pop())
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
            unsupp()
        elif instr == OP_SETFIELD0:
            accu.set_field(0, stack.sp(0))
            stack.pop()
            accu = Val_unit
        elif instr == OP_SETFIELD1:
            accu.set_field(1, stack.sp(0))
            stack.pop()
            accu = Val_unit
        elif instr == OP_SETFIELD2:
            accu.set_field(2, stack.sp(0))
            stack.pop()
            accu = Val_unit
        elif instr == OP_SETFIELD3:
            accu.set_field(3, stack.sp(0))
            stack.pop()
            accu = Val_unit
        elif instr == OP_SETFIELD:
            n = bc[pc]
            pc += 1
            accu.set_field(n, stack.sp(0))
            stack.pop()
            accu = Val_unit
        elif instr == OP_SETFLOATFIELD:
            n = bc[pc]
            pc += 1
            accu.set_field(n, stack.pop())
            accu = Val_unit
        elif instr == OP_VECTLENGTH:
            accu = make_int(len(accu._fields))
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
                pc += bc[pc + (sizes & 0xFFFF) + index]
            else:
                index = to_int(accu)
                assert index < (sizes & 0xFFFF)
                pc += bc[pc + index]
        elif instr == OP_BOOLNOT:
            accu = make_int(1 - to_int(accu))
        elif instr == OP_PUSHTRAP:
            n = bc[pc]
            pc += 1

            stack.push(make_int(extra_args))
            stack.push(env)
            stack.push(make_int(trap_sp))
            stack.push(make_int(pc - 1 + n))
            trap_sp = stack.len()
        elif instr == OP_POPTRAP:
            trap_sp = to_int(stack.sp(1))
            assert trap_sp <= stack.len()
            for _ in range(4): stack.pop()
        elif instr == OP_RAISE:
            if trap_sp == -1:
                raise Exception('terminated with exception %s' % accu)

            assert trap_sp <= stack.len(), (trap_sp, stack.len())
            while stack.len() > trap_sp:
                stack.pop()

            pc = to_int(stack.pop())
            trap_sp = to_int(stack.pop())
            env = stack.pop()
            extra_args = to_int(stack.pop())
        elif instr == OP_CHECK_SIGNALS:
            pass
        elif instr == OP_C_CALL1:
            n = bc[pc]
            pc += 1
            accu = prims.call1(n, accu)
        elif instr == OP_C_CALL2:
            n = bc[pc]
            pc += 1
            accu = prims.call2(n, accu, stack.sp(0))
            stack.pop()
        elif instr == OP_C_CALL3:
            n = bc[pc]
            pc += 1
            accu = prims.call3(n, accu, stack.sp(0), stack.sp(1))
            stack.pop()
            stack.pop()
        elif instr == OP_C_CALL4:
            n = bc[pc]
            pc += 1
            accu = prims.call4(n, accu, stack.sp(0), stack.sp(1), stack.sp(2))
            stack.pop()
            stack.pop()
            stack.pop()
        elif instr == OP_C_CALL5:
            n = bc[pc]
            pc += 1
            accu = prims.call5(n, accu, stack.sp(0), stack.sp(1), stack.sp(2), stack.sp(3))
            stack.pop()
            stack.pop()
            stack.pop()
            stack.pop()
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
            stack.push(accu)
            accu = make_int(0)
        elif instr == OP_PUSHCONST1:
            stack.push(accu)
            accu = make_int(1)
        elif instr == OP_PUSHCONST2:
            stack.push(accu)
            accu = make_int(2)
        elif instr == OP_PUSHCONST3:
            stack.push(accu)
            accu = make_int(3)
        elif instr == OP_PUSHCONSTINT:
            stack.push(accu)
            accu = make_int(bc[pc])
            pc += 1
        elif instr == OP_NEGINT:
            accu = make_int(0 if is_true(accu) else 1)
        elif instr == OP_ADDINT:
            accu = make_int(to_int(accu) + to_int(stack.pop()))
        elif instr == OP_SUBINT:
            accu = make_int(to_int(accu) - to_int(stack.pop()))
        elif instr == OP_MULINT:
            accu = make_int(to_int(accu) * to_int(stack.pop()))
        elif instr == OP_DIVINT:
            accu = make_int(to_int(accu) / to_int(stack.pop()))
        elif instr == OP_MODINT:
            accu = make_int(to_int(accu) % to_int(stack.pop()))
        elif instr == OP_ANDINT:
            accu = make_int(to_int(accu) & to_int(stack.pop()))
        elif instr == OP_ORINT:
            accu = make_int(to_int(accu) | to_int(stack.pop()))
        elif instr == OP_XORINT:
            accu = make_int(to_int(accu) ^ to_int(stack.pop()))
        elif instr == OP_LSLINT:
            accu = make_int(to_int(accu) << to_int(stack.pop()))
        elif instr == OP_LSRINT:
            accu = make_int(to_uint(accu) >> to_int(stack.pop())) # TODO: logical shift
        elif instr == OP_ASRINT:
            accu = make_int(to_int(accu) >> to_int(stack.pop())) # TODO: arthmetic shift
        elif instr == OP_EQ:
            accu = make_int(eq(stack.pop(), accu))
        elif instr == OP_NEQ:
            accu = make_int(not eq(stack.pop(), accu))
        elif instr == OP_LTINT:
            accu = make_bool(to_int(accu) < to_int(stack.pop()))
        elif instr == OP_LEINT:
            accu = make_bool(to_int(accu) <= to_int(stack.pop()))
        elif instr == OP_GTINT:
            accu = make_bool(to_int(accu) > to_int(stack.pop()))
        elif instr == OP_GEINT:
            accu = make_int(to_int(accu) >= to_int(stack.pop()))
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

if sys.argv[0].endswith('rpython'):
    def make_int_array(data):
        from my_struct import unpack

        assert len(data) % 4 == 0
        result = [0]*(len(data)//4)
        for i in range(0, len(result)):
            result[i] = unpack('<i', data[4*i : 4*i+4])[0]
        return result
else:
    def make_int_array(data):
        return array.array('i', data)

def entry_point(argv):
    exe_dict = parse_executable(open(argv[1], 'rb').read())
    bytecode = make_int_array(exe_dict['CODE'])
    prims = Prims(exe_dict['PRIM'].split('\0'), argv)
    global_data = unmarshal(exe_dict['DATA'])._fields

    eval_bc(prims=prims, global_data=global_data, bc=bytecode)
    return 0

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    entry_point(sys.argv)
