#!/usr/bin/python

from emdros_application import *

DO_REF = True
DO_OUT = True
DO_LBL = True

class UnitManager(EmdrosApplication):

    def __init__(self, options,  listAllLabels=False):
	EmdrosApplication.__init__(self, options, DO_REF=DO_REF, DO_OUT=DO_OUT,
				   DO_LBL=DO_LBL)
	
	self.spin = Spinner()

	self.database    = self.cfg.get('database')
	self.mode        = self.cfg.get('mode')
	self.local_cfg   = self.modeCfgs[self.mode]

	self.objectTypes = self.local_cfg.getmulti('object_type')
	self.base_object   = self.local_cfg.get('base_object')

	# for LabelManager, all object types, including base_object,
	# should be in the objectTypes list.
	# for UnitManager, however, only the object types above 
	# base_object are needed.

	if self.base_object in self.objectTypes:
	    olist = list(self.objectTypes)
	    olist = olist[olist.index(self.base_object)+1:]
	    self.objectTypes = tuple(olist)

	for o in [self.base_object] + list(self.objectTypes):
	    if not self.mql.objectTypeExists(o):
		if not self.mql.createObjectType(o):
		       raise Exception("mql.createObjecType(%s) failed." % o) 
	    if not self.mql.enumExists('%s_%s_label_t' % (self.mode, o)):
		DEBUG("CREATING ENUM %s_%s_label_t" % (self.mode, o))
		self.mql.createEnum('%s_%s_label_t' % (self.mode, o), ('None',))
	    if not self.mql.createObjectFeature(o, '%s_labels' % self.mode,
						'LIST OF %s_%s_label_t' % (self.mode, o)):
	       raise Exception("mql.createObjectFeature(%s) failed." % o) 
	    else:
		self.mql.doQuery("SELECT FEATURES FROM OBJECT TYPE [%s] GO" % o, True, True, True)


	if not self.loadFromDatabase():
	    extraFeatures = self.local_cfg.get_multi('data_feature', self.base_object)
	    eF = ""
	    if extraFeatures <> None:
		for e in extraFeatures:
		    eF += ", " + e
	    writeln("No objects loaded, starting from [%s]" % self.base_object)
	    if not self.mql.objectFeatureExists(self.base_object, 'note'):
		self.mql.createObjectFeature(self.base_object, 'note', 'string')
	    q = "SELECT ALL OBJECTS WHERE [%s get %s_labels%s, note] GO" % (self.base_object, self.mode, eF)
	    self.mql.doQuery(q)
	    self.sheaf = self.mql.getPySheaf()
	    
	self.statsFile = addPath('%s.%s.labelstats' % (self.database, self.mode), self.kernel.LBL_DIR)
	self.stats = LabelStats(self.objectTypes, filename=self.statsFile)
	self.syncStats(self.sheaf, loadfreqs=userAffirms("add stats from %s?" % self.statsFile))



    def syncStats(self, sheaf, loadfreqs=False, reset=True):
	if reset:  # needed for recursion, see below
	    self.stats.reset()
	if loadfreqs:
	    self.stats.load()
	for straw in sheaf:
	    for o in straw:
		self.spin.next()
		if o.otype <> self.base_object:
		    label = self.stats.matchFiltered(o.otype, o.features['%s_labels' % self.mode])
		    self.stats.inc(o.otype, self.filterLabels(o.features['%s_labels' % self.mode]))
		    self.syncStats(o.sheaf, reset=False)




    def showObjectWindow(self, i1, i2):
	cls()
	for i in range(i1, i2+1):
	    if i <= len(self.sheaf) -1:
		straw = self.sheaf[i]
		txt = self.out.reprMonads(straw.monads)
		txt = re.sub('[\n]*$', '\n', txt)
		writeln("%s %i. %s" % (straw[0].otype[:4], i, txt ))

    def objType(self, i):
	return self.sheaf[i][0].otype

    def objTInd(self, otyp):
	if otyp not in self.objectTypes and otyp == self.base_object:
	    return -1  # careful: this is a flag, don't use as an array index!
	return self.objectTypes.index(otyp)

    def nextLevel(self, i):
	otyp = self.objType(i)
	if otyp == self.base_object:
	    return self.objectTypes[0]
	else:
	    n = self.objTInd(otyp) + 1
	if n > len(self.objectTypes) -1:
	    n = len(self.objectTypes) -1
	return self.objectTypes[n]

	
    def checkProposal(self, i1, i2, otyp):
	b = True
	otold = None
	for i in range (i1, i2+1):
	    o1 = self.objType(i)
	    if o1 <> otold:
		if otold == None:
		    otold = o1
		else:
		    if b:
		        b = userAffirms("*** combining %s with %s?" %(otold, o1))
	    if b:
		oi1 = self.objTInd(o1)
		oi2 = self.objTInd(otyp)
		if oi1 == oi2:
		    if b:
			b = userAffirms("*** nesting two %ss into eachother?" % otyp)
		elif oi2 < oi1:
		    if b:
			b = userAffirms("*** nesting %ss into %s?" % (otyp, o1))
		elif oi2 > oi1 + 1:
		    if b:
			b = userAffirms("*** jumping from %ss to %s?" % (otyp, o1))
	return b
		

    ### filter out all labels starting on '_', this allows the use of auxiliary labels
    ### which will not appear in the stats. The list of labels is either presented as
    ### a python list or as a string (lists of values are issued as strings by Emdros).

    def filterLabels(self, llist):
	if type(llist) == list:
	    newlist = []
	    for l in llist:
		if l[0] <> '_':
		    newlist.append(l)
	elif type(llist) == str:
	    newlist = re.sub("\(_[^,\)]*", "(", llist)
	    newlist = re.sub(",_[^,\)]*", ",", newlist)
	    newlist = re.sub(",[,]+", ",", newlist)

	return newlist



    def showUnit(self, i1, i2, otyp):

	newMonads = SetOfMonads()
	for i in range(i1, i2+1):
	    newMonads.unionWith(self.sheaf[i].monads)

	cls()
	writeln()
	writeln(self.out.reprMonads(newMonads))

	matchedLabels = self.lbl.matchLabels(otyp, newMonads)


	fLabels = self.filterLabels(matchedLabels)

	### add calculated labels
	if i1 <> i2:
	    for i in range(i1+1, i2+1):
		ot = self.sheaf[i][0].otype
		ff = self.local_cfg.get_multi('data_feature', ot)
		if ff: 
		    for f in ff:
			combiLabel = self.lbl.calculateCombiLabel(f, self.sheaf[i-1][0], self.sheaf[i][0])
			if combiLabel:
			    #writeln('%s: %s' % (f, combiLabel))
			    if not combiLabel in fLabels:
				fLabels.append(combiLabel)


	writeln()
	writeln("%s labels: %s" % (self.mode, repr(fLabels)))
	ml = self.stats.match(otyp, fLabels, filtered=True)
	writeln()
	if len(ml) == 0: 
	    writeln('pattern not encountered before')
	else:
	    writeln(repr(ml))
	    for m in ml:
		write("%ix " % self.stats.getCount(otyp, m))
		for l in m:
		    if not search("^_", l):
			write(" %s" % l)
		writeln()
	writeln()


    def editWindow(self, curr, i1=None):
	if i1 is not None:
	    if not(i1 >= 0 and i1 <= len(self.sheaf)-1):
		i1 = None
	if i1 is None:
	    i1 = userIntInput("start of new object:", 
		    min=0, max=len(self.sheaf)-1, cancelOK=True)
	if i1 == None: 
	    i1 = -1
	else:
	    i2 = userIntInput("  end (<Rt> = %i):" % (i1+1), 
			min=0, max=len(self.sheaf) - 1, cancelOK=True)
	    if i2 == None: i2 = i1+1

	if i1 <> -1 and i2 <> -1 and i2 >= i1:
	    #self.showObjectWindow(i1, i2)

	    nextl = self.nextLevel(i1) ## guessing first level
	    self.showUnit(i1, i2, nextl)

	    if self.checkProposal(i1, i2, nextl):
		if userAffirms("new %s OK?" % nextl, cancelOK=True, cancelMsg="(<Rt> = yes)"):
		    otyp = nextl
		else:
		    self.showObjectWindow(i1, i2)
		    otyp = userNumberedOption(self.objectTypes, 
			question="select type of new object")
		    if otyp <> None:
			self.showUnit(i1, i2, otyp)
			if not userAffirms("new %s OK?" % otyp):
			    otyp = None
	    else:
		 otyp = userNumberedOption(self.objectTypes,
		     question="select type of new object")
	    if otyp <> None:
		self.newUnit(i1, i2, otyp)


    def newUnit(self, i1, i2, otyp):

	# establish the monads of the new object
	# and calculate the labels that would apply to it

	newMonads = SetOfMonads()
	for i in range(i1, i2+1):
	    newMonads.unionWith(self.sheaf[i].monads)
	matchedLabels = self.lbl.matchLabels(otyp, newMonads)


