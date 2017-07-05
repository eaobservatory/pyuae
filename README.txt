pyuae
Ryan Berthold 20170703

This module incorporates python scripts and modules into
the UAE build system without having to make too many changes
to the EPICS configuration files themselves.  It does this
via two components:

1. The env.py script, which allows python scripts to be
called with a modified PYTHONPATH environment variable.
Python scripts will have their #! line modified at build time
such that they will load modules from the dependencies given
in the config/CONFIG.Defs file.

2. The 'uae' python module, which is imported by setup.py
files and parses the config/CONFIG.Defs file.  It also modifies
the distutils build classes to insert the env.py shebang line.

As a special case, this module is installed directly into the
main python directory (e.g. /local/python/lib/python2.7/site-packages)
since it needs to be importable with no special path setup.
In contrast, anything built using this module will typically be
installed to the standard /jac_sw/itsroot/install location.

For now, python scripts/modules will need to be in a dedicated
directory with a custom Makefile.Host file:

install:
	../setup.py install

If you need to build C programs or other non-python targets,
you can incorporate setup.py into a more typical UAE
Makefile.Host file by updating the TARGETS variable like so:

include $(TOP)/config/CONFIG
TARGETS = pyinstall
pyinstall:
	../setup.py install
include $(TOP)/config/RULES.Build

Here's an example setup.py file that imports this module:

import os
import uae
uae.scripts = [test.py]
uae.setup()

Note that the setup.cfg file is build output and should be ignored.

