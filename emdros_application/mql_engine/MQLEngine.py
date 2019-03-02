# -*- coding: utf-8 -*-
from re import *
import sys
import EmdrosPy
from emdros_application import *
from PySheaf import *
from PyTable import *

DEFAULT_KERNEL_CFG = 'emdros_application.config'

class MQLEngine:

   def __init__(self, database=None, usr=None, pwd=None, be=None, 
		      domainfile=None, domain=None,
		      VERBOSE=False, verbose=False, test=False, 
		      outstream=sys.stdout, errstream=sys.stderr,
                      kernel=None):
    
      if kernel is None:
         import importlib
         kernel = importlib.import_module('config')

      # INIT VARIABLES

      self.outstream = outstream
      self.errstream = errstream
      self.test   = test

      if be is None:
         be = kernel.backends.index(kernel.DEFAULT_BACKEND)

      if database is not None:
         db = database
      else:
         try:
            db = kernel.DEFAULT_DATABASE
         except:
            db = None
      if db is None:
         db = userInput('database: ')

      if be in (EmdrosPy.kSQLite2, EmdrosPy.kSQLite3):
	 db = addPath(db, kernel.DATA_DIR)
      self.database = db
      self.db = self.database # spelling variant for sloppy programmers
      try:
         usr = kernel.DEFAULT_USR
      except:
         usr = None
      if usr is None and be not in (EmdrosPy.kSQLite2, EmdrosPy.kSQLite3):
	 usr = userInput("user name:")
         
      try:
         pwd = kernel.DEFAULT_PWD
      except:
        pwd = None
      if pwd is None and be not in (EmdrosPy.kSQLite2, EmdrosPy.kSQLite3):
	 pwd = userInput("password for %s:" % u, outstream=self.errstream)
  
      self.VERBOSE = VERBOSE
      self.verbose = verbose

      if self.verbose:
	 writeln('backend: %s' % be, outstream=sys.stderr)
	 writeln('database: %s' % db, outstream=sys.stderr)
	 writeln('usr: %s' % usr, outstream=sys.stderr)
	 writeln('pwd: %s' % pwd, outstream=sys.stderr)
	
      ############ INSTANTIATE EMDROSENV ######################
      self.env = EmdrosPy.EmdrosEnv(EmdrosPy.kOKConsole,
                          EmdrosPy.kCSISO_8859_8,
                          "localhost",
                          usr, pwd, db, be)
      if self.env is None or \
	     self.env is EmdrosPy.NIL or not self.env.connectionOk():
	 raise Exception('EmdrosEnv for %s could not be initiated'%self.database)
      else:
	 self.EmdrosVersion = self.getEmdrosVersion(as_float = False)
         self.EmdrosVersion_float = self.getEmdrosVersion(as_float=True)
	 if self.verbose:
	    writeln('EmdrosEnv (Emdros version %s) initiated for %s' % (self.EmdrosVersion, self.database),
	    outstream=self.errstream)


      self.domain = None # initialize in order for readDomainFile to work
      if domain is not None:
	 self.domain = domain
      elif domainfile is not None:
	 self.domain = self.readDomainFile(addPathAndExt(domainfile,
							 kernel.DOMAINS_DIR,
                                                         kernel.MQL_EXT))
      else:
	 self.domain = None    # selects the entire database

      if self.VERBOSE:
	 writeln("Domain for queries: %s" % self.domain,
		     outstream=self.errstream)

   def getEmdrosVersion(self, as_float=False):
      v_str = self.env.getEmdrosVersion()
      if as_float:
	 v_str = re.sub("\.", "", v_str)
	 v_str= re.sub("pre", "", v_str)
	 return float(v_str)
      else:
	 return v_str


   def setDomain(self, som):
      if type(som) != str:
	  som = som.toString()
      self.domain = som
      if self.verbose:
	 writeln("working corpus is %s" % som, outstream=self.errstream)


   def matchFocusQuery(self, query, inner_domain, label=None):

	import Query
	if type(inner_domain) == str:
	    in_dom = inner_domain
	else:
	    in_dom = self.monadsToString(inner_domain)
	

	in_dom = re.sub("[ \t]", "", in_dom)
	q = Query.Query(query, domain = in_dom)


	# retrieve the monads of the outermost enveloping object
	q.subToken("SELECT", "GET", q.select_clause)
	q.delToken("WHERE", q.select_clause)
	q.delToken("ALL", q.select_clause)
	q.subToken("IN", "HAVING MONADS IN", q.select_clause)

	q.topograph = q.topograph[:2]
	q.topograph.append(']')


	if not self.doQuery(repr(q)) : # or not self.solutionFound(): # 2018-09-09
	    return False
	else:
	    py_sheaf = PySheaf(self.getFlatSheaf())
	    out_dom = re.sub("[ \t]", "", py_sheaf.monads.toString())


	    if not self.doQuery(query, domain=out_dom):
		return False
	    else:
		sheaf = self.getPySheaf().filterFocus()
		for straw in sheaf:
		    for obj in straw:
			obj_mon = re.sub("[ \t]", "", obj.monads.toString()) 
			if obj_mon == in_dom:
			    return True
		return False



   def getPySheafFromQuery(self, query, spin=None):
      if self.doQuery(query):
         if re.search("[ \t\n][Ff][Oo][Cc][Uu][Ss][ \t\n\]]", query):
            return self.getPySheaf(spin).filterFocus()
         else:
            return self.getPySheaf(spin)
      else:
         return None


   def getPySheaf(self, filterFocus=False, PyMonads=False, spin=None):
      if self.isSheaf():
	 if filterFocus and \
		re.search("[ \t\n][Ff][Oo][Cc][Uu][Ss][ \t\n\]]",
							     self.latestQuery):
	    return PySheaf(self.getSheaf(), PyMonads, spin=spin).filterFocus()
	 else:
	    return PySheaf(self.getSheaf(), PyMonads, spin=spin)
      else:
	 if self.verbose:
	    writeln('no sheaf in MQL.getPySheaf', outstream=self.errstream)
	 return None

	 
   def isRetrievalQuery(self, q):
      return re.search("[sS][eE][lL][eE][cC][tT]", q)


   def doQuery(self, query, domain=None, VERBOSE=None, verbose=None, showErr=True, test=None):
      if VERBOSE is None: VERBOSE = self.VERBOSE
      if verbose is None: verbose = self.verbose

      if test is None: test = self.test
      if test and self.isRetrievalQuery(query):
	 test = False

      if domain is None:
	 dom = self.domain #dom = self.monadsToString(self.domain)
      else:
	 if type(domain) == str:
	    dom = domain
	 else:
	     dom = self.monadsToString(domain)


      if dom not in ("all", None):
	     query = sub("[Oo][Bb][Jj][Ee][Cc][Tt][Ss][ \t\n]*\[",
		  "OBJECTS IN " + dom + " [", query)
	     query = sub("[Oo][Bb][Jj][Ee][Cc][Tt][Ss][ \t\n]*[Ww][Hh][Ee][Rr][Ee]",
		  "OBJECTS IN " + dom + " WHERE", query)

      if not test:
	 if VERBOSE:
	    writeln(query, outstream=self.errstream)
	 dummyBool = False
	 out = self.env.executeString(query, dummyBool, VERBOSE, showErr)
	 self.latestQuery = query
	 return out[0] and out[1]
      else:
	 if verbose:
	    writeln('\n<test mode, not executed>', outstream=self.errstream)
	    writeln(query, outstream=self.errstream)
	 return True


   def getCompilerError(self):
      return self.env.getCompilerError()

   
   def getDBError(self):
      return self.env.getDBError()


   def getAllErrors(self):
      e = self.env.getCompilerError()
      if e is not '':
         e += '\n'
      e += self.getDBError()
      return e

      
   def isSheaf(self):
      return self.env.isSheaf()


   def solutionFound(self):
      if self.isSheaf():
         return ((self.getSheaf()).isFail() == False)
      elif self.isTable():
         return True
      else:
         return False
      
   def isFlatSheaf(self):
      return self.env.isFlatSheaf()

   def isTable(self):
      return self.env.isTable()

   def getSheaf(self):
      if self.env.isSheaf():
         return self.env.getSheaf()
      else:
         return None

   def getFlatSheaf(self):
      if self.env.isFlatSheaf():
         return self.env.getFlatSheaf()
      else:
         return None

   def getFlatPySheaf(self, PyMonads=False):
      return self.getPyFlatSheaf()

   def getPyFlatSheaf(self, PyMonads=False):
      return PySheaf(self.getFlatSheaf(), PyMonads)

   def getTable(self):
      if self.isTable():
         return self.env.getTable()
      else:
         return None

   def getPyTable(self):
      return PyTable(self.getTable())

   def getResult(self, widget=None):
      if self.env.isTable():
         return PyTable(self.env.getTable())
      elif self.env.isSheaf():
         return PySheaf(self.env.getSheaf())
      else:
         return None

   def showConsoleOutput(self, outstream=sys.stderr):
      # THIS CRASHES: APPARENTLY, THE OUTPUTSTREAM IS THE PROBLEM
      pOut = EmdrosPy.EMdFOutput(EmdrosPy.kCSISO_8859_8, outstream,
                                 EmdrosPy.kOKConsole, 0)
      self.env.getResult().out(pOut)

   def showResult(self, widget=None):
      if self.env.isTable():
         self.showTable(self.getResult(), widget)
      elif self.env.isSheaf():
         self.showSheaf(self.getResult(), widget)
      else:
         if widget is None:
            writeln('query did not yield a result.', outstream=self.errstream)
         else:
            widget.insert("end", 'query did not yield a result.\n', outstream=self.errstream)

   def showTable(self, table, widget=None):
      if widget is None:
         writeln(repr(table), outstream=self.errstream)
      else:
         widget.delete("1.0", "end")
         widget.insert(repr(table) + '\n')

   def showSheaf(self,sheaf, widget=None):
      if widget is None:
         writeln(repr(sheaf), outstream=self.errstream)
      else:
         widget.insert(repr(sheaf) + '\n')
   
   def getResultMonads(self):
      if self.env.isSheaf():
         return(self.env.getSheaf().getSOM(False))
      else:
         return None

   def reprByMonads(self, m, rO=None):
      if rO is None: 
	 rO = self.rO
      rO.clean()
      rO.process(m.first(), m.last())
      r = rO.getDocument()
      return self.__postprocess(r)


   def displayMonads(self, m, rO=None):
         rS = ''
         mi = m.const_iterator()
         while mi.hasNext():
            s = self.reprByMonads(mi.next(), rO=rO) + '\n'
            rS += s
         return rS
       
   def postEdit(self, s):
      ## QUICK AND DIRTY HACK, SHOULD BE DONE IN EXTERNAL CFG FILE ##
      s = sub('\[ ', '[', s)
      s = sub(' \]', ']', s)
      return s
      
   def getResultString(self, rO=None, rasterized=False):
      s = self.env.getSheaf()
      if s is None or s.isFail():
         return self.env.getDBError() + '\n' + self.env.getCompilerError()
      else:
         m = s.getSOM(False)
         if rasterized:
            r = re.split("\n", self.displayMonads(m, rO=rO))
         else:
            r = self.displayMonads(m, rO=rO)
         return self.postEdit(r)
         
      
   def displayResult(self, rO=None, widget=None, outstream=None):
      if outstream is None:
	 outstream = self.errstream
      if widget is None:
         writeln(self.getResultString(rO=rO), outstream=outstream)
      else:
         widget.insert("end", self.getResultString(rO=rO) + '\n')      

    
   def readDomainFile_OLD(self, filename):
      if filename is not None:
	  try:
	     lines = open(filename, "r").readlines()
	  except:
	     warning('no domain query file %s' % filename)
	     return "{0}"
	  q = ""
	  for l in lines:
	      q += l
	  if self.doQuery(q, VERBOSE=self.VERBOSE, verbose=self.verbose):
	      return self.getSheaf().getSOM(False).toString()
          else:
	      warning("query in %s does not yield a domain" % filename)
	      return "{0}"

   def readDomainFile(self, filename):
      import QueryList
      som = SetOfMonads()
      for q in QueryList.QueryList(filename):
	 if self.doQuery(repr(q), VERBOSE=self.VERBOSE, verbose=self.verbose):
	    som.unionWith(self.getSheaf().getSOM(False))
      return som.toString()


   def duplicatesExist(self, PyObj, defining_features=[]):
      ##### defining_features is a list of features which, i 
      #import pdb; pdb.set_trace()
      otype  = PyObj.otype
      monads = PyObj.monads.toString()
      id_d   = PyObj.id_d
      idd_list = []

      q = "SELECT ALL OBJECTS IN %s WHERE [%s FIRST AND LAST (NOT self = %i)\n" %\
	       (monads, otype, id_d)
      for f in defining_features:
	 val = PyObj[f]
	 if type(val) == int: val = str(val)
	 q += 'AND %s = %s\n' % (f, val)
      q += "] GO"
      if self.doQuery(q) and self.solutionFound():
         #import pdb; pdb.set_trace()
	 for straw in self.getPySheaf():
	    for o in straw:
	       idd_list.append(o.id_d)
      return idd_list


   def storeObject(self, pyObject, recursive=False,
		   delDuplicates=True, defining_features=[],
		   mode=None, labels=None):
      def doVal(v):
	 if type(v) == str:
	    return v
	    #return '"%s"' % v
	 if type(v) == int:
	    return '%i' % v
	 else:
	    return str(v)

      otyp   = pyObject.otype
      monads = pyObject.monads.toString()
      

      q = "CREATE OBJECT FROM MONADS = %s [%s " % (monads, otyp)
      #if MQL_VERSION < 3.7:
      if self.EmdrosVersion_float < 3.7:
          q += " first_monad := %d;" % pyObject.monads.first()
          q += " last_monad := %d;" % pyObject.monads.last()
      for f in pyObject.features.keys():
	 q += " %s := %s;"% (f, pyObject.featureStrings[f])
	 #val = pyObject.features[f]
	 #if not search('_labels', f):
	 #if f != 'label' :
	    #val = doVal(val)
	 #q += " %s := %s;" % (f, val)
      q += "] GO"
      if not self.doQuery(q):
	 return None
      else:
	 id_d = self.getPyTable().getColumn(0)[0]  
	 pyObject.id_d = id_d
	 if delDuplicates:
	    f_list = []
	    dups = self.duplicatesExist(pyObject, defining_features)
	    if dups != []:
	       #import pdb; pdb.set_trace()
	       for d in dups:
		  if self.verbose:
		     writeln('deleting duplicate %s %d at %s' % \
			     (pyObject.otype, d, pyObject.monads.toString()))
		  self.deleteObject(otype=pyObject.otype, id_d=d)
	
	 if recursive:
	    for straw in pyObject.sheaf:
	       for o in straw:
		  self.storeObject(o, recursive=True)

	 return id_d
         

   def createObject(self, otype, monads, mode=None, labels=None):
    
	if not self.objectTypeExists(otype):
	    self.createObjectType(otype, mode=mode, labels=labels)

	if type(monads) != str:  # monads is a real SetOfMonads
	    m = monads.toString()
	else: # monads is a string
	    raise Exception("string '%s' passed to MQLEngine.createObject(), should be SetOfMonads" % monads)

	q = "CREATE OBJECT FROM MONADS = %s [%s " % (m, otype)
        #if MQL_VERSION < 3.7:
        if self.EmdrosVersion_float < 3.7:
            q += " first_monad := %d;" % monads.first()
            q += " last_monad  := %d; " % monads.last()
	if mode is not None and labels is not None and len(labels) > 0:
	    lbltype = "%s_labels" % (mode)
	    q += lbltype + " := (%s" % labels[0]
	    for l in labels[1:]:
		q += ",%s" % l
	    q += ");"
	q += "] GO"
	try:
	    success = self.doQuery(q)
	except:
	    success = False
	if success:
	    id_d = int(self.getPyTable().getColumn(0)[0])
	    return PyObject(otype=otype, id_d=id_d, monads=monads)
	else:
	    raise Exception("MQLEngine.createObject(%s, %s), query %s failed" % (otype, m, q))


   def updateObject(self, PyObj):
      q  = "UPDATE OBJECT BY ID_D = %d\n" % PyObj.id_d
      q += "[%s\n" % PyObj.otype
      for f in PyObj.features.keys():
	 q += "%s := %s;\n" % (f, PyObj.featureStrings[f])
      q += "] GO"
      self.doQuery(q)
	 

   def deleteObject(self, PyObj=None, otype=None, id_d=None):
	if PyObj is not None:
	    q = "DELETE OBJECT BY ID_D = %i [%s] GO" % (PyObj.id_d, PyObj.otype)
	else:
	    q = "DELETE OBJECT BY ID_D = %i [%s] GO" % (id_d, otype)
	return self.doQuery(q)

   def deleteObjectsFrom(self, otyp, domain):
      q = "SELECT ALL OBJECTS WHERE [%s] GO" % otyp
      self.doQuery(q, domain=domain)
      sheaf = self.getPySheaf()
      for straw in sheaf:
	 for obj in straw:
	    if self.verbose:
		writeln('deleting [%s id_d=%d] at %s' % (otyp, obj.id_d, obj.monads.toString()))
	    self.deleteObject(obj)
   #################### EXTRA FUNCTIONALITIES ###############

   def monadsToString(self, monads):
      t = repr(type(monads))
      if t in ("<class 'EmdrosPy.SetOfMonads'>", "<type 'instance'>"):
	 if monads.isEmpty():
	    return '{0-0}'
	 return monads.toString()
      elif t == "<type str>":
	 return t
      else:
	 return None

    
   def getObjectTypeRaster(self, otype, domain, features=None, strict=True):
	if domain is None:
	    dom = self.monadsToString(self.domain)
	else:
	   dom = self.monadsToString(domain)
	q = "SELECT ALL OBJECTS "
	if domain is not None:
	    if not strict: 
		q += "HAVING MONADS "
	    q += "IN %s " % dom
	q += "WHERE [%s " % otype
	if features:
	    q += "get %s" % features[0]
	    for f in features[1:]:
		q += ", %s" % f
	q += "] GO"
	self.doQuery(q)
	sh = self.getPySheaf()
	raster = []
	for straw in sh:
	    for obj in straw:
		raster.append(obj)
	return raster



