#!/usr/bin/python

import re
import copy
from time import gmtime, strftime
from emdros_application import *

options = Options('options')
eA = EmdrosApplication(options=options, title='labelman')

lbl = eA.lbl

lbl.logError(msg="LABELMAN STARTS", timed =True, IS_ERR=False)

if not options.get('sync'):       # if sync is set, label have already been
    lbl.updateAll()               # updated during initialization.

if lbl.ERRORS_FOUND:
    writeln('problem(s) encountered, check %s' % lbl.logfile_name)

lbl.logError(msg="LABELMAN STOPS", timed =True, IS_ERR=False)

if lbl.logfile is not None:
    lbl.logfile.close()
