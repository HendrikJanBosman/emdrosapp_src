# The init procedure reads a *.lbl file, in the following format:
# LBL_FILE = {LABEL_DEFINITION}*
# LABEL_DEFINITION = LABEL {PATTERN}*
# LABEL = '//#'[:char:]+\n
# PATTERN = MQL Query, terminated by 'GO'

import re
from emdros_application.syscfg.config import *
from emdros_application.utils.Paths import *
from emdros_application.utils.IOTools import *


###### LabelDefBase contains a dictionary of LabelDefinitions, which
###### is filled from outside, by LabelManager.__init__

class LabelDefBase:

    def __init__(self, verbose=False):
        self.labelDef = {}
	self.otypes = []
	self.verbose = verbose


    def __repr__(self):
	rep =  "LabelDefBase:"
	for o in self.otypes:
	    rep += "\n   %s" % repr(self.labelDef[o]) 
	return rep


    def add(self, labelDefinition):
	otype = labelDefinition.otype
        self.labelDef[otype] = labelDefinition
	if otype not in self.otypes:
	    self.otypes.append(otype)
    
    def addFromFile(self, filename=None, otype=None, mode=None, verbose=False):
	self.add(LabelDefinition(filename=filename, otype=objectType, mode=mode, 
				 verbose=self.verbose))

    def getObjectTypes(self):
	return self.otypes

    def getLabels(self, otype):
	if self.labelDef.has_key(otype):
	    return self.labelDef[otype].labels
	else:
	    return None

    def getDefs(self, otype, label):
	if self.labelDef.has_key(otype) and \
		    self.labelDef[otype].has_key(label):
	    return  self.labelDef[otype][label]
	else:
	    return None

    def hasLabel(self, otype, label):
        return self.labelDef[otype].hasLabel(label)

    def addLabel(self, otype, label):
        return self.labelDef[otype].addLabel(label)
    
    def addDefinition(self, otype, label, definition):
	self.labelDef[otype].addDefinition(label, definition)

    def delLabel(self, otype, label):
	self.labelDef[otype].delLabel(label)
    
    def removeLabel(self, otype, label):
	self.delLabel(otype, label)

    def delDefinition(self, otype, label, d):
	self.labelDef[otype].delDefinition(label, d)

    def removeDefinition(self, otype, label, d):
	self.delDefinition(otype, label, d)

    def setChanged(self, otype, b=True):
	self.labelDef[otype].setChanged(b)

    def isChanged(self, otype):
	return self.labelDef[otype].isChanged()
    
    def saveToFile(self, otype, filename=None, confirm=False):
	self.labelDef[otype].saveToFile(filename, confirm)

    def doSave(self, otype, filename=None):
	self.labelDef[otype].doSave(filename)
    
    def getAssignedFeatures(self, otype):   # labels which are MQL assignment
	lbl = self.getLabels(otype)         # statements
	if lbl:
	    features = []
	    for l in lbl:
		if ':=' in l:
		    feature.append(re.sub('[ \t]*:\.*', '', l))
	    return features
	else:
	    return None

