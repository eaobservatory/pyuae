#!/local/python/bin/python2
import sys
import time
print('%.6f importing jac_sw...'%(time.time()))
import jac_sw
print('%.6f importing drama...'%(time.time()))
import drama
print('%.6f printing sys.path (minus eggs):'%(time.time()))
import pprint
pprint.pprint([x for x in sys.path if not 'egg' in x])
print('%.6f done.'%(time.time()))
