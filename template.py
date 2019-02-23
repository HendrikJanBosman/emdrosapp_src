#!/usr/bin/python

from emdros_application import *

DO_REF = True
DO_OUT = True
DO_LBL = True


class MainObject(EmdrosApplication):

    def __init__(self, options, title=''):

	# initialize superclass
	EmdrosApplication.__init__(self, options, title,
                                   DO_REF=DO_REF, DO_OUT=DO_OUT, DO_LBL=DO_LBL)

	# add init stuff for MainObject here
	# settings are stored in self.cfg

    def main(self):
        ### replace by something useful
        print 'emdros_application succesfully initialized for database %s' % self.database


if __name__ == '__main__':

    #UNCOMMENT ONE OF THE FOLLOWING TWO BLOCKS (AND DELETE THE OTHER):

    # when standard options are sufficient
    options = Options('options')

    # when custom options are needed
    #options = Options('options', parse=False)
    #options.addOption('auto','a','automatic',action='store_true',default=False)
    #   etc.
    #options.parse()
    
    #options.set('gui', True)
    main_object = MainObject(options=options, title="Sample application")
    main_object.main()
