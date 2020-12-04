#!/usr/bin/python
from emdros_application import *


class ClauseAtomPairs2Units(EmdrosApplication):

    def __init__(self, options, localcfg=None,
		 DO_REF=True, DO_OUT=True, DO_LBL=False):

	EmdrosApplication.__init__(self, options, localcfg,
				   DO_REF=False, DO_OUT=True, DO_LBL=False)


	self.spin = Spinner()
	self.mql.createObjectFeature('clause_atom', 'daughters', 'list of id_d')

	self.addDaughters()
	self.ca_list = self.getClauseList()
	self.ca_offset = self.ca_list[0]['number']

	self.unt_list = []
	self.lvl_dict = {}
	for ca in self.ca_list:
	    self.getUnt(ca)
	self.storeUnits(self.unt_list, self.lvl_dict)
	self.doUnitRelations()
	self.doUnitLevels()


    def addDaughters(self):

	cas = {}
	q = "SELECT ALL OBJECTS WHERE [clause_atom get mother, number] GO\n"
	self.mql.doQuery(q)
	for ca in self.mql.getPySheaf().flatten():
	    if ca['mother'] <> 0:
		if not cas.has_key(ca['mother']):
		    cas[ca['mother']] = []
		cas[ca['mother']].append(ca.id_d)

	for ca in cas.keys():
	    self.spin.next()
	    if cas[ca]:
		q = "UPDATE OBJECT BY ID_D = %d " % ca
		q+= "[clause_atom daughters := ("
		q += "%d" % cas[ca][0]
		for id_d in cas[ca][1:]:
		    q += ",%d" % id_d
		q += "); ] GO"
	    self.mql.doQuery(q)

    def addUnit(self, monads, lvl=0):
	if not monads.toCompactString() in self.unt_list:
	    self.unt_list.append(monads.toCompactString())
	if not self.lvl_dict.has_key(monads.toCompactString()):
	    self.lvl_dict[monads.toCompactString()] = lvl


    def getUnt(self, ca, monads=None, lvl=0):
	self.addUnit(ca.monads) # each clause_atom is a unit at level 0
	branch_monads = self.getBranch(ca, monads=ca.monads)
	if ca['mother'] == 0:
	    mother = ca
	else:
	   mother = self.getObj(ca['mother'])
	if ca['number'] < mother['number']:
	    self.addUnit(SetOfMonads(branch_monads.first(),
				     mother.monads.last()))
	else:
	    self.addUnit(SetOfMonads(mother.monads.first(),
				     branch_monads.last()))

    def getBranch(self, ca, monads):
	branch_monads = SetOfMonads(monads.first(), monads.last())
	if ca['daughters']:
	    for d in ca['daughters']:
		daughter = self.getObj(d)
		branch_monads.unionWith(self.getBranch(daughter, daughter.monads))
	return (branch_monads)
	    

    def dump(self, unt_list, lvl_list):
	for u in  unt_list:
	    som = SetOfMonads(u)
	    print 'lvl = %d' % lvl_list[u]
	    print self.out.byMonads(som)
	    print

    def storeUnits(self, unt_list, lvl_list):

	if not self.mql.objectTypeExists("unit") or self.auto:
	    self.mql.dropObjectType("unit")
	    self.mql.createObjectType(otype="unit", mode="syntactic")
	    self.mql.createObjectFeature("unit", "tab", "integer", "-1")
	    self.mql.createObjectFeature("unit", "level", "integer", "-1")
	    self.mql.createObjectFeature("unit", "mother", "ID_D")
	else:
	    self.mql.deleteObjectsFrom("unit", self.domain)


	q = "CREATE OBJECTS WITH OBJECT TYPE [unit]\n"
	for u in unt_list:
	    som = SetOfMonads(u)
	    q += "CREATE OBJECT FROM MONADS = %s [" % som.toString()
            if MQL_VERSION < 3.7:
                q += "first_monad := %d; " % som.first()
                q += "last_monad := %d; "  % som.last()
            q += "level := %d;]\n"   % lvl_list[u]
	    #q += "level := %d;]\n"   % self.calcLevel(som)

	q += "GO"
	self.mql.doQuery(q)


    def related(ca1, ca2):
	return (ca1.id_d == ca2['mother']) or (ca2.id_d == ca1['mother'])


    def getObj(self, id_d):
	return self.ca_list[self.ca_index_dict[id_d]]

    def get_index(self, ca):
	return ca['number'] - self.ca_offset

    def number(self, ca):
	return self.get_index(ca) + 1

    def getNext(self, p, unt_list):
	i = unt_list.index(p)
	if i >= len(unt_list):
	    return None
	else:
	    return unt_list[i+1]

    def getClauseList(self):
	q = "SELECT ALL OBJECTS WHERE [clause_atom " + \
	    "GET first_monad, last_monad, mother, daughters, number, tab] GO"
	self.mql.doQuery(q)
	ca_list = self.mql.getPySheaf().flatten()

	self.ca_index_dict = {}
	self.max_tab = -1
	for ca in ca_list:
	    self.spin.next()
	    self.ca_index_dict[ca.id_d] = ca_list.index(ca)
	    if ca['tab'] > self.max_tab: self.max_tab = ca['tab']
	return ca_list


    def doUnitRelations(self):
	q = "SELECT ALL OBJECTS WHERE\n"
	q = "%s[clause_atom_pair AS cap1\n" % q
	q = "%s   [unit FOCUS OVERLAP(SUBSTRATE) first_monad = cap1.first_monad\n" % q
	q = "%s      [clause_atom as ca1 FIRST]\n" % q
	q = "%s   ]\n" % q
	q = "%s   !\n" % q
	q = "%s   [unit FOCUS OVERLAP(SUBSTRATE) \n" % q
	q = "%s	     [clause_atom FIRST \n" % q
	q = "%s	         mother = ca1.self OR\n" % q
	q = "%s	         self   = ca1.mother\n" % q
	q = "%s	     ]\n" % q
	q = "%s   ]\n" % q
	q = "%s]\n" % q
	q = "%sGO\n" % q

	if self.mql.doQuery(q):
	    for straw in self.mql.getPySheaf():
		self.spin.next()
		for ca_pair in straw:
		    unit_1 = ca_pair.sheaf[0][0]
		    unit_2 = ca_pair.sheaf[0][1]
		    q = "UPDATE OBJECTS BY ID_DS = %s [unit mother := %d;] GO" % \
			(unit_2.id_d, unit_1.id_d)
		    self.mql.doQuery(q)

    def doUnitLevels(self):
	lvl = 0
	DONE = False
	while not DONE:
	    q = "SELECT ALL OBJECTS WHERE\n"
	    q+= "[unit AS u1\n" 
	    q+= "   [unit self <> u1.self AND level = %d]\n" % lvl
	    q+= "] GO"
	    if not self.mql.doQuery(q) or not self.mql.solutionFound():
		DONE = True
	    else:
		lvl += 1
		units_list = self.mql.getPySheaf().flatten()
		update_list = []
		q = "UPDATE OBJECTS BY ID_DS = "
		for u in units_list[:-1]:
		    q += "%d, " % u.id_d
		q += "%d\n[unit level := %d;]\nGO" % (units_list[-1].id_d, lvl)
		self.mql.doQuery(q)


if __name__ == '__main__':


    options = Options('options')
    if options.get('domain') is None:
	if not options.get('auto'):
	    if not userAffirms('No domain specified. Run for ENTIRE database %s?' % options.get('database')):
		quit()
    ca2p = ClauseAtomPairs2Units(options=options)

