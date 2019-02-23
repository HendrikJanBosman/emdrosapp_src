import importlib
from EmdrosPy import *
from emdros_application.syscfg.config import *
from emdros_application.mql_engine import *
from emdros_application.utils import *


class ReferenceManager:

    def __init__(self, mql, cfg=None, verbose=False, kernel=None):

        if kernel is None:
            kernel = __import__(DEFAULT_KERNEL)

        if cfg is None:
            cfg = kernel.DEFAULT_KERNEL_CFG
        if type(cfg) == str:
            cfg = kernel.DEFAULT_KERNEL_CFG
            self.cfg = Configuration(cfg, kernel=kernel)
        else:
            self.cfg = cfg


	self.mql = mql
	self.verbose = verbose
	self.matrix = {}
	self.prevQueries = {}
	self.refObjects = self.cfg.get_multi('reference_object')
	self.refFormat = self.cfg.get('reference_format')
	if self.refObjects == None:
	    self.refObjects = []
	if self.refFormat == None:
	    self.refFormat = []

	for otyp in self.refObjects:
	    q = "SELECT ALL OBJECTS WHERE"
	    q += '\n[%s get ' % otyp
	    self.features = self.cfg.get_multi('reference_feature', otyp)
	    q += self.features[0]
	    for f in self.features[1:]:
		q += (', %s' % f)
	    q += ']\n'
	    q += 'GO\n'
	    if self.mql.doQuery(q, verbose=self.verbose):
		sheaf = self.mql.getPySheaf()
		for straw in sheaf:
		    for obj in straw:
			monads = obj.monads
			mi = monads.const_iterator()
			while mi.hasNext():
			    ms = mi.next()
			    for m in range(ms.first(), ms.last()+1):
				if not self.matrix.has_key(m):
				    self.matrix[m] = {}
				if not self.matrix[m].has_key(otyp):
				    self.matrix[m][otyp] = {}
				for f in self.features:
				   self.matrix[m][otyp][f] = obj.features[f] 
            
    def getRef(self, monad):
	def doCorr(ref):
	    if self.cfg.has_key('reference_correction'):
		for k in self.cfg['reference_correction'].keys():
		    ref = re.sub(k, self.cfg.get('reference_correction', k), ref)
	    return ref
		



	self.rec = {}
	self.lst = []
	m = self.matrix[int(monad)]
	for otyp in self.refObjects:
		if m.has_key(otyp):
		    for f in self.cfg.get_multi('reference_feature', otyp):
			self.rec[f] =  m[otyp][f]
			self.lst.append(m[otyp][f])
	self.lst = tuple(self.lst)

	if self.refFormat is not None:
	    return doCorr(eval('"' + self.refFormat + '" % ' + repr(self.lst)))
	else:
	    r = self.lst[0]
	    for f in self.lst[1:]:
		r += ' ' + f
	    return doCorr(r)
    
    def byMonad(self, monad):
	return self.getRef(monad)

    def byMonads(self, monads):
	return self.byMonad(monads.first())

    def byObject(self, obj):
	return self.byMonads(obj.getMonads())
	    
    def byPySheaf(self, sheaf):
	return self.byMonads(sheaf.monads)
    
    def getString(self, monad):
	rec = self.getRecord(monad)


    def findMonads(self):
	STOP = False
	while not STOP:
	    fM = self.__findloop__()
	    if fM == None:
		if not userAffirms('reference not found, try again?'):
		    STOP = True
	    else:
		STOP = True
	return fM


    def __findloop__(self):
	lst = {}
	feat = []
	q = "SELECT ALL OBJECTS WHERE"
	for otyp in self.refObjects:
	    q += "\n[%s " % otyp
	    firstFeature = True
	    for f in self.cfg.get_multi('reference_feature', otyp):
		feat.append(f)
		i = userInput("%s:" % f)
		if i != '':
		    lst[f] = i
		    self.prevQueries[f] = i
		else:
		    if self.prevQueries.has_key(f):
			i = self.prevQueries[f]
		    else:
			i = ''
		    lst[f] = i
		if i == 'None':
		    i = ''
		    self.prevQueries[f] = i
		if i != '':
		    if firstFeature:
			firstFeature = False
		    else:
			q += " AND"
		    q += " %s = %s" % (f, i)
	for otyp in self.refObjects:
	    q += "]\n"
	q += "GO\n"
	if not self.mql.doQuery(q, verbose=self.verbose):
	    writeln(q)
	    return None
	else:
	    return self.mql.getResultMonads()

if __name__ == '__main__':
    from EmdrosApplication import *
    from Options import *
    options = Options()
    e = EmdrosApplication(options=options)
    print e.ref.getRef(364528)
    print e.ref.getRef(100)
