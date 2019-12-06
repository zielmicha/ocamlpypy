import sys, subprocess, sys

for test in sys.argv[1:]:
    print(test)
    subprocess.check_call(['ocamlc', '-g', test, '-o', 'test.byte'])
    out = subprocess.check_output(['python', 'bytecode.py', 'test.byte'])
    exp = open(test[:-3] + '.reference', 'rb').read()
    if out != exp:
        print('expected:')
        print(exp)
        print('got:')
        print(out)
        sys.exit(1)
