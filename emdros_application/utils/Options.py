#from emdros_application.syscfg.config import * 
from Paths import *
from IOTools import *
from optparse import OptionParser
from Configuration import Configuration

class Options:

    def __init__(self, cfg_name='options', parse=True):
	optcfg = Configuration(addPathAndExt('options',
                                             #emdros_application.syscfg.config.BOOT_DIR,
                                             #emdros_application.syscfg.config.CFG_EXT))
					     BOOT_DIR, CFG_EXT))

	self.optionKeys = []  # gets filled in self.addOption()
	self.forced = {}
	self.valid = {}
	self.parser = OptionParser()
	for opt in optcfg.get_multi('opt'):
	    full = opt
	    abbr = optcfg.get("abbr", opt)
	    help = optcfg.get("help", opt)
	    action = optcfg.get("action", opt)
	    default = optcfg.get("default", opt)
	    forced = optcfg.get("forced", opt)
	    valid  = optcfg.getmulti("valid", opt)
	    self.addOption(full, abbr, help=help, 
	    	           action=action, default=default, valid=valid, forced=forced)
	del optcfg

	# use param 'parse' when you don't need any custom options ######
	if parse:
	    self.parse()
    
    def set(self, key, val):
	exec ("self.opts.%s = '%s'" % (key, val) )

    def get(self, key):
	try:
	    exec ("r = self.opts.%s" % key)
	except:
	    return None
	return r

    def keys(self):
	return self.optionKeys

    def has_key(self, key):
	return key in self.optionKeys

    def __setitem__(self, key, val):
	self.set(key, val)

    def __getitem__(self, key):
	return self.get(key)

    def __repr__(self):
	rpr = ""
	keys = self.optionKeys
	if len(keys) > 0:
	    rpr = "%s = %s" % (keys[0].ljust(8), self.get(keys[0]))
	if len(keys) > 1:
	    for k in keys[1:]:
		rpr += "\n%s = %s" % (k.ljust(8), self.get(k))
	return rpr

    def isForced(self, key):
	return self.forced[key]

    def isValid(self, key, val):
	if not key in self.valid.keys():
	    return True
	else:
	    return val in self.valid[key]

    def validVals(self, key):
	if not key in self.valid.keys():
	    return None
	else:
	    return self.valid[key]


    def addOption(self, opt, abbr, help=None, action=None, default=None, valid=None, forced=False):
	self.optionKeys.append(opt)
	full = "--%s" % opt
	abbr = "-%s" % abbr
	if default == "True" : default = True
	if default == "False" : default = False
	self.forced[opt] = forced
	if valid <> None:
	    self.valid[opt] = valid
	self.parser.add_option(abbr, full, help=help, 
			       action=action, default=default)


    def checkAllOptions(self):
	for opt in self.optionKeys:
	    if self.isForced(opt) and self.get(opt) is None:
		raise Exception('missing option: --%s %s' % (opt, repr(self.valid[opt])))
	    elif not self.isValid(opt, self.get(opt)) and self.get(opt) <> None:
		    raise Exception('invalid option: --%s %s %s' % (opt, self.get(opt), repr(self.valid[opt])))

	    
    def parse(self):
	(self.opts, self.args) = self.parser.parse_args()
	try:
	    self.checkAllOptions()
	except:
	    write('error in option ')
	    exitOnError()

    def getArgs(self):
	return self.args

    def toConfiguration(self, kernel=None):
        cfg = Configuration(name='options', kernel=kernel)
        for k in self.optionKeys:
            cfg.set(k, self.get(k))
        return cfg