############ FREQUENTLY USED DATABASE OPERATIONS ###########

   def objectTypeExists(self, otype, domain=None):

      if not self.doQuery ("SELECT OBJECT TYPES GO"):
	 return False
      else:
	 table = self.getPyTable()
	 return otype in table.getColumn(0)


   def objectsExist(self, otype, domain=None):

      if not self.objectTypeExists(otype):
	 warning("MQLEngine.objectsExist(): obj type [%d] does not exist" % otype)
	 return False

      if domain is not None:
	  domain = self.monadsToString(domain)
	  return self.doQuery("SELECT ALL OBJECTS WHERE [%s] GO" % otype, domain=domain) \
	    and self.solutionFound()


   def monadSetExists(self, m):
      if not self.doQuery ("SELECT MONAD SETS GO"):
	 return False
      else:
	 return m in self.getPyTable().getColumn(0)

   def objectFeatureExists(self, otype, f):
      #if not self.objectTypeExists(otype):   # HJB
	    #self.createObjectType(otype)
	    #return False
      if not self.doQuery("SELECT FEATURES FROM OBJECT TYPE [%s] GO" % otype):
	  return None
      else:
	  table = self.getPyTable()
	  if f in table.getColumn(0):
	    return table.getColumn(1)[table.getColumn(0).index(f)]

   def enumExists(self, enum):
      self.doQuery ("SELECT ENUMERATIONS GO")
      return enum in self.getPyTable().getColumn(0)

   def enumValueExists(self, enum, val):
        if self.enumExists(enum):
            self.doQuery("SELECT ENUM CONSTANTS FROM ENUM %s GO" % enum)
            return val in self.getPyTable().getColumn(0)
        else:
            return False

   def objTypeHasLabel(self, mode, otype, label):
      return self.enumValueExists("%s_%s_label_t" % (mode, otype), label)
   
   def labelTypeExists(self, mode, otype):
      return self.enumExists("%s_%s_label_t" % (mode, otype))


   def createObjectType(self, otype, mode=None, labels=None, forced=False):

      if forced and self.objectTypeExists(otype):
	    self.dropObjectType(otype)

      if mode is not None:
	 if not self.enumExists("%s_%s_label_t" % (mode, otype)):
	    if labels is None:
		self.createEnum("%s_%s_label_t" % (mode, otype), ("None",))
	    else:
		self.createEnum("%s_%s_label_t" % (mode, otype), labels)

      if self.verbose:
	 writeln('creating object type [%s]' % otype)
      q = 'CREATE OBJECT TYPE IF NOT EXISTS [%s ' % otype
      if mode is not None:
	 q += "%s_labels : list of %s_%s_label_t; " % (mode, mode, otype)
      #if MQL_VERSION < 3.7:
      if self.EmdrosVersion_float < 3.7:
          q += 'first_monad: integer; last_monad: integer; '
      q += 'note: string;] GO'
      success = self.doQuery(q)
      return success


   def objectExists(self, otype, monads):
      try:
	 mon = monads.toString()
      except:
	 mon = monads
      q = "SELECT ALL OBJECTS IN %s WHERE [%s] GO" % (mon, otype)
      if not self.doQuery(q):
	 return False
      else:
	 return len(self.getPySheaf()) > 1


   def dropObjectType(self, otype, VERBOSE=False):
      if self.objectTypeExists(otype):
	  if self.verbose:
	    writeln('dropping object type [%s]' % otype)
	  return self.doQuery('DROP OBJECT TYPE [%s] GO' % otype)
      else:
	 return True

   def dropObjectsFromDomain(self, otype, domain=None):
      if domain is None:
	 domain = self.domain
      domain = self.monadsToString(domain)

      q = "SELECT ALL OBJECTS WHERE [%s] GO" % (otype)
      if self.doQuery(q, domain=domain) and self.solutionFound():
	 del_list = []
	 for straw in self.getPySheaf():
	    for obj in straw:
	       del_list.append(obj.id_d)
	 if del_list:
	    q = "DELETE OBJECTS BY ID_D = %d" % del_list[0]
	    for d in del_list[1:]:
	       q += ", %d" % d
	    q += "[%s] GO" % otype
	    if self.verbose:
		msg = "deleting all [%s] objects from " % otype
		if domain is None:
		    msg += "the entire database %s" % self.database
		else:
		    msg += "domain %s" % domain
		writeln(msg)
	    return self.doQuery(q)

   def dropObject(self, otype, monads):
      if self.objectExists(otype, monads):
	 q = "DROP OBJECT BY MONADS = %s " % monads.toString()
	 q += "[%s] GO"  % otype
	 return self.doQuery(q)


   def createObjectFeature(self, otype, feature, ftype, default=None):
      if not self.objectFeatureExists(otype, feature):
	  if self.verbose:
	     writeln('creating feature %s in object type [%s]' % (feature, otype))
	  q = "UPDATE OBJECT TYPE [%s ADD %s : %s;] GO" % (otype, feature, ftype)
	  success = self.doQuery(q)
	  return success
      else:
	 return True


   def setObjectFeature(self, otype, id_d, feature, val, force=False):
      if type(val) != 'str':
	 val = str(val)
      q = "UPDATE OBJECT BY ID_D = %i [%s %s := %s;] GO" % (id_d, otype, feature, val)
      r =  self.doQuery(q)
      return r


   def dropObjectFeature(self, otype, feature):
      if self.objectFeatureExists(otype, feature):
	 q = "UPDATE OBJECT TYPE [%s REMOVE %s;] GO" % (otype, feature)
	 return self.doQuery(q)
      else:
	 return True

   def createEnum(self, enum, vals):
      if self.enumExists(enum):
	 if self.verbose:
	    writeln('dropping existing enumeration %s' % enum)
	 self.dropEnum(enum)

      if vals == [] or vals == ():
	  vals = ['None']
      if self.verbose:
	 writeln('database = %s' % self.database)
	 writeln('creating enumeration %s' % enum)
      q = "CREATE ENUMERATION %s = {%s" % (enum, vals[0])
      for v in vals[1:]:
	 q += ", %s" % v
      q += " } GO"
      success = self.doQuery(q)
      if not success:
	 raise Exception("could not create %s" % enum)
      return success

   def getEnumLen(self, enum):
      if self.doQuery('SELECT ENUM CONSTANTS FROM ENUM %s GO' % enum):
	 table = self.getPyTable()
	 #import pdb; pdb.set_trace()
	 return len(table)
      else:
	 return 0


   def createNamedMonadSet(self, name, monads):
      if type(monads) == str:
	 monads = SetOfMonads(monads)
      return self.doQuery("CREATE MONAD SET %s WITH MONADS = %s GO" % \
                          (name, monads.toString()))

   def addEnumVal(self, enum, val, i=None):
      if self.enumExists(enum) and (not self.enumValueExists(enum, val)):
	    if i is None:
	       i = self.getEnumLen(enum) + 1
	    return self.doQuery("UPDATE ENUM %s = { ADD %s = %i } GO" % \
							    (enum, val, i))
      else:
	 return True
   
   def removeEnumVal(self, enum, val):
      if self.enumExists(enum) and self.enumValueExists(enum, val):
	    return self.doQuery("UPDATE ENUM %s = { REMOVE %s } GO" % \
                                                            (enum, val))
      else:
	 return True

   def dropEnum(self, enum):
      if self.enumExists(enum):
	 if self.verbose:
	    writeln('dropping enumeration %s' % enum)
	 return self.doQuery("DROP ENUMERATION %s GO" % enum)
      else:
	 return True


