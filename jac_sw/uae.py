'''
jac_sw/uae.py   RMB 20180307

UAE module for setup.py build scripts.

Provides a setup() function, which invokes distutils setup()
with UAE defaults and build/install configuration.
Also exposes the variables exported by the 'config' module: incs, libs, etc.

Note that importing this module will create a setup.cfg file to define
the options for setup.py; this should be added to your .gitignore.

Example setup.py file (from pydrama):

#!/local/python/bin/python2
import jac_sw.uae as uae
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


Copyright (C) 2020 East Asian Observatory

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from jac_sw.arch import *
from jac_sw.config import *

if not path:
    raise RuntimeError('CONFIG.Defs not found')
    
if not inst:
    raise RuntimeError('CONFIG.Defs missing APPLIC_INSTALL and/or APPLIC_VERSION')

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

with open('setup.cfg', 'w') as f:
    f.write('[build]\n')
    f.write('build-base=./O.' + linux + '\n')
    f.write('[install]\n')
    f.write('install-lib=%s/lib/%s/%s\n' % (inst, linux, python))
    f.write('install-scripts=%s/bin/%s\n' % (inst, linux))
    f.write('install-data=%s/data\n' % (inst))
    f.write('install-headers=%s/include\n' % (inst))

# debug
sys.stdout.write('UAE config:\ninst: %s\ndeps: %s\nlibs: %s\nincs: %s\nargv: %s\n' % (inst,deps,libs,incs,sys.argv))

from distutils.core import setup as dsetup
from distutils.command.build_scripts import build_scripts as dbuild_scripts
from distutils.command.install_scripts import install_scripts as dinstall_scripts
from distutils.util import convert_path
from distutils.extension import Extension
from Cython.Distutils import build_ext

import re

def mtime(filename):
    '''Return os.stat(filename).st_mtime, or 0.0 on error.'''
    try:
        return os.stat(filename).st_mtime
    except:
        return 0.0
                
class build_scripts(dbuild_scripts):
    def copy_scripts(self):
        # create __scriptname__syspath__.py module alongside installed script;
        # the jac_sw module will import it to update sys.path.
        outfiles = [os.path.join(self.build_dir, os.path.basename(convert_path(s))) for s in self.scripts]
        mt_old = [mtime(f) for f in outfiles]
        dbuild_scripts.copy_scripts(self)
        mt_new = [mtime(f) for f in outfiles]
        modified = [f for f,o,n in zip(outfiles, mt_old, mt_new) if o != n]
        for outfile in modified:
            # make sure it's a python script
            shebang = open(outfile).readline()
            if not (shebang.startswith('#!') and 'python' in shebang):
                continue
            scriptdir = os.path.dirname(outfile)
            scriptname = os.path.basename(outfile).split('.')[0]
            modpath = scriptdir + '/__' + scriptname + '__syspath__.py'
            with open(modpath,'w') as f:
                f.write('deps = [\n')
                for d in deps:
                    f.write('%s,\n' % (repr(d)))
                f.write(']\n')

class install_scripts(dinstall_scripts):
    def run(self):
        # skip the chmod, just copy things over.
        if not self.skip_build:
            self.run_command('build_scripts')
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)

def setup(name = config['APPLIC_VERSION'],
          version = 'uae',
          cmdclass = {'build_scripts':build_scripts,
                      'install_scripts':install_scripts,
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
                 keep the uae build_scripts so "#jac_sw.sys.path"
                 comments are generated properly in installed scripts:
                 {'build_scripts':uae.build_scripts, ...}
    '''
    dsetup(name=name, version=version, cmdclass=cmdclass, **kwargs)


def git_version_file(filename):
    '''
    Create a file containing git version information.
    filename.__version__ is set to the 'git describe' output, while
    filename.__doc__ holds a more verbose summary of the repository status.
    '''
    import time
    import socket
    from subprocess import check_output
    def doc(f, cmd):
        out = check_output(cmd.split())
        out = str(out.decode())
        out = out.strip().replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
        f.write('\n\n=== %s ===\n\n%s' % (cmd, out))
        return out
    with open(filename, 'w') as f:
        hostname = socket.gethostname()
        timestamp = time.strftime('%Y%m%d %H:%M:%S %Z')
        inpath = os.path.realpath(os.path.basename(sys.argv[0]))
        outpath = os.path.realpath(filename)
        f.write('"""\n')
        f.write('%s\n' % (outpath))
        f.write('Generated %s by %s:%s\n' % (timestamp, hostname, inpath))
        description = doc(f, 'git describe --always --long --dirty')
        doc(f, 'git log -1 --decorate --stat')
        doc(f, 'git status')
        doc(f, 'git diff')
        f.write('\n"""\n\n__version__ = "%s"\n\n\n' % (description))


