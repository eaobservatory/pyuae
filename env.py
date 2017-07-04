#!/local/python/bin/python2
'''
/usr/bin/env replacement for shebang lines, used like so:
#!/path/to/env.py -S PYTHONPATH=/jac_sw/itsroot/install/common/lib/Linux-x86_64/python2 /local/python/bin/python2

Like the FreeBSD env implementation, it works around the fact that
shebang lines only pass a single argument to the specified program:
Any argument that starts with -S is expanded using shlex.split,
then /usr/bin/env is exec'd using the expanded arguments.

Unfortunately there is an OS limit of 127 chars for shebang lines
(see the execve man page).  To work around this limit, this script
tries to determine if it's been called via shebang and reparses the line.
Basically hacks upon hacks.
'''
import sys
import os
import shlex
argv = []
if os.path.exists(sys.argv[-1]):
    line = open(sys.argv[-1]).readline()
    if line and line.startswith('#!'):
        argv = shlex.split(line[2:])
        if argv and argv[0] == sys.argv[0]:
            sys.argv = argv + [sys.argv[-1]]
        argv = []
for arg in sys.argv:
    if arg.startswith('-S'):
        s = shlex.split(arg[2:])
        if s:
            argv += s
    else:
        argv.append(arg)
argv[0] = '/usr/bin/env'
os.execv(argv[0], argv)

