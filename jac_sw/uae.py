'''
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
'''

from arch import *
from config import *

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
            scriptdir = os.path.dirname(outfile)
            scriptname = os.path.basename(outfile).split('.')[0]
            modpath = scriptdir + '/__' + scriptname + '__syspath__.py'
            with open(modpath,'w') as f:
                f.write('deps = [\n')
                for d in deps:
                    f.write('%s,\n', repr(d))
                f.write(']\n')


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
                 keep the uae build_scripts so "#jac_sw.sys.path"
                 comments are generated properly in installed scripts:
                 {'build_scripts':uae.build_scripts, ...}
    '''
    dsetup(name=name, version=version, cmdclass=cmdclass, **kwargs)



