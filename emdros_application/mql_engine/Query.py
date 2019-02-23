from emdros_application.utils.IOTools import *
from PySheaf import *
from shlex import *
import copy
import re


class Query:

    def __init__(self, query, domain=None, doCorrect=False):
	q = copy.deepcopy(query)
	self.q = re.sub("\/", "#", q)
	self.tokens =  list(shlex(self.q))
	self.noOfTokens = len(self.tokens)

	self.parse(self.tokens, doCorrect=doCorrect)
	if domain:
	    self.insertDomain(domain)


    def parse(self, tokens, doCorrect=False):
	self.select_clause = []
	self.topograph    = []
	self.tail         = []

	i = 0
	SELECT = False
	TOPO   = False
	TAIL   = False
	EOQ    = False

	while not EOQ and i < self.noOfTokens:
	    curr = tokens[i]
	    if curr.upper() == "SELECT":
		SELECT = True
		TOPO = False
		TAIL = False
	    elif curr == "[":
		SELECT = False
		TOPO = True
		TAIL = False
	    elif curr == "]":
		SELECT = False
	    elif curr.upper() == "GO":
		TAIL = True

	    if SELECT:
		self.select_clause.append(curr)
	    elif TAIL:
		self.TOPO = False
		self.tail.append(curr)
		EOQ = True
	    elif TOPO:
		self.topograph.append(curr)
	    i += 1

	    if self.select_clause == "":
		if doCorrect:
		    self.select_clause = "SELECT ALL OBJECTS WHERE "
		else:
		    writeln("SELECT clause missing in\n%s" % self.q)
	    if self.tail == "":
		if doCorrect:
		    self.tail = "GO"

    def preProcess(self):
	DO_MACRO = False
	for t in self.tokens:
	    if re.match('[Mm][Aa][Cc][Rr][Oo]', t):
		DO_MACRO = True
		continue
	    elif DO_MACRO:
		DO_MACRO = False
	    else:
		pass		

    def PyObjectFromTopo(self, topo):
	t = copy.deepcopy(topo)
	obj = PyObject()

	self.stringValues = re.findall("(\"[^\"]*\")", t)
	for i in range(0, len(self.stringValues)):
	    t = re.sub("\"[^\"]*\"", "STRING_%d" %i, t, count=1)

	head = re.search("[ \t\n]*\[[ \t\n]*[A-Za-z_]+", t).group(0)
	t = t[len(head):]

	tail = re.search("[ \t\n]*\][ \t\n]*$", t).group(0)
	t = t[:-len(tail)]

	otype = re.search("[A-Za-z_]+", head).group(0)
	obj.otype =  otype
	return obj


    def findToken(self, token, substring=None):
	if substring is None: substring = self.tokens
	hits = []
	for i in range(0, len(substring)):
	    if token.lower() == substring[i].lower():
		hits.append(i)
	return hits

	
    def insertDomain(self, monads):
	if type(monads) != str:
	    monads = monads.toString()
	hits = self.findToken("IN", self.select_clause)
	if len(hits) > 1: 
	    raise Exception("multiple keywords IN, in: %s" % self.__repr__())
	elif len(hits) == 1:
	    IN_index = hits[0]
	    for i in range(IN_index+1, len(self.select_clause)):
		curr = self.select_clause[i]
		if curr != "{":
		    del self.select_clause[index:i+1]
		    break
		else:
		    while curr != '}' or i >= len(self.select_clause):
			i += 1
			curr = self.select_clause[i]
		    del self.select_clause[index:i+1]
		    break
	self.select_clause.insert(self.select_clause.index("WHERE"), "IN")
	self.select_clause.insert(self.select_clause.index("WHERE"), monads)
	return repr(self)


    def insertGetPhrase(self, getPhrase):

	DONE = False
	hits =  self.findToken("FOCUS", self.topograph)
	if hits:
	    for h in hits:
		i = h
		while self.topograph[i] not in ('[', ']'):
		    i += 1
		self.topograph.insert(i, getPhrase)
	else:
	    index = 0
	    for i in range(1, len(self.topograph)):
		curr = self.topograph[i]
		if curr.lower() == 'get':
		    index = i
		if curr in ('[', "NOTEXIST"):
		    if index != 0:
			del self.topograph[index:i]
			self.topograph.insert(index, getPhrase)
		    else:
			self.topograph.insert(i, getPhrase)
		    DONE = True
		    break
	    if not DONE:
		if index != 0:
		    del self.topograph[index:i]
		    self.topograph.insert(index, getPhrase)
		else:
		    self.topograph.insert(i, getPhrase)
	return repr(self)

		    
    def delToken(self, token, substring=None, num=1):
	if substring is None: substring = self.tokens
	hits = self.findToken(token, substring)
	if hits:
	    del substring[hits[0]]
	    if num > 1:
		for i in range(1, num):
		    hits = self.findToken(token, substring)
		    if hits:
			del substring[hits[0]]
	    

    def subToken(self, token1, token2, substring=None, num=1):
	if substring is None: substring = self.tokens
	hits = self.findToken(token1, substring)
	for i in range(0, num):
	    substring[hits[i]] = token2
	

    def toString(self, substring):
	tab = 0
	if substring == []:
	    s = ""
	else:
	    s = substring[0]
	    for token in substring[1:]:
		if token == '[':
		    tab += 1
		    s += ' %s' % (tab * "   ")
		if token == ']':
		    tab = tab - 1
		s += ' ' + token
		if token == ']':
		    s += ' %s'  % (tab * "   ")
	return s
	    
    def __repr__(self):
	rep =  self.toString(self.select_clause) + ' ' + \
	       self.toString(self.topograph) + ' ' + \
	       self.toString(self.tail)
	rep = re.sub("#", "/", rep)
	rep = re.sub("< >", "<>", rep)
	rep = re.sub("> =", ">=", rep)
	rep = re.sub("< =", "<=", rep)
	rep = re.sub("\. \.", "..", rep)
	rep = re.sub(" ` ", "`", rep)
	return rep

def insertGetPhrase(query, getPhrase):
    Q = Query(query)
    if len(Q.topograph) > 0:
	Q.insertGetPhrase(getPhrase)
	return repr(Q)
    else:
	return None


def insertDomain(query, monads):
    Q = Query(query)
    if len(Q.select_clause) > 0:
	Q.insertDomain(monads)
	return repr(Q)
    else:
	return None


def test():
    import sys
    q = ''
    for l in sys.stdin.readlines():
	q += l

    print insertGetPhrase(q, "get lam, kees, bok")
