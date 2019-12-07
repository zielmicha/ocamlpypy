# ocamlpypy

ocamlpypy is a fast JIT compiler for Ocaml bytecode that uses PyPy metatracing JIT compiler.

It is currently much faster than ocamlrun, and slower than ocamlopt, but there is still a lot to improve.

## Building and running

```
pypy ~/apps/pypy/rpython/bin/rpython -Ojit bytecode.py
ocamlc foo.ml -o foo.byte
./bytecode-c foo.byte
```
