import sys
import os

sys.path.insert(0, "/var/www/MET-Bot")
os.chdir("/var/www/MET-Bot")

from main import app as application