class LabelDefinition:
    def __init__(self, filename=None, otype=None, mode=None, verbose=False, kernel=None):

        import importlib
        def hasGOKeyWord(line):
            return (re.search("^[ \t]*[Gg][Oo][ \t\n]*$", line) or \
               re.search("\][ \t]*[Gg][Oo][ \t\n]*$", line))


        if kernel is None:
            kernel = importlib.import_module('config')
	self.otype = otype
	self.mode = mode
	self.verbose = verbose
	filename = addPathAndExt(filename, kernel.LBL_DIR, kernel.LBL_EXT)
	self.filename = filename
        self.labels = []
        self.defs   = {}
	self.changed = False
        
        try:
            input = file(filename, "r")
            lines = []
            for l in input:
                lines.append(l)
	    input.close()
        except:
	    if self.verbose:
		if filename is None:
		    writeln("no lbl file for %s %s labels specified, skipped." \
                             % (mode, otype))
		else:
		    writeln("lbl file %s does not exist, no %s %s labels." % \
			(filename, mode, otype))
            lines = []
        
        lbl = "UNDEF"
        patt = ""
        for line in lines:
            if (line[0] == "#") or (line[:3] == "//#"):  # new label encountered
                lbl = re.sub("//#", "", line) # remove leading comment plus hash
                lbl = re.sub("#", "", lbl)    # remove leading hash sign
                lbl = re.sub("\/\/.*$", "", lbl) # remove comments, starting with //
                lbl = re.sub("[ \t\n]*$", "", lbl) # remove trailing blanks / nl
                self.labels.append(lbl)
                self.defs[lbl] = []
                patt = ""         # clear current pattern
                continue          # move on to next line

            else:
                line = re.sub("\/\/.*$", "", line)        # remove comments
                if not re.search('[^ \t]', line): continue # skip empty lines

            patt += line  # add line to current pattern, including \n
            if hasGOKeyWord(line):
		patt = re.sub("^[ \t\n]*", "", patt) # remove leading blanks
		
                #### if lbl == UNDEF, no label is encountered up to eof ###
		if lbl != 'UNDEF':
                    #### add current pattern to defs list
		    (self.defs[lbl]).append(patt)
		    patt = ""  # clear pattern

    def has_key(self, key):
	return self.defs.has_key(key)

    def hasKey(self, key):
	return self.has_key(key)

    def hasLabel(self, label):
	return self.has_key(label)

    def __getitem__(self, key):
        if self.defs.has_key(key):
            return self.defs[key]
        else:
            return None

    def __setitem__(self, key, val):
	if not self.defs.has_key(key):
	    self.labels.append(key)
	self.defs[key] = val

    def __repr__(self):
	rep = "LabelDefinition for %s, file %s, labels" % (self.otype, self.filename)
	for l in self.labels:
	    rep += " %s" % l
	return rep

    def addLabel(self, label):
	if not (label in self.labels):
	    self.labels.append(label)
	    self.defs[label] = []
	    self.setChanged(True)
	return len(self.labels) + 1


    def addDefinition(self, label, definition):
	if not definition in self.defs[label]:
	    self.addLabel(label)
	    self.defs[label].append(definition)
	    self.setChanged(True)


    def delLabel(self, label):
	self.labels.remove(label)
	self.defs.pop(label, None)
	self.setChanged(True)

    def removeLabel(self, label):
	self.delLabel(label)

    def delDefinition(self, label, d):
	if type(d) == str:
	    self.defs[label].remove(d)
	elif type(d) == int:
	    del self.defs[label][d]
	self.setChanged(True)

    def removeDefinition(self, label, d):
	self.delDefinition(label, d)

    def setChanged(self, b=True):
	self.changed = b

    def isChanged(self):
	return self.changed

    def saveToFile(self, filename=None, confirm=False):
	if filename == None:
	    filename = self.filename
	write("saving labels to %s. " % filename)
	if confirm:
	    if userAffirms("OK?", confN=True):
		self.doSave(filename)
		return True
	    else:
		writeln("OK, %s is not updated." % filename)
		writeln("your changes will disappear at next update.")
		return False
	else:
	    write("...")
	    self.doSave(filename)
	    return True

    def doSave(self, filename):
	if filename == None:
	    filename = self.filename
	f = open(filename, 'w')
	for l in self.labels:
	    f.write("\n\n\n//#%s" % l)
	    for d in self.defs[l]:
		d = re.sub("^[\\n]*", "", d)
		f.write("\n\n%s" % d)
	f.write("\n")
	f.close()
	if self.verbose:
	    writeln("done.")


    def niceRepr(self):
        repStr = ""
        for l in self.labels:
            repStr += "#" + l + "\n"
            for d in self.defs[l]:
                repStr += d + "\n\n"
        return repStr
