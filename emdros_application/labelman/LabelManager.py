import re
import copy
from time import gmtime, strftime

from emdros_application.syscfg.config import *
from emdros_application.utils.Paths import *
from emdros_application.utils.IOTools import *
from emdros_application.utils.Configuration import *
from emdros_application.mql_engine import *
from LabelDefinition import *


class LabelManager():

    def __init__(self, mql, mode, globalcfg, local_cfg=None, opt_otypes=None, kernel=None):
        if kernel is None:
            kernel = __import__(DEFAULT_KERNEL)
	self.globalcfg = globalcfg
	if local_cfg == None:
            local_cfg = globalcfg
	self.local_cfg = local_cfg

	self.mql = mql
	self.mode = mode
	self.database = mql.database
	self.auto = self.globalcfg.get('auto')
	only_object_type  = self.globalcfg.get('Object')

	if self.local_cfg == None:
	    exitOnError("programming error, self.local_cfg==None, in LabelManager.__init__()")

	self.spin = Spinner(delay=0)
	self.labelDefs = LabelDefBase() # always starts out empty

        try:
            self.logfile_name = kernel.LOG_DIR + 'labelman.log'
        except:
            self.logfile_name = 'labelman.log'
	self.logfile = None
	self.ERRORS_FOUND = False

	### SET LOCAL VARIABLES ###############
	self.commit = (self.globalcfg.get('test') == False)
	self.verbose = self.globalcfg.get('verbose')
	self.VERBOSE = self.globalcfg.get('VERBOSE')

        self.labelFiles = {} # useful for error messages in label definitions
        self.updateList = [] # objects that will have to be updated

	### LOAD DATA AND UPDATE DATABASE

	if opt_otypes not in ([], None):
	    self.objectTypes = opt_otypes
	    self.auto = True
	else:
	    self.objectTypes = self.local_cfg.get_multi('object_type')
	    if local_cfg.has_key('lbl_object_type'):
		self.objectTypes += local_cfg.get_multi('lbl_object_type')
	if self.objectTypes is not None:
	    for otype in self.objectTypes:
	       self.loadLabelDefinitions(otype, kernel=kernel)
	       if not self.mql.objectTypeExists(otype):
		   labels = list(filter(lambda l: re.search(":=",l) is None, self.getLabels(otype)))
		   self.mql.createObjectType(otype, mode=self.mode, labels=labels)
	else:
	    warning("No object types defined in %s" % self.local_cfg.filename)
	if self.verbose:
	    writeln('%s labels manager initiated for database %s' % (self.mode, self.database))
	
	    
    def getLabels(self, otype):
	return self.labelDefs.getLabels(otype)

    def getDefs(self, otype, label):
	return self.labelDefs.getDefs(otype, label)

    def __repr__(self):
	r = "labelmanager on database %s\n" % self.database 
	for o in self.objectTypes:
	    r += "%s: %s\n" % (o, repr(self.labelDefs.getLabels(o)))
	return r


    def selectUpdatedObjects(self,mql=None):
	if mql == None: mql = self.mql
	typeList = []
	DONE = False
	for o in self.objectTypes:
	    if not mql.enumExists("%s_%s_label_t" % (self.mode, o)):
		typeList.append('*' + o)
	    else:
		typeList.append(o)
	while not DONE:
	    selection = userCheckList(typeList,
				       question="toggle %s labels to update:" % self.mode)
	    if userAffirms("selection OK?"):
		DONE = True
        return selection


    def loadLabelDefinitions(self, objectType, kernel):
	labelFile = self.local_cfg.get('label_file', objectType)
	labelFile = addPathAndExt(labelFile, kernel.LBL_DIR, kernel.LBL_EXT)
        self.labelFiles[objectType] = labelFile
        self.labelDefs.add(LabelDefinition(filename=labelFile,
					   otype=objectType,
					   mode=self.mode,
					   verbose=self.verbose,
                                           kernel=kernel))

    def mqlUpdateCommand(self, obj, label):
        q = "UPDATE OBJECT BY ID_DS = %d \n   [%s " % (obj.id_d, obj.otype)
        q += "%s_labels := %s;" % (self.mode,
            obj.featureStrings["%s_labels" % self.mode])
        q += "\n   ]\nGO"
        return q


    def valueType(self, value):

        if type(value) == int or re.search("^[\-]*[0-9][0-9]*$", value):
            return 'integer'

        elif value[0] == '"' and value[-1] == '"':
            return 'string'

        elif re.search('^[a-zA-Z_, ]*' , value):
            return 'enum'
	
	else:
	    raise Exception('LabelManager.valueType: unknown type for %s' % \
		repr(value))


    def createObjectFeatureFromValue(self, otype, feature, value):

        db_ftype = self.mql.objectFeatureExists(otype, feature)
        ftype    = self.valueType(value)

        if ftype == 'enum':
                db_ftype = "%s_%s_t" % (otype, feature)
                if not self.mql.enumExists(db_ftype):
                    self.mql.createEnum(db_ftype, ('NA',))
		self.mql.addEnumVal(db_ftype, value)
        else:
            db_ftype = ftype
        return self.mql.createObjectFeature(otype, feature, db_ftype)


    def assignFeatures(self, otype, assign_statements, queries):
        write('assigning %s %s feature(s): %s\n' % (self.mode, otype, assign_statements))
	feat_val = self.parseStatements(assign_statements)

	for (feature, value) in feat_val:
	    self.createObjectFeatureFromValue(otype, feature, value)

        id_ds = []
        for q in queries:
            if self.mql.doQuery(q):
		sheaf = self.mql.getPySheaf()
                for straw in sheaf.filterFocus():
                    for obj in straw:
                        if not obj.id_d in id_ds:
                            id_ds.append(obj.id_d)
                continue
	    else:
		self.logError(q, self.mode, otype, assign_statements, self.mql.getAllErrors())
		#writeln("query failed:\n%s" % q)
		
	if id_ds == []:
		self.logError(q, self.mode, otype, assign_statements, 'no solutions found')
		if self.verbose:
		    writeln("query had no solutions:\n%s" % q)

        else:
	    for (feature, value) in feat_val:
		q2 = "UPDATE OBJECTS BY ID_DS = %d" % id_ds[0]
		for i in id_ds[1:]:
		    q2 += ", %d" % i
		q2 += "\n[%s %s := %s;]\nGO" % (otype, feature, value)
		if self.verbose:
		    writeln_stderr(q2)
		self.mql.doQuery(q2)


    def parseStatements(self, assign_statements):
	ret = []
	statements = re.sub(" ", "", assign_statements)
	statements = re.split(";", statements)
	for st in statements:
	    if not st: continue
	    st = re.sub(";", "", st)
	    ret.append(re.split("[ ]*:=[ ]*", st))
	return ret

	



    def updateAll(self, forced = False, mql=None, objTypes=None):
	if self.verbose:
	    writeln('update all %s labels in %s' % (self.mode, self.database))
	if mql == None: mql = self.mql
	if objTypes <> None:
	    typList = objTypes
	elif self.auto:
	    typList = self.objectTypes
	else:
	    typList = self.selectUpdatedObjects()

	for otype in typList:
	    if not mql.objectFeatureExists(otype, "%s_labels" % self.mode):
		self.createLabelType(otype)
	    self.updateByObjectType(otype, domain=None, forced=forced, mql=mql)


    def updateByObjectType(self, otype, domain=None, forced=False, mql=None):
	#import Query
	if mql == None: mql = self.mql

	self.dropLabelType(otype, mql=mql)
	self.createLabelType(otype, mql=mql)
	
	labels = self.labelDefs.getLabels(otype)
	if labels == None:
	    if self.verbose:
		writeln('no %s labels for object type %s' % (self.mode, otype))

	else:
	    for label in self.labelDefs.getLabels(otype):
		DO_DELETE = False
		if re.search("DELETE[ \t]*", label):
		    DO_DELETE = False
		    label = re.sub("DELETE[ \t]*", "", label)
		    writeln("removing %s %s label '%s'" % (self.mode, otype, label))
		elif re.search(":=", label):
		    self.assignFeatures(otype, label, self.labelDefs.getDefs(otype, label))
		    continue
		else:
		    writeln("assigning %s %s label '%s'" % (self.mode, otype, label))
		for query in self.labelDefs.getDefs(otype, label):

		    # need to retrieve the already assigned labels
		    q = Query(query).insertGetPhrase('get %s_labels'% self.mode)
		    if q == None:
			self.logError(query, self.mode, otype, label, 'empty query?')
			continue
		    if mql.doQuery(q):
			sh = mql.getPySheaf()
			sheaf = sh.filterFocus()
		    else:
			if re.search("SELECT.*OBJECT", q):
			    selecterr = ""
			else:
			    selecterr = "\n'SELECT ALL OBJECTS WHERE' missing."
			self.logError(q, self.mode, otype, label, mql.getAllErrors()+ selecterr)
			writeln("query failed:\n%s" % q)
			continue


		    if sheaf <> None:
			for straw in sheaf:
			    for obj in straw:
				self.spin.next()
				if re.search(":=", label):
				    self.parseUpdateLine(obj, label, mql)
				else:
				    if DO_DELETE:
					obj.delListValue('%s_labels' % self.mode, label)
				    else:
					obj.addListValue('%s_labels' % self.mode, label)
					
				    q = self.mqlUpdateCommand(obj, label)
				    if not mql.doQuery(q):
					raise Exception("query failed:\n%s" % q)
		    else:
			if verbose:
			    writeln("no solution for query:")
			    writeln(q)


    def parseUpdateLine(self, obj, label, mql):
        ret = ''
        commands = re.split(';', label)
        for c in commands:
            if c <> '':
                if not c.index(':='):
                    raise Exception(':= operator missing in MQL line:\n%s' % c)
                feature = re.sub('^[ \t]*(?P<xxx>[^ \t]*)[ \t]*\:\=.*$', '\g<xxx>', c)
                value   = re.sub('^.*\:\=[ \t]*(?P<xxx>[^ ]*)', '\g<xxx>', c)

                mql.assignFeature(obj, feature, value)


    def matchLabels(self, otype, monads, mql=None, emitError=False):
	if mql==None: mql=self.mql
	tmpObject = mql.createObject(otype, monads)
	matchedLabels = []
	for l in self.labelDefs.getLabels(otype):
            try:
                if self.matchToMonads(otype, l, monads, mql=mql):
                    matchedLabels.append(l)
                    tmpObject.addListValue('%s_labels' % self.mode, l)
                    q = self.mqlUpdateCommand(tmpObject, tmpObject.features["%s_labels" % self.mode])
                    if not mql.doQuery(q):
                        mql.deleteObject(tmpObject)
                        exitOnError()
            except:
                mql.deleteObject(tmpObject)
                exitOnError()
	mql.deleteObject(tmpObject)
	return matchedLabels

    def matchToMonads(self, otype, label, monads, mql=None):
	if mql == None: mql = self.mql
	for q in self.labelDefs.getDefs(otype, label):
	    #q = Query(q).insertGetPhrase('get %s_labels' % self.mode)
	    err_msg = 'problem in definition of label "%s" (%s):\n%s' % (label, self.labelFiles[otype], q)
	    if re.search('[ \t\n][Ff][Oo][Cc][Uu][Ss]',q):
		return mql.matchFocusQuery(q, inner_domain=monads) 
	    elif mql.doQuery(q, domain=monads):
		if mql.solutionFound():
		    return True
	    else:
		raise Exception(err_msg)
	else:
	    return False

    def calculateCombiLabel(self, feature, obj1, obj2):
	if obj1.hasFeature(feature) and obj2.hasFeature(feature):
	    feat1 = obj1.features[feature]
	    feat2 = obj2.features[feature]
	    if type(feat1) <> str:
		feat1 = str(feat1)
	    if type(feat2) <> str:
		feat2 = str(feat2)
	    return feat1 + '-' + feat2
	else:
	    return None

    ### DATABASE MANIPULATION : MQL STUFF ###############

    def dropLabelType(self, otype, mql=None):
	if mql == None: mql = self.mql
	if self.verbose:
	    if mql.objectFeatureExists(otype, "%s_labels" % self.mode):
		writeln("dropping [%s %s_labels ] from database %s" % \
			    (otype, self.mode, mql.database))
	mql.dropObjectFeature(otype, '%s_labels' % self.mode)
	mql.dropEnum("%s_%s_label_t" % (self.mode, otype))

    def createLabelType(self, otype, mql=None):
	if mql == None: mql = self.mql
	self.dropLabelType(otype, mql)
	labels = self.labelDefs.getLabels(otype)
	if labels is not  None:
	    ll = []
	    for l in labels:
		if not re.search(':=', l):
		    ll.append(l)
	    self.createLabelType_old(otype, ll, mql=mql)

    def createLabelType_old(self, otype, vals=None, mql=None):
	if mql==None: mql=self.mql
	real_vals = list(filter(lambda v: re.search(":=", v) is None, vals))
	if real_vals <> []:
	    if mql.createEnum("%s_%s_label_t" % (self.mode,otype), real_vals):
		if self.verbose:
		    writeln("\ncreated enumeration %s_%s_label_t as %s" % (self.mode,otype, repr(real_vals)))
	    else:
		raise Exception("unable to create enumeration %s_%s_label_t" % (self.mode,otype))

	    #if not mql.objectTypeExists(otype):    # AAP
		#mql.createObjectType(otype)

	    if not mql.objectFeatureExists(otype, "%s_labels" % self.mode):
		if self.verbose:
		    writeln("creating %s_%s_label_t" % (self.mode, otype))
		if not mql.createObjectFeature(otype, "%s_labels" % self.mode,
				"list of %s_%s_label_t" % (self.mode,otype)):
		    pass
		    #raise Exception("unable to create %s_%s_label_t" % (self.mode,otype))
	else:
	    if self.verbose:
		writeln("No values for %s_%s_label_t found, skipped." % (self.mode,otype))

