#!/usr/bin/python
from emdros_application import *

class MainObject(EmdrosApplication):

    def __init__(self, options, localcfg=None,
		 DO_OUT=False, DO_REF=True, DO_LBL=False):

	# initialize superclass
	EmdrosApplication.__init__(self, options, localcfg,
				   DO_REF, DO_OUT, DO_LBL)

    def main(self):

	import re 

	self.mql.createObjectFeature("colon", "no_of_feet", "integer", "-1")
	self.mql.createObjectFeature("verseline", "metre", "string", "-1")
	q = "select all objects where [verseline [colon [wordcluster get etcbc_txt, no_of_feet] ] ]go"
	self.mql.doQuery(q)
	for straw in self.mql.getPySheaf():
	    for verseline in straw:
		metre = []
		for straw in verseline.sheaf:
		    for colon in straw:
			if not self.verbose: self.spinner.next()
			stresses = 0
			for straw in colon.sheaf:
			    for wordcluster in straw:
				stresses += wordcluster['no_of_feet']
				if self.verbose:
				    write(wordcluster['etcbc_txt'] + ' ')
			if self.verbose: writeln(": %d" % stresses)
			self.mql.setObjectFeature("colon", colon.id_d,
						  "no_of_feet", stresses)
			metre.append(stresses)
		metre_string = '"%d' % metre[0]
		for m in metre[1:]:
		    metre_string += '+%d' % m
		metre_string += '"'
		self.mql.setObjectFeature("verseline", verseline.id_d,
						  "metre", metre_string)



if __name__ == '__main__':

    options = Options('options')
    mo = MainObject(options=options)
    mo.main()
