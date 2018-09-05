'''
Exports the following platform-specific variables for use in paths:
  linux - "Linux" or "Linux-x86_64"
  python - "python2.7", "python3.5", etc.

Note the linux check used to use platform.architecture, but I found
it to be slower than os.uname by several milliseconds.
'''

import sys
import os

linux = 'Linux'
if '64' in os.uname()[-1]:
    linux += '-x86_64'

python = 'python' + sys.version.split()[0].rsplit('.',1)[0]

