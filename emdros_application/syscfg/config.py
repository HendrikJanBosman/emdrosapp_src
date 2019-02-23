#### KERNEL CONFIGURATION FILE, PRESENTLY SET TO ETCBC-BASED BIBLICAL HEBREW ###
KERNEL_NAME = "config"

#### IMPORTED MODULES, DO NOT CHANGE
from config import *
import os.path
import sys
import platform
#from utils.Paths import *

DEFAULT_KERNEL = 'bhebrew'

##### CHANGE THE FOLLOWING TO MATCH YOUR SYSTEMS ##########

if platform.system() == 'Linux':

    EMDROSPY_DIR   = '/usr/local/lib/x86_64-linux-gnu/emdros'

    HOME_DIR       = os.path.expanduser('~/')

    EMDROSAPP_DIR = HOME_DIR + 'ownCloud/git/EmdrosApplication/'
    SRC_DIR  = EMDROSAPP_DIR + 'emdrosapp_src/'
    BOOT_DIR       = SRC_DIR + 'emdros_application/syscfg/'
    CFG_DIR        = BOOT_DIR
    TMP_DIR        = HOME_DIR + "tmp/"

    EDITOR = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'vi'

### SETUP OTHER SYSTEMS; MAKE SURE TO SPECIFY ALL VARIABLES UNDER 'Linux'
elif platform.system() == 'Windows':
    pass
elif platform.system() == 'SunOS':
    pass
elif platform.system() == 'Darwin': # this is what Mac OS X calls itself
    pass
else:
    raise Exception ('unknown operating system %s' % platform.system())


#### DO NOT CHANGE BELOW THIS LINE, UNLESS YOU KNOW WHY ###########

############ STANDARD FILE EXTENSIONS ########
MQL_EXT     = ".mql"
DOM_EXT     = MQL_EXT
LBL_EXT     = ".lbl"
CFG_EXT     = ".cfg"
TEX_EXT     = ".src"   # when done, do: gt2tex < *.src > *.tex
JSON_EXT    = ".json"

### IMPORT EMDROSPY #############
sys.path.append(EMDROSPY_DIR)
sys.path.append(SRC_DIR)
from EmdrosPy import *
backends = ['NO_BACKEND', 'POSTGRESQL', 'MYSQL', 'SQL2', 'SQL3']
DEFAULT_KERNEL_BASE = 'syscfg.%s' % DEFAULT_KERNEL
DEFAULT_KERNEL = "emdros_application.syscfg.%s" % DEFAULT_KERNEL
