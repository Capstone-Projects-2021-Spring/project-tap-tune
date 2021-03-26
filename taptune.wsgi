import os
import sys
sys.path.insert(0, '/var/www/html/taptune')
os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache/"

from main import app as application