'''
UAE module for setup.py build scripts.

Provides a setup() function, which invokes distutils setup()
with UAE defaults and build/install configuration.

Also provides some info about the UAE environment:
 - inst: install path, APPLIC_INSTALL/APPLIC_VERSION
 - deps: dependency list, inst + APPLIC_DEPENDS + APPLIC_BASE
 - libs: library path list from deps
 - incs: include path list from deps

Note that setup.py will create a setup.cfg file to define
its options; this should be added to your .gitignore.

Example setup.py file (from pydrama):

#!/local/python/bin/python2
import uae
uae.setup(
    packages = ['drama'],
    ext_modules = [
        uae.Extension("drama.__drama__", ["src/drama.pyx"],
            depends=['setup.py',
                     'src/drama.pxd',
                     'src/ditsaltin.h',
                     'src/ditsmsg.h'],
            include_dirs=uae.incs,
            library_dirs=uae.libs,
            libraries=['jit', 'expat', 'tide', 'ca', 'Com', 'git',
                       'dul', 'dits', 'imp', 'sds', 'ers', 'mess', 'm'],
            define_macros=[("unix",None),("DPOSIX_1",None),
                           ("_GNU_SOURCE",None),("UNIX",None)],
            extra_compile_args=["-fno-inline-functions-called-once"]
            )])
'''
import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))

Linux = 'Linux'
if '64' in os.uname()[-1]:
    Linux += '-x86_64'

config = {}
p = os.path.realpath(os.curdir)
while p != '/':
    if os.path.exists(p + '/config/CONFIG.Defs'):
        break
    p = os.path.realpath(p + '/..')
with open(p + '/config/CONFIG.Defs') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key,eq,value = line.partition('=')
        config[key] = value

inst = config['APPLIC_INSTALL'] + '/' + config['APPLIC_VERSION']
inst = os.path.realpath(inst)
deps = [inst] + config['APPLIC_DEPENDS'].split() + [config['APPLIC_BASE']]
libs = ['./'] + [x + '/lib/' + Linux for x in deps]
libs = [os.path.realpath(x) for x in libs]
libs = [x for x in libs if os.path.exists(x) or inst in x]
incs = ['./']
for d in deps:
    incs.append(d + '/include')
    incs.append(d + '/include/os/' + Linux)
incs = [os.path.realpath(x) for x in incs]
incs = [x for x in incs if os.path.exists(x) or inst in x]

# modify options before importing distutils;
# setup.cfg avoids some bugs with sys.argv parsing.
pyversion = 'python' + sys.version.split()[0].rpartition('.')[0]
with open('setup.cfg', 'w') as f:
    f.write('[build]\n')
    f.write('build-base=./O.' + Linux + '\n')
    f.write('[install]\n')
    f.write('install-lib=%s/lib/%s/%s\n' % (inst, Linux, pyversion))
    f.write('install-scripts=%s/bin/%s\n' % (inst, Linux))
    f.write('install-data=%s/data\n' % (inst))
    f.write('install-headers=%s/include\n' % (inst))

# debug
sys.stdout.write('UAE config:\ninst: %s\ndeps: %s\nlibs: %s\nincs: %s\nargv: %s\n' % (inst,deps,libs,incs,sys.argv))

from distutils.core import setup as dsetup
from distutils.command.build_scripts import build_scripts as dbuild_scripts
from distutils.util import convert_path
from distutils.extension import Extension
from Cython.Distutils import build_ext

import re

class build_scripts(dbuild_scripts):
    def copy_scripts(self):
        dbuild_scripts.copy_scripts(self)
        mods = [x + '/' + pyversion for x in libs]
        mods = [os.path.realpath(x) for x in mods if os.path.exists(x) or inst in x]
        # TODO use bindir of this python, rather than /local hardcode
        shebang = '#!/local/python/bin/env.py -S "PYTHONPATH='
        shebang += ':'.join(mods) + '" '
        first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')
        for script in self.scripts:
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            line = open(outfile).readline()
            match = first_line_re.match(line)
            if match and not line.startswith(shebang):
                post_interp = match.group(1) or ''
                line = shebang + self.executable + post_interp + '\n'
                lines = open(outfile).readlines()
                lines[0] = line
                open(outfile, 'w').writelines(lines)


def setup(name = config['APPLIC_VERSION'],
          version = 'uae',
          cmdclass = {'build_scripts':build_scripts,
                      'build_ext': build_ext},
          **kwargs):
    '''
    Invoke distutils.core.setup() with defaults for UAE.
    The following are some useful kwargs, see distutils docs for more:
     - scripts []
     - packages []
     - py_modules []
     - ext_modules []
     - package_dir {}
     - cmdclass: If you override this kwarg, for instance to build
                 non-cython extensions, you probably still want to
                 keep the uae build_scripts so PYTHONPATH is set
                 properly in installed scripts:
                 {'build_scripts':uae.build_scripts, ...}
    '''
    dsetup(name=name, version=version, cmdclass=cmdclass, **kwargs)