#######################  MISC  ###############################################

    def addLabel(self, otype, label, mql=None):
	if mql==None: mql=self.mql
	if self.verbose:
	    write("adding %s %s label '%s'..." % (self.mode, otype, label))
	i = self.labelDefs.addLabel(otype, label)
	mql.addEnumVal("%s_%s_label_t" % (self.mode,otype), label, i)
	if self.verbose:
	    writeln('done.')


    def logError(self, query='', mode='', otype='', label= '', msg= '', timed = False, IS_ERR=True):
	lines = []
	if self.logfile is None:
	    try:
		log = open(self.logfile_name, 'r')
		for l in log:
		    lines.append(l)
		log.close()
	    except:
		writeln('opening new log file %s' % self.logfile_name)
	    self.logfile = open(self.logfile_name, 'w')
	    for l in lines:
		self.logfile.write(l)
	if timed:
	    self.logfile.write("\n#### %s: %s\n" % \
		(strftime("%Y-%m-%d %H:%M:%S", gmtime()), msg))
	else:
	    self.logfile.write("Issue with query for  %s_%s_label '%s':\n" % \
					    (mode, otype, label))
	    self.logfile.write(query)
	    self.logfile.write('message: ' + msg + '\n\n')
	self.ERRORS_FOUND = IS_ERR


if __name__ == '__main__':
    from Options import *
    from EmdrosApplication import *

    options = Options('options', parse=False)
    options.addOption('Object', 'O', default=None, help='Only update labels for this unit type. Assumes proper setting of -m option.')
    options.parse()


    e = EmdrosApplication(options=options, DO_LBL=True, DO_REF=False, DO_OUT=False,
			    opt_otypes = options.getArgs())
    lm = e.lbl
    lm.logError(msg="LABELMAN STARTS", timed =True, IS_ERR=False)
    if not options.get('sync'):      # if sync is set, label have already been
	lm.updateAll()               # updated during initialization.


    if lm.ERRORS_FOUND:
	writeln('problem(s) encountered in label definition(s), check %s' % lm.logfile_name)
    lm.logError(msg="LABELMAN STOPS", timed =True, IS_ERR=False)
    if lm.logfile is not None:
	lm.logfile.close()

