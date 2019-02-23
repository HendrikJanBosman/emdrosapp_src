#!/usr/bin/python
from emdros_application import *

DO_REF = True
DO_OUT = True
DO_LBL = False

class MQLCommandTool(EmdrosApplication):

    def __init__(self, options, title=''):

	# initialize superclass
	EmdrosApplication.__init__(self, options, title,
				   DO_REF=True, DO_OUT=True, DO_LBL=False)

	if not self.auto:
	    writeln('MQLCommandTool by Hendrik Jan Bosman (Emdros version %s)' % self.mql.EmdrosVersion, outstream=sys.stderr)


	# add init stuff for MainObject.
	
	self.local_fmt = self.options.get('format')
	self.filter_focus = True
	if not self.auto:
	    self.writeln("\nfilter focus is on, enter 'filter off' to turn off", outstream=sys.stderr)


	if self.options.getArgs():
	    self.last_query = self.loadQueryFile(self.options.getArgs()[0])
	else:
	    if self.auto:
		self.last_query = None
	    else:
		self.last_query = 'SELECT ALL OBJECTS WHERE\n\nGO'
	self.last_failed = ""
	self.last_sheaf = None
	self.last_table = None
	 
	if title == None:
	    title = repr(self)
	if options.get('gui'):
	    self.gui = GUI(title=title)
	    self.gui.app = self
	    self.gui.mainloop()
	else:
	    self.gui = None


    def quit(self):
	exit()

    def __repr__(self):
	return('MQLCommandTool by Hendrik Jan Bosman (Emdros version %s)' % self.mql.EmdrosVersion)

    def next(self):
	mql = self.mql
	ref = self.ref
	out = self.out

	self.writeln("", outstream=sys.stderr)
	writeln("enter command ('e[dit]' to write a query, '?' for help)", outstream=sys.stderr)
	q = userInput(">")
	if q == '':
	    if self.gui:
		q = self.last_query
	    else:
		self.writeln('current query:\n\n%s' % self.last_query, outstream=sys.stderr)
		if userAffirms('execute it?'):
		    q = self.last_query

	if q in self.cfg.get_multi('exit_phrase'):
	    return True # DONE

	elif re.match("format[ \t]*=?[ \t]*", q):
	    q = re.sub("format[ \t]*=?[ \t]*", "", q)
	    q = re.sub("[ \t]*$", "", q)
	    self.writeln('change format to: "%s"' % q, outstream=sys.stderr)
	    try:
		self.setFormat(q)
		self.local_fmt = q
	    except:
		if q in ('mql', 'MQL', 'mqlc', 'MQLc', 'cons', 'xml', 'XML', 'csv'):
		    self.local_fmt = q.lower()
		else:
		    self.writeln('not valid, ignored.', outstream=sys.stderr)
		 
	elif re.match("mode[ \t]*=[ \t]*", q):
	    q = re.sub("mode[ \t]*=[ \t]*", "", q)
	    q = re.sub("[ \t]*$", "", q)
	    self.writeln('change mode to: "%s"' % q, outstream=sys.stderr)
	    try:
		self.setMode(q)
		q = self.last_query
	    except:
		self.writeln(sys.exc_info()[1], outstream=sys.stderr)
		self.writeln("mode not valid, ignored.", outstream=sys.stderr)

	elif re.match("load[ \t]+", q):
	    q = re.sub("load[ \t]*", "", q)
	    self.last_query = self.loadQueryFile(q)

	elif re.match("save[ \t]", q):
	    filename = re.sub("save[ \t]*", "", q)
	    filename = re.sub("[ \t]*$", "", filename)
	    with open(filename, 'w') as tmp:
		self.writeln('saving sheaf to %s' % filename, outstream=sys.stderr)
		if self.format == 'latex':
		    MAINDOC = userAffirms('output a main document?')
		    if MAINDOC:
			tmp.write('\\documentclass[a4,12pt]{article}\n')
			tmp.write('\\usepackage{palatino}\n')
			tmp.write('\\begin{document}\n')
		    tmp.write('\\begin{verbatim}\n')
		tmp.write(self.last_query + '\n')
		if self.format == 'latex':
		    tmp.write('\end{verbatim}\n')
		tmp.write('\n' + self.sheafRepr(self.last_sheaf) + '\n')
		if self.format == 'latex' and MAINDOC:
			tmp.write('\\end{document}\n')

	elif re.match('filter[ \t]*on', q):
	    self.writeln("filter is on: only focused objects returned in the sheaf\n('filter off' to turn off)", outstream=sys.stderr)
	    self.filter_focus = True

	elif re.match('filter[ \t]*off', q):
	    self.writeln("filter is off: entire sheaf is retrieved\n('filter on' to turn on)", outstream=sys.stderr)
	    self.filter_focus = False

	elif re.match('\?', q):
	    self.printHelp()

	elif re.match('edit[ \t][ \t]*failed', q):
	    self.last_query = editString(self.last_failed)

	elif q in ('e', 'edit', '!v'):
	    self.last_query = editString(self.last_query)

	elif q is not '':
	    self.doQuery(q, mql)
	return False # DONE = False
	

    def doQuery(self, q, mql):
	    if mql.doQuery(q):
		self.last_query = q
		if mql.isTable():
		    self.last_table = mql.getPyTable()
		    self.writeln(self.out.byPyTable(self.last_table), outstream=sys.stderr)
		elif mql.isSheaf():
		    self.last_sheaf = mql.getPySheaf(filterFocus=self.filter_focus)
		    if self.local_fmt == 'cons':
			mql.showConsoleOutput()
		    if self.local_fmt == 'csv':
			print self.last_sheaf.toCSV()
		    else:
			self.writeln(self.sheafRepr(self.last_sheaf), outstream=sys.stderr)
		elif mql.isFlatSheaf():
		    self.last_sheaf = mql.getPyFlatSheaf()
		    if self.local_fmt == 'cons':
			mql.showConsoleOutput()
		    else:
			self.writeln(self.sheafRepr(self.last_sheaf), outstream=sys.stderr)
		else:
		    self.writeln('%s\nquery result can not be displayed.' % q, outstream=sys.stderr)
	    else:
		self.writeln('query could not be executed.', outstream=sys.stderr)
		self.last_failed = q




    def sheafRepr(self, sheaf):

	if sheaf is None:
	    return 'query could not be executed'

	if sheaf.isEmpty():
	    ret_val = 'no solutions'
	else:
	    if self.local_fmt == 'csv':
		ret_val = sheaf.toCSV(do_header=True)
	    else:
		i = 0
		ret_val = '' 
		for straw in sheaf:
		    i += 1
		    if self.local_fmt not in ('xml', 'mql', 'mqlc', 'csv'):
			if self.format == 'latex':
			    ret_val += '\\noindent\n'
			ret_val += 'solution no %d:' % i
			if self.format == 'latex':
			    ret_val += '\\\\'
			ret_val += '\n'
		    for obj in straw:
			if self.local_fmt not in ('cvs', 'mql', 'xml', 'mqlc'):
			    ret_val += self.ref.byObject(obj) + ' '
			ret_val += self.out.byPyObject(obj,
			                          format=self.local_fmt) + '\n'
	return ret_val


    def printHelp(self):
	self.writeln("", outstream=sys.stderr)
	self.writeln('commands:', outstream=sys.stderr)
	self.writeln('---------------', outstream=sys.stderr)
	self.writeln('<empty line>      : execute current query', outstream=sys.stderr)
	self.writeln('e[dit]            : edit current query', outstream=sys.stderr)
	self.writeln('edit failed       : edit last failed query', outstream=sys.stderr)
	self.writeln('load <file_name>  : load query from file', outstream=sys.stderr)
	self.writeln('save <file_name>  : save current results to file', outstream=sys.stderr)
	self.writeln('filter on | off   : toggle focus filter', outstream=sys.stderr)
	self.writeln('mode   = <mode>   : set linguistic mode %s' % repr(self.modes), outstream=sys.stderr)
	self.writeln("format = <format> : set output format %s" % repr(self.formats + ('mql', 'xml', 'csv')), outstream=sys.stderr)
	self.writeln('quit, bye, etc.   : quit', outstream=sys.stderr)
	self.writeln('?                 : show this message', outstream=sys.stderr)

    def main(self):
	mql = self.mql
	ref = self.ref
	out = self.out

	if self.auto:
	    if self.last_query is not None:
		self.doQuery(self.last_query, mql)
	    else:
		q = ""
		for l in sys.stdin:
		    q += l
		self.doQuery(q, mql)
	else:
	    DONE = False
	    while not DONE:
		DONE = self.next()


    def loadQueryFile(self, q):
	try:
	    tmp = open(q, 'r')
	except:
	   self.writeln('could not open MQL file %s, ignored.' % q, outstream=sys.stderr)
	   return None

	lines = tmp.readlines()
	tmp.close()
	query = ''
	for l in lines:
	    query += l
	self.writeln('loaded query from MQL file %s (<Enter> to execute)' % q, outstream=sys.stderr)
	return query

	

	    
if __name__ == '__main__':
    options = Options()
    mct = MQLCommandTool(options=options)
    mct.main()
