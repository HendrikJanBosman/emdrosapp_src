#!/usr/bin/python
from emdros_application import *
from hebrew_prosody import *

class Scansion(EmdrosApplication):

    def __init__(self, options, localcfg=None, DO_REF=False, DO_OUT=True, DO_LBL=True):

	# initialize superclass
	EmdrosApplication.__init__(self, options, localcfg, DO_REF, DO_OUT, DO_LBL)

	# add init stuff for MainObject.
	# available: self.CFG, self.cfg (if -c option is used), self.options
	self.initData(self.mql, self.options)
	
    def initData(self, mql, options):
	self.wordClusters = WordClusterList(mql,SetOfMonads(),self.cfg,self.verbose)
	q = "SELECT ALL OBJECTS WHERE [%s] GO" % options.get('raster')
	if mql.doQuery(q):
	    raster_sheaf  = mql.getPySheaf()
	    for straw in raster_sheaf:
		for raster_obj in straw:
		    #wcl = WordClusterList(mql,raster_obj.monads,
					  #self.cfg,self.verbose)
		    #self.wordClusters.append(wcl)
		    self.wcl = WordClusterList(mql,raster_obj.monads,
					  self.cfg,self.verbose)
		    for wc in self.wcl:
			self.worClusters.append(wc)

    def display(self):
	if not self.auto:
	    for wc in self.wordClusters:
		writeln("%s %s" % (wc.flatText().ljust(30), wc))

    def displayNEW(self):
	if not self.auto:
	    for wcl in self.wordClusters:
		for wc in wcl:
		    writeln("%s %s" % (wc.flatText().ljust(30), wc))

    def store(self, mql=None):
	if mql == None: mql = self.mql
	if self.auto or userAffirms('store in database %s (as [wordcluster] objects)?' % self.database):
	    self.mql.createObjectType('wordcluster', mode='prosodic', forced=True)
	    self.mql.createObjectFeature('wordcluster', 'etcbc_txt', 'string')
	    self.mql.createObjectFeature('wordcluster', 'ascii_txt', 'string')
	    self.mql.createObjectFeature('wordcluster', 'latex_txt', 'string')
	    self.mql.createObjectFeature('wordcluster', 'utf8_txt', 'string')
	    self.mql.createObjectFeature('wordcluster', 'shebanq_txt', 'string')
	    self.mql.createObjectFeature('wordcluster', 'no_of_syllables', 'integer')
	    self.mql.createObjectFeature('wordcluster', 'no_of_stresses', 'integer')

	    for wc in self.wordClusters:
		q = 'CREATE OBJECT FROM MONADS = %s\n[wordcluster' % wc.monads.toString()
		q += '\n\tetcbc_txt := "%s";' % wc.repr(format='etcbc', sep='/')
		q += '\n\tascii_txt := "%s";' % wc.repr(format='ascii', sep='/')
		q += '\n\tshebanq_txt := "%s";' % wc.repr(format='shebanq', sep='/')
		q += '\n\tutf8_txt := "%s";' % wc.repr(format='utf8', sep='/')
		q += '\n\tlatex_txt := "%s";' % wc.repr(format='latex', sep='\\/')
		q += '\n\tno_of_syllables := %d;' % wc.noOfSyllables
		q += '\n\tno_of_stresses := %d;' % wc.noOfStresses
		q += '\n]\nGO\n'
		self.mql.doQuery(q)


if __name__ == '__main__':

    #UNCOMMENT ONE OF THE FOLLOWING TWO BLOCKS (AND DELETE THE OTHER):

    # when standard options are sufficient
    options = Options('options', parse=False)
    options.addOption('raster', 'R', default="verse")
    options.parse()

    sc = Scansion(options=options, localcfg="./scansion.cfg")
    sc.display()
    #sc.store()
