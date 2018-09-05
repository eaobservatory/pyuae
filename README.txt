pyuae
Ryan Berthold 20170703

This module incorporates python scripts and modules into
the UAE build system without having to make too many changes
to the EPICS configuration files themselves.  Python scripts
should simply 'import jac_sw', which will modify the script's
environment and import paths as follows:

1. By looking for a special __scriptname__syspath__.py module
installed alongside the script.  The __syspath__ module is built
from the real paths of the dependencies listed in CONFIG.Defs.
This method is fast and helps ensure that each installed script uses
the same versions of the dependencies it was built against.

2. By looking in parent directories for a config/CONFIG.Defs file.
This allows simple testing of scripts in UAE source trees.

3. By finding all current symlinks in /jac_sw/itsroot/install.
The slowest method, providing ease-of-use for standalone scripts.

As a special case, this module is installed directly into the
main python directory (e.g. /local/python/lib/python2.7/site-packages)
since it needs to be importable with no special path setup.
In contrast, anything built using this module will typically be
installed to the standard /jac_sw/itsroot/install location.

To install scripts so that they use method 1, you'll need to create
a setup.py file and invoke it in your Makefile.Host:

	install:
		../setup.py install

Or you could create an alternate install target inside a more typical
Makefile.Host as follows:

	include $(TOP)/config/CONFIG
	TARGETS += pyinstall
	pyinstall:
		../setup.py install
	include $(TOP)/config/RULES.Build

Here's a simple setup.py file that imports this module:

	from jac_sw.uae import setup
	setup(scripts = ['test.py'])

Note that the setup.cfg file is build output and should be ignored.

