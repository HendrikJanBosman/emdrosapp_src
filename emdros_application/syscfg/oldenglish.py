#### KERNEL CONFIGURATION FILE FOR OLDENGLISH DATABASES ###
import os.path
import sys
import platform
#from utils.Paths import *
from config import *

KERNEL_NAME = 'oldenglish'

#### CHANGE THE SETTINGS BELOW TO MATCH YOUR SYSTEM / SETUP

# Name of master cfg file, see man CFG(3),
# can be overruled by -C command line option.

DEFAULT_KERNEL_CFG = 'oldenglish.cfg'

if platform.system() == 'Linux':

    # options here: 'NO_BACKEND', 'POSTGRESQL', 'MYSQL', 'SQL2', 'SQL3'
    DEFAULT_BACKEND = 'SQL3'

    # Overruled by -d, -u and -p command line options, or, failing these, by 
    # the keys database, usr and pwd in DEFAULT_KERNEL_CFG:
    DEFAULT_DATABASE = 'oldenglish'
    DEFAULT_USR      = 'emdf'
    DEFAULT_PWD      = 'changeme'

    EMDROSAPP_DIR = HOME_DIR + 'ownCloud/git/EmdrosApplication/'
    PROJECT_DIR   = EMDROSAPP_DIR + 'emdrosapp_data/oldenglish/'

    ### THE FOLLOWING ARE NOW UNDER THE PROJECT TREE,
    ### BUT CAN POINT TO ANYWHERE YOU LIKE ON YOUR SYSTEM

    CFG_DIR      = PROJECT_DIR + 'config/'
    DOMAINS_DIR  = CFG_DIR + 'domains/'
    JSON_DIR     = CFG_DIR + 'json/'
    DOMAINS_DIR  = CFG_DIR + 'domains/'
 
    LBL_DIR      = PROJECT_DIR + 'lbl/'
    DATA_DIR     = PROJECT_DIR + 'data/'
    TMP_DIR      = HOME_DIR + 'tmp/' 
    LOG_DIR      = TMP_DIR

### SETUP OTHER SYSTEMS; COPY AND EDIT FROM 'Linux' ####

elif platform.system() == 'SunOS':
    DEFAULT_DATABASE = 'oldenglish'
    DEFAULT_BACKEND  = 'POSTGRESQL'
    DEFAULT_USR      = 'hjb'
    DEFAULT_PWD      = 'changeme'
    EMDROSAPP_DIR = HOME_DIR + 'github/EmdrosApplication/'
    PROJECT_DIR   = EMDROSAPP_DIR + 'oldenglish/'

    CFG_DIR      = PROJECT_DIR + 'config/'
    DOMAINS_DIR  = CFG_DIR + 'domains/'
    JSON_DIR     = CFG_DIR + 'json/'
    DOMAINS_DIR  = CFG_DIR + 'domains/'
 
    LBL_DIR      = PROJECT_DIR + 'lbl/'
    DATA_DIR     = PROJECT_DIR + 'data/'
    TMP_DIR      = '/usr/local/tmp/' 
    LOG_DIR      = TMP_DIR

elif platform.system() == 'Windows':
    pass
    
elif platform.system() == 'Darwin': # this is what Mac OS X calls itself
    pass

else:
    raise Exception ('unknown operating system %s' % platform.system())

### SOME ALTERNATIVE SPELLINGS, FOR SLOPPY PROGRAMMERS LIKE MYSELF #######
DOMAIN_DIR  = DOMAINS_DIR
DOM_DIR     = DOMAINS_DIR
DOMAIN_EXT  = DOM_EXT
LABEL_DIR   = LBL_DIR
