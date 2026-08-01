import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

try:
    import app.main
    print('SUCCESS')
except Exception as e:
    import traceback
    traceback.print_exc()
