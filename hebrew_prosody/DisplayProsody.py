#!/usr/bin/python
from emdros_application import *


class MainObject(EmdrosApplication):

    def __init__(self, options, localcfg=None,
		 DO_REF=True, DO_OUT=True, DO_LBL=False):

	# initialize superclass
	EmdrosApplication.__init__(self, options, localcfg,
				   DO_REF, DO_OUT, DO_LBL)
	self.mode   = "prosodic"
	self.format = "latex"

    def main(self):
	q = "SELECT ALL OBJECTS WHERE [verseline get prosodic_labels] GO"

	if self.mql.doQuery(q):
	    for straw in self.mql.getPySheaf():
		for verseline in straw:
		    self.output(verseline)
		    
    def output(self, verseline):
	curr_ref = ''
	new_ref = self.ref.byObject(verseline)
	if new_ref <> curr_ref:
	    write('%s & ' % new_ref)
	    curr_ref = new_ref
	write(self.out.byMonads(verseline.monads) + ' & ')
	writeln(verseline['prosodic_labels'] + '\\\\')



if __name__ == '__main__':

    options = Options('options')

    # when custom options are needed
    #options = Options('options', parse=False)
    #options.addOption('auto','a','automatic',action='store_true',default=False)
    #   etc.
    #options.parse()


    mo = MainObject(options=options)
    mo.main()
