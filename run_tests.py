import sys, subprocess, os, colorama

nonstop = bool(os.environ.get('NONSTOP'))
ok = 0
fail = 0

for test in sys.argv[1:]:
    print(colorama.Fore.GREEN + test + colorama.Style.RESET_ALL)
    if subprocess.call(['ocamlc', '-g', test, '-o', 'test.byte']) != 0:
        if nonstop:
            continue
        else:
            sys.exit('compilation failed')

    try:
        out = subprocess.check_output(['pypy', 'bytecode.py', 'test.byte'])
    except Exception:
        if nonstop:
            fail += 1
            continue
        else:
            sys.exit('bytecode failed')

    try:
        exp = open(test[:-3] + '.reference', 'rb').read()
    except IOError:
        exp = ''

    if out != exp:
        print('expected:')
        print(exp)
        print('got:')
        print(out)
        if nonstop:
            fail += 1
        else:
            sys.exit(1)
    else:
        ok += 1

print('ok', ok, 'fail', fail)
