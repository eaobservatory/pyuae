'''
RMB 20180815

Setup sys.path for importing /jac_sw python modules.
Import this module before e.g. 'import drama'.

NOTE The "config" submodule is imported conditionally, so you shouldn't
rely on jac_sw.config in your code unless you explicitly import it.
I'd prefer to not export it at all, but so far I haven't found a good
way to do that -- python automatically adds submodules to the global
package namespace on first import.

NOTE The "uae" submodule is only intended to be used by setup.py scripts.
On import, it will change the current working directory to sys.argv[0]
and write out a setup.cfg file.

This module looks for paths in the following order, stopping at first success:
 1. Special __scriptname__syspath__ module installed alongside script
 2. Dependencies listed in config/CONFIG.Defs
 3. All current links in /jac_sw/itsroot/install

The motivation is that once 'built', scripts should continue to behave
just as they did when first installed -- even if the modules they depend on
are updated in the meantime.  Of course said dependencies could be updated
without incrementing their version numbers, defeating the intent of this
module, but having per-script syspaths seems like a reasonable compromise
between "only use the current symlinks" and "virtualenv every script".

Originally the build process would append special comments to installed
scripts that this module would then read and append to sys.paths, but I've
decided that per-script syspath modules are a better option.  They require
no changes to the original script, and don't hide runtime-changing behavior
inside of comments.  Given their obvious filenames, they are easily ignored
when comparing directory contents.  And they retain the advantages of the
original comment system:
 - Only has an effect if the jac_sw module is actually imported
 - Avoids installer looking for an 'import jac_sw' statement
     (which might be missing if jac_sw is imported by a separate module)
 - User doesn't need to include any special tags for replacement
 - Traceback line numbers unchanged between source/install scripts
 - Robust against invoking as a script or via passing to python as arg
     (unlike modifying PYTHONPATH in wrapper script or env.py)
 - No ugly, nonstandard shebang line (vs former env.py method)

On the other hand, hardcoded module paths are now hidden in a separate file,
instead of being explicitly shown in the script itself.  Given the features
outlined above, I feel the tradeoff is worth it.

Suggestions for alternatives/improvements welcome; contact RMB.
'''

import sys
import os
import arch

# set default environment variables if missing;
# note updating os.environ calls os.putenv, but not vice versa.
os.environ.setdefault("JITXML_DIR", "/jcmtdata/orac_data/ocs_configs")

# look for __scriptname__syspath__.py module
def check_module():
    try:
        import importlib  # assumes at least python2.7
        realpath = os.path.realpath(sys.argv[0])
        basename = os.path.basename(realpath)
        modname = '__' + basename.split('.')[0] + '__syspath__'
        deps = importlib.import_module(modname).deps  # config.deps
        for d in reversed(deps):
            path = d + '/lib/' + arch.linux + '/' + arch.python
            if os.path.exists(path):
                sys.path.insert(1, path)
        return True
    except:
        return False


# look for CONFIG.Defs and use those module paths
def check_config():
    import config
    if config.path:
        for mod in reversed(config.mods):
            sys.path.insert(1, mod)
        return True
    return False
    

# crawl the /jac_sw/itsroot/install directory
def check_install():
    # get a list of symlinks in the install directory (TODO configurable)
    idir = '/jac_sw/itsroot/install/'
    try:
        # os.scandir is much faster than os.listdir, but requires python3.5+
        links = [f for f in os.listdir(idir) if os.path.islink(idir+f)]
        #links = [f.name for f in os.scandir(idir) if f.is_symlink()]  # TODO
    except:
        links = []
    # exclude backup links (*Was, *old, etc), assuming unique prefixes
    current = []
    links.sort()
    for link in links:
        if current and link.startswith(current[-1]):
            continue
        current.append(link)
    for link in reversed(current):
        path = idir + link + '/lib/' + arch.linux + '/' + arch.python
        if os.path.exists(path):
            sys.path.insert(1, path)
    return True

# use boolean short-circuit evaluation; first success skips the rest
check_module() or check_config() or check_install()

# these should only be called once; do not export.
del check_module
del check_config
del check_install


