'''
Crawls up the script's path looking for config/CONFIG.Defs,
providing the following information about the UAE environment:

path: to CONFIG.Defs
config: dict of keys/values in CONFIG.Defs
inst: install path, APPLIC_INSTALL/APPLIC_VERSION
deps: dependency list, inst + APPLIC_DEPENDS + APPLIC_BASE
libs: library path list from deps
incs: include path list from deps
mods: python module search paths, inst + existing libs
'''

import os
import sys
from . import arch

config = {}
inst = ''
deps = []
libs = []
incs = []
mods = []

path = os.path.realpath(sys.argv[0])
if sys.argv[0]:  # not interactive
    path = os.path.dirname(path)
while path != '/':
    if os.path.exists(path + '/config/CONFIG.Defs'):
        break
    path = os.path.realpath(path + '/..')
path += '/config/CONFIG.Defs'
try:
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key,eq,value = line.partition('=')
            config[key] = value
    inst = config['APPLIC_INSTALL'] + '/' + config['APPLIC_VERSION']
    inst = os.path.realpath(inst)
    deps = [inst] + config['APPLIC_DEPENDS'].split() + [config['APPLIC_BASE']]
    deps = [os.path.realpath(x) for x in deps]
    libs = ['./'] + [x + '/lib/' + arch.linux for x in deps]
    libs = [os.path.realpath(x) for x in libs]
    libs = [x for x in libs if os.path.exists(x) or inst in x]
    incs = ['./']
    for d in deps:
        incs.append(d + '/include')
        incs.append(d + '/include/os/' + arch.linux)
    incs = [os.path.realpath(x) for x in incs]
    incs = [x for x in incs if os.path.exists(x) or inst in x]
    mods = [x + '/' + arch.python for x in libs]
    mods = [os.path.realpath(x) for x in mods if os.path.exists(x) or inst in x]
except:
    path = ''

