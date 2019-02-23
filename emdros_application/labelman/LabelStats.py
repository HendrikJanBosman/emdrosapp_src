#!/usr/bin/python

import re
from emdros_application.utils.IOTools import *

class LabelStats:

    def __init__(self, otypes=None, filename=None, filtered=True):
	self.counts = {}
	self.otypes = []
	self.filtered = filtered

	if filename == None:
	    filename = "labelstats"
	self.filename=filename

	if otypes <> None:
	    for o in otypes:
		self.otypes.append(o)
		self.counts[o] = {}

    def set(self, o, labels, freq, pro=True):
	labels = self.__labels2tuple__(labels)
	if o not in self.counts.keys():
	    self.counts[o] = {}
	    self.otypes.append(o)
	self.counts[o][labels] = freq


    def inc(self, o, labels, pro=True):
	labels = self.__labels2tuple__(labels)
	if o not in self.counts.keys():
	    self.counts[o] = {}
	    self.otypes.append(o)
	if labels not in self.counts[o].keys():
	    self.counts[o][labels] = 1
	else:
	    self.counts[o][labels] += 1

    def dec(self, o, labels, pro=True):
	labels = self.__labels2tuple__(labels)
	if labels in self.counts[o].keys():
	    if self.counts[o][labels] > 0:
		self.counts[o][labels] = self.counts[o][labels]-1
	
    #def match(self, o, labels, pro=True):
	#if not self.filtered:
	    #return self.matchUnfiltered(o, labels, pro)
	#else:
	    #return self.matchFiltered(o, labels, pro)
    
    def match(self, o, labels, filtered=True, pro=True):
	def isSubSet(l1, l2):
	    RET = l1 <> []
	    for l in l1:
		if not l in l2:
		    RET = False
	    return RET

	retList = []
	labels = self.__labels2tuple__(labels)
	if not o in self.counts.keys():
	    return None
	for k in self.counts[o].keys():
	    if filtered:
		if isSubSet(k,labels):
		    retList.append(k)
	    else:
		if k == labels:
		    retList = k
	return retList

    def matchFiltered(self, o, labels, pro=True):
	return self.match(o, labels, filtered=True, pro=pro)


    def matchUnfiltered(self, o, labels, pro=True):
	    if o in self.counts.keys() and labels in self.counts[o].keys():
		return self.counts[o][labels]
	    else:
		return 0

    def selectLabels(self, labels):
	import copy
	retList = copy.deepcopy(labels)
	STOP = False
	while not STOP:
	    choice = userNumberedList(retList, question="select label to exclude", getInt=False, cancelOK=True)
	    if choice == None:
		STOP = True
	    else:
		retList.remove(choice)
	return retList


    def getCount(self, o, labels, pro=True):
	labels = self.__labels2tuple__(labels)
	if o in self.counts.keys() and labels in self.counts[o].keys():
	    return self.counts[o][labels]
	else:
	    return 0

    def save(self, filename=None):
	if filename == None:
	    filename = self.filename
	out = open(filename, 'w')
	for o in self.otypes:
	    for l in self.counts[o]:
		out.write("%i %s %s\n" % (self.counts[o][l], o, repr(l)))
	out.close()
	writeln("saved label stats to %s" % self.filename)


    def load(self, filename=None):
	if filename == None:
	    filename = self.filename
	try:
	   lines = open(filename, 'r').readlines() 
	except:
	   writeln("could not open %s." % filename)
	   lines = ()

	for l in lines: 
	    l = l[:-1]
	    #linepattern = re.compile('([0-9]*) ([^ ]*) \((.*)\)', I)
	    linepattern = re.compile('([0-9]*) ([^ ]*) \((.*)\)')
	    mo = re.search(linepattern, l)
	    if mo <> None:
		freq = int(mo.group(1))
		otyp = mo.group(2)
		labels = self.__labels2tuple__(mo.group(3))
		self.set(otyp, labels, freq)

    def reset(self):
	for o in self.otypes:
	    for l in self.counts[o].keys():
		self.counts[o][l] = 0
	

    def __labels2tuple__(self, l):
	if type(l) == str:
	    l = re.sub("[\(\[\]\)\']", "", l)
	    l = re.sub(" ", "", l)
	    lst = re.split(",", l)
	elif type(l) == list:
	    lst = l
	elif type(l) == tuple:
	    lst = list(l)
	else:
	    raise Exception("wrong type: %s (%s)" % (repr(l), repr(type(l))) )
	for l in lst:
	    if l == '':
		lst.remove(l)
	return tuple(lst)
	    


    def __repr__(self):
	r = ""
	for o in self.otypes:
	    for l in self.counts[o]:
		 r += "%i %s %s\n" % (self.counts[o][l], o, repr(l))
	return r