### TODO HJB: hier moet een call naar createCalculatedLabels in, zodat deze meegenomen worden

	# create a new PyObject, assign labels to it,
	# put its constituent objects inside it i
	# and store the result in the database

	newObject = PyObject(otype=otyp, monads=newMonads)

	newObject.addFeature("%s_labels" % self.mode, matchedLabels)
	#for l in matchedLabels:
	    #newObject.addListValue('%s_labels' % self.mode, l)

	self.stats.inc(otyp, self.filterLabels(newObject.features['%s_labels' % self.mode]))

	for i in range(i1, i2+1):
	    newObject.sheaf.appendPyStraw(self.sheaf[i])

	self.mql.VERBOSE = True
	newObject.id_d = self.mql.storeObject(newObject, recursive=False)
	self.mql.VERBOSE = False

	# put the new PyObject inside a new straw, and
	# place this straw into self.sheaf

	newStraw = PyStraw()
	newStraw.appendPyObject(newObject)
	del self.sheaf.straws[i1:i2+1]
	self.sheaf.straws.insert(i1, newStraw)
	self.sheaf.refreshMonads()


	    
    def changeOutputFormat(self):
	self.out.mode = userKeyPress(self.out.modes,
				     question='mode:',
				     fullkey=True,
				     cancelOK=False)
	self.out.format=userKeyPress(self.out.formats,
				     question='format:',
				     fullkey=True,
				     cancelOK=False)

    def addNote(self, curr):
	i = userIntInput("add note to object: ",min=curr, max=curr+self.windowSize-1, cancelOK=True)
	cls()
	obj = self.sheaf[i][0]
	otype = self.sheaf[i][0].otype
	id_d  = self.sheaf[i][0].id_d
	self.showUnit(i, i, otype)
	if obj.features.has_key('note') and obj.features['note'] <> "":
	    writeln("note is now:\n%q" % obj.features['note'])

	note = userMultiLineInput(question="enter note:", confirm=True, emptyOK=True)
	q = 'UPDATE OBJECT BY ID_D = %d [%s note := "%s"; ] GO' % (id_d, otype, note)
	if not self.mql.doQuery(q) and userAffirms("unable to add this note to the database, try again?"):
	    self.addNote(curr)
	


    def undo(self, curr):
	i = userIntInput("undo object: ",min=curr, max=curr+self.windowSize-1, cancelOK=True)
	if i <> None:
	    currStraw = self.sheaf[i]

	    # presumably, the straw only contains one object
	    # checking, just to be sure
	    if len(currStraw.objects) <> 1:
		raise Exception("straw %i has %i objects (should be 1)" % \
			       (curr, len(currStraw.objects)))

	    o = currStraw[0]
	    if o.otype <> self.base_object:
		del self.sheaf.straws[i]
		self.stats.dec(o.otype, self.filterLabels(o.features['%s_labels' % self.mode]))
		try:
		    if not self.mql.deleteObject(o):
			WARNING("Unable to drop object from database. Expect trouble...")
		except:
		    raise Exception("%s" % repr(o))
		j = i
		for straw in o.sheaf.straws:
		    self.sheaf.straws.insert(j, straw)
		    j += 1


    def jump(self):
	m = self.ref.findMonads()
	if m <> None:
	    m = m.first()
	    for i in range(0, len(self.sheaf)-1):
		if self.sheaf[i].monads.isMemberOf(m):
		    return i
	return -1


    def showLabels(self, i, otype=None):
	obj = self.sheaf[i][0]
	self.showUnit(i, i, obj.otype)
	userInput("<enter> to continue")


    def doExtras(self, curr):
	options = ("format", "windowsize", "show labels", "edit labels", "load objects", "clear all")
	choice = userKeyPress(options, cancelOK=True)
	if choice == "f":
	    self.changeOutputFormat()
	elif choice == "s":
	    i = userIntInput("select object (-1 to cancel):")
	    if i <> -1:
		self.showLabels(i)
	elif choice == "e":
	    self.lbl.userEdit()
	elif choice == "l":
	    self.loadFromDatabase()
	elif choice == "w":
	    ws = userIntInput("window now %i objects, change to:" % self.windowSize)
	    if ws > 0:
		self.windowSize = ws
	elif choice == "c":
	    if userAffirms("This will remove all %s objects from the data. OK?"):
		self.clearAll()


    def mainMenu(self):
	options = ("create","undo","back 1 object", "jump", "note", "options", "quit")
	return userKeyPress(options, cancelOK=True, integerOK=True)


    def freeStyle(self,filtered=True):
	self.windowSize = 10
	STOP = False
	curr = 0
	while not STOP:
	    self.showObjectWindow(curr, curr + self.windowSize-1)
	    choice = self.mainMenu()

	    if choice == "c" or type(choice) == int:
		if curr <= len(self.sheaf) -1:
		    self.editWindow(curr, choice)
	    elif choice == "b":
		curr = curr - 1
		if curr < 0: curr = 0
	    elif choice == "j":
		    j = self.jump()
		    if j <> -1:
			curr = j
	    elif choice == "n":
		self.addNote(curr)
	    elif choice == "u":
		self.undo(curr)
	    elif choice == "o":
		self.doExtras(curr)
	    elif choice == "l":
		self.loadFromDatabase()
	    elif choice == "q":
		if userAffirms("save label statistics?"):
		    self.save()
		STOP = True
	    else:
		curr += 1
		if curr > len(self.sheaf)-1:
		    curr = len(self.sheaf)-1


    def syncDataToSheaf(self, affirm=False):
	if affirm:
	    cont = userAffirms("synchronize database %s?" % self.mql.database)
	else:
	    cont = True
	if cont: 
	    writeln("Patience, this will take a while.")
	    warning("Do not interrupt the program, or the database objects will be corrupted.")
	    for otyp in self.objectTypes:
		for straw in self.sheaf:
		    self.spin.next()
		    self.mql.storeObject(straw[0], recursive = True)
	    
    def clearAll(self):
	DEBUG(self.objectTypes)

    def save(self):
	import time
	import re
	self.syncStats(self.sheaf)
	self.stats.save()
	    

    def loadFromDatabase(self):

	def load_recursion(o, objectList, firstandlast=False):
	    i = objectList.index(o)
	    q = "[%s " % o
	    if firstandlast: q += " first and last "
	    q += " get %s_labels " % self.mode
	    ff = self.local_cfg.get_multi('data_feature', o)
	    if ff <> None:
		for f in ff: 
		    q += ', ' + f
	    if i < len(objectList)-1:
		q += load_recursion(objectList[i+1], objectList)
	    q += "]"
	    return q

	writeln('loading data from database %s' % self.database)
	otypes =  list(self.objectTypes)[::-1]
	if self.base_object not in otypes:
	    otypes = otypes + [self.base_object,]
	q = "SELECT ALL OBJECTS WHERE "
	for o in otypes:
	    self.spin.next()
	    q += "\n"
	    if otypes.index(o) > 0:
		q += "OR\n"
	    q += load_recursion(o, otypes, firstandlast=False)
	q += ' GO'

	if self.mql.doQuery(q) and len(self.mql.getPySheaf()) > 0:
	    sheaf = self.mql.getPySheaf()
	    self.sheaf = PySheaf()

	    laststraw = PyStraw()
	    lastmonads = SetOfMonads()
	    for straw in sheaf:
		self.spin.next()
		if self.sheaf.straws == []:
		    self.sheaf.appendPyStraw(straw)
		    laststraw = straw
		    lastmonads = straw.monads
		else:
		    if straw.monads.part_of(lastmonads):
			pass
		    elif lastmonads.part_of(straw.monads):
			laststraw = straw
			lastmonads = laststraw.monads
			self.sheaf.replacePyStraw(-1, straw)
		    else:
			self.sheaf.appendPyStraw(straw)
			laststraw = straw
			lastmonads = straw.monads
	    return True
	else:
	    return False



if __name__ == '__main__':
    options = Options('options')
    uM   = UnitManager(options)
    uM.freeStyle()
