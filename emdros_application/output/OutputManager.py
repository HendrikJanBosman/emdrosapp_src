import sys
import importlib
from emdros_application.mql_engine.MQLEngine import *


class OutputManager:
    
    def __init__(self, mql, cfg, mode=None, format=None, json=None,
		       outstream=None, msgstream=None, widget=None, 
		       verbose=False, VERBOSE=False, kernel=None):

        if kernel is None:
            kernel = importlib.import_module('emdros_application.config')

	self.verbose = verbose
	self.VERBOSE = VERBOSE

	self.json = json  # if specified, it is the ONLY json file used
			  
	self.mql = mql
	self.cfg = cfg

	self.matrix = self.setupMatrix(self.cfg, kernel=kernel)

	if mode == None: 
	    self.mode = self.cfg.get('mode')
	else:
	    self.mode = mode

	if format == None:
	    self.format = self.cfg.get('format')
	else:
	    self.format = format


	# init streams and widgets

	if outstream == None:
	    self.outstream = sys.stdout
	else:
	    self.outstream = outstream

	if msgstream == None:
	    self.msgstream = sys.stderr
	else:
	    self.msgstream = msgstream
	
	self.widget = widget

    def __repr__(self):
	rep = ""
	for mode in self.matrix.keys():
	    rep += '\n' + underlined(mode) + '\n'

	    rep += 'modecfg: %s\n' % self.matrix[mode]['modecfg']
	    for format in self.matrix[mode].keys():
		if format <> 'modecfg':
		    rep += '%s: %s\n' % (format, 
					 self.matrix[mode][format]['json'])

	rep += "current mode  : %s\n" % self.mode
	rep += "current format: %s\n" % self.format
	return rep


    def setupMatrix(self, cfg, kernel, withJSON=True):
	matrix = {}
	db = self.cfg.get('database')
	modes = self.cfg.get_multi('modes')
	formats = self.cfg.get_multi('formats')
	self.modes = modes
	self.formats = formats
	for m in modes:
	    if m is None: continue
	    matrix[m] = {}
	    mcfg = addPathAndExt(cfg.get('modecfg', m), kernel.CFG_DIR, kernel.CFG_EXT)
	    matrix[m]['modecfg'] = mcfg
	    modecfg = Configuration(mcfg, kernel=kernel)
	    if withJSON:
		for f in formats:
		    matrix[m][f] = {}
		    if self.json:
			jsonfile = self.json
		    else:
			jsonfile = modecfg.get('jsonfile', f)
		    if jsonfile is None:    # NOV 10 2018
			matrix[m][f] = None
			continue
		    jsonfile = addPathAndExt(jsonfile, kernel.JSON_DIR, kernel.JSON_EXT)

		    matrix[m][f]['json'] = jsonfile
		    JSONval = EmdrosPy.readAndParseJSONFromFile(jsonfile)
			
		    if type(JSONval) == str:
			exitOnError('\nproblem in %s:\n%s' % (jsonfile, JSONval))
			warning('problem reading %s.' % jsonfile)
			matrix[m][f]['rO'] = None
		    else:
			try:
			     matrix[m][f]['rO'] = \
				 RenderObjects(self.mql.env, db, JSONval[0], "base")
			except:
			    raise Exception('problem initiating RenderObjects')
			    matrix[m][f]['rO'] = None

		    if self.verbose:
			writeln("output manager (%s, %s) from %s: OK" % \
			    (m, f, jsonfile))
	return matrix


    def dump(self, outstream=None):
	writeln("database   : %s" % self.mql.database, outstream=outstream)
	writeln("modes      : %s" % repr(self.modes), outstream=outstream)
	writeln("formats    : %s" % repr(self.formats), outstream=outstream)
	for m in self.modes:
	    writeln(underlined(m))
	    for f in self.formats:
		writeln('%s:' % f, outstream=outstream)
		writeln(self.matrix[m][f]['json'], outstream=outstream)
		writeln(self.matrix[m][f]['rO'], outstream=outstream)
		writeln('', outstream=outstream)


    #### USER INTERFACE ######

    def setMode(self, mode):
	if mode in self.modes:
	    self.mode = mode
	else:
	    raise Exception("invalid mode '%s' %s"%(mode,repr(self.modes)))


    def setFormat(self, format):
	if format in self.formats:
	    self.format = format
	else:
	    raise Exception("invalid format %s %s"%(format,repr(self.formats)))


