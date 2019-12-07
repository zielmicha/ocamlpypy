import sys
if sys.argv[0].endswith('rpython'):
    from rpython.rlib.rstruct.runpack import runpack
    from rpython.rlib.objectmodel import specialize

    @specialize.arg(0)
    def unpack(tmpl, b):
        return runpack(tmpl, b),
else:
    from struct import unpack
