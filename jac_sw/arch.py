'''
jac_sw/arch.py      RMB 20180905

Exports the following platform-specific variables for use in paths:
  linux - "Linux" or "Linux-x86_64"
  python - "python2.7", "python3.5", etc.

Note the linux check used to use platform.architecture, but I found
it to be slower than os.uname by several milliseconds.


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

import sys
import os

linux = 'Linux'
if '64' in os.uname()[-1]:
    linux += '-x86_64'

python = 'python' + sys.version.split()[0].rsplit('.',1)[0]