######### THE ACTUAL OUTPUT METHODS ########################

    def reprMonads(self, monads, mode=None, format=None):

	if mode==None: mode = self.mode
	if format==None: format = self.format
	rO = self.matrix[mode][format]['rO']
	if rO <>  None:
	    rO.clean()
	    rO.process(monads.first(), monads.last())
	    r = rO.getDocument()
	    return r
	else:
	    return '<None>'

    def byMonads(self, monads, mode=None, format=None):
	return self.reprMonads(monads, mode=mode, format=format)

    def reprPyObject(self, obj, mode=None, format=None, filterFocus=False):
	if not filterFocus:
	    return self.reprMonads(obj.monads, mode, format)
	else:
	    tmpSheaf = PySheaf()
	    #import pdb; pdb.set_trace()
	    tmpSheaf.append(obj)
	    return self.reprPySheaf(tmpSheaf.filterFocus(), mode=mode, format=format)

    def byPyObject(self, obj, mode=None, format=None, filterFocus=False):
	if mode is None:
	    mode = self.mode
	if format is None:
	    format = self.format

	if   format.lower() == 'csv':
	    return obj.toCSV()
	elif format.lower() == 'mql':
	    return obj.toMQL()
	elif format.lower() == 'mqlc':
	    return obj.toMQL(create=True)
	elif format.lower() == 'xml':
	    return obj.toXML()
	else:
	    return self.reprPyObject(obj, mode=mode, format=format,
						    filterFocus=filterFocus)

    def byObject(self, obj, mode=None, format=None, filterFocus=False):
	if mode is None:    mode = self.mode
	if format is None: format = self.format
	if isinstance(obj, EmdrosPy.MatchedObject):
	    obj = PyObject(obj)
	return self.reprPyObject(obj, mode=mode, format=format,
						    filterFocus=filterFocus)

    def reprPySheaf(self, sheaf, mode=None, format=None, filterFocus=False):
	if filterFocus:
	    sheaf = sheaf.filterFocus()
	if format == 'csv':
	    return sheaf.toCSV()
	return self.reprMonads(sheaf.monads, mode=mode, format=format)

    def byPySheaf(self, sheaf, mode=None, format=None, filterFocus=False):
	if format in ('MQL', 'mql'):
	    return sheaf.toMQL()
	elif format in ('MQLc', 'mqlc'):
	    return sheaf.toMQL(create=True)
	elif format in ('XML', 'xml'):
	    return sheaf.__repr__()
	else:
	    return self.reprPySheaf(sheaf, mode=mode, format=format,
						    filterFocus=filterFocus)


    def byPyTable(self, table, format=None):
	if format == None:
	    format = self.format
	if format == 'latex':
	    return self.latexPyTable(table)
	else:
	    return repr(table)

    def latexPyTable(self, table):
	if len(table) == 0:
	    return ""

	r = "\\begin{longtable}{|"
	for c in table[0]:
	    r += "c|"
	r += "}\n\\hline\n"

	for row in table:
	   for cell in row[:-1]:
	       r += cell + ' & '
	   r += row[-1] + '\\\\\n'
	r += '\\hline\n'
	r += '\\end{longtable}'
	return re.sub("_", "\\_", r)

    def reprResult(self, mql=None, mode=None, format=None, filterFocus=False):
	if mql == None: mql = self.mql
	if mql.isTable():
	    return repr(mql.getPyTable())
	else:
	    return self.reprPySheaf(mql.getPySheaf(), mode, format, filterFocus)


    def byResult(self, sheaf, mql=None, mode=None, format=None, filterFocus=False):
	return self.reprPySheaf(sheaf, mql=mql, mode=mode, format=format,
						    filterFocus=filterFocus)

    def LaTeXHeader(self, commented=False):
	if commented:
	    comm = "%%"
	else:
	    comm = ''
	ret =  "%s\\documentclass[12pt]{book}\n" % comm
	ret += "%s\\usepackage{palatino}\n" % comm
	ret += "%s\\usepackage{a4}\n" % comm
	ret += "%s\\usepackage{dsea12}\n" % comm
	ret += "%s\\usepackage{hjbabbr}\n" % comm
	ret += "%s\\usepackage{longtable}\n" % comm
	ret += "%s\\usepackage{lscape}\n" % comm
	ret += "%s\\usepackage{multicol}\n" % comm
	ret += "%s\\begin{document}\n" % comm
	return ret
	
    def LaTeXTail(self, commented=False):
	if commented:
	    comm = "%%"
	else:
	    comm = ''
	ret = "%s\\end{document}\n" % comm
	return ret