if __name__ == '__main__':
    
   from EmdrosApplication import *
   from Options import *

   options = Options(parse=True)

   emdros = EmdrosApplication(options=options, title='mqlengine', DO_LBL=False)
   mql = emdros.mql
   out = emdros.out
   ref = emdros.ref

   prompt = "database %s, usr %s" % (mql.database, options['usr']) 

   lastQuery = ''
   while 1 == 1:
      q = userMultiLineInput("enter a query, empty query repeats last one")

      if q == "":
	 choice = userAffirms('repeat last succesfull query?:\n\n%s\n\n' % lastQuery, cancelOK=True)
	 if choice in (True, -1):
	    q = lastQuery
      elif q in emdros.CFG.get_multi('exit_phrase'):
	 emdros.writeln('OK, bye.')
	 break
      elif re.match("mode[ \t]*=[ \t]*", q):
	 q = re.sub("mode[ \t]*=[ \t]*", "", q)
	 q = re.sub("[ \t]*$", "", q)
	 emdros.writeln('change mode to: %s' % q)
	 try:
	    emdros.setMode(q)
	 except:
	    continue
	
      if re.match("format[ \t]*=[ \t]*", q):
	 q = re.sub("format[ \t]*=[ \t]*", "", q)
	 q = re.sub("[ \t]*$", "", q)
	 emdros.writeln('change format to: %s' % q)
	 try:
	    emdros.setFormat(q)
	 except:
	    continue
      
      elif mql.doQuery(q):
	 lastQuery = q
	 if mql.isTable():
	    mql.showTable(mql.getPyTable())
	 elif mql.isSheaf():
	    sheaf = mql.getPySheaf().filterFocus()
	    if len(sheaf) > 0: 
		emdros.write(ref.byPySheaf(sheaf) + ' ')
		emdros.writeln(out.reprPySheaf(sheaf))
	    else:
		emdros.writeln('this query has no solutions\n')
	 else:
	    emdros.writeln("query result can not be displayed, probably was a command")
	     
