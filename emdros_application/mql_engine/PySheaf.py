from emdros_application.utils.IOTools import *
import re
import copy
TAB = '   '

class PyObject:
   def __init__(self, matchedObject=None, monads=None, id_d=None, otype=None):
      if matchedObject is None:
         self.otype = otype
	 if monads is None:
	    monads = SetOfMonads()
	 elif type(monads) == str:
	    monads = SetOfMonads(monads)
         self.monads = monads
         self.id_d = id_d
         self.focus = False
         self.featureKeys = []
         self.sheaf = PySheaf()
         self.features = {}
	 self.featureStrings = {}
      else:
         self.otype = matchedObject.getObjectTypeName()
         self.monads = matchedObject.getMonads()
         self.id_d = matchedObject.getID_D()
	 if type(self.id_d) == str:
	    if self.id_d == 'nil': 
		self.id_d = None
	    else:
		self.id_d = long(self.id_d)
         self.focus = matchedObject.getFocus()
         self.featureKeys = []
         self.sheaf = None
         self.features = {}
	 self.featureStrings = {}
     
	 featureList = matchedObject.getFeatureList()
	 if featureList is not None:
	   fi = featureList.const_iterator()
	   i = 0
	   while fi.hasNext():
	      fKey = fi.next()
	      self.featureKeys.append(fKey)
	      EMdFVal = matchedObject.getEMdFValue(fKey)
	      val_type =  EMdFVal.getKind()

	      if val_type == kEVInt:
		  self.features[fKey] = EMdFVal.getInt()
		  self.featureStrings[fKey] = str(self.features[fKey])

	      elif val_type == kEVString:
		  self.features[fKey] = EMdFVal.getString()
		  self.featureStrings[fKey] = '"%s"' % self.features[fKey]

	      elif val_type == kEVID_D:
		  self.features[fKey] = EMdFVal.getID_D()
		  self.featureStrings[fKey] = str(self.features[fKey])

	      elif val_type ==kEVEnum:
		 val = matchedObject.getFeatureAsString(i)
		 self.featureStrings[fKey] = val
		 if val == 'nil': 
		     self.features[fKey] = None
		 if re.match("true", val) or re.match("false", val):
		     self.features[fKey] = (val == "true") 
		 else:
		     self.features[fKey] = val

	      elif val_type == kEVListOfID_D:
		 self.features[fKey] = matchedObject.getEMdFValue(fKey).getIntegerList().getAsVector()
		 self.featureStrings[fKey]=self.List2Str(self.features[fKey])

	      elif val_type == kEVListOfInteger:
		  val = matchedObject.getFeatureAsString(i)
		  self.features[fKey] = self.Str2List(val)
		  self.featureStrings[fKey] = val
	      else:
		  raise Exception('unknown EMdFKind %d for feature %s:\n%s' % \
				   (val_type, fKey, self.__repr__()))
	      i += 1
	 if not matchedObject.sheafIsEmpty():
	    self.sheaf = PySheaf(matchedObject.getSheaf())

	 
   def Str2List(self, val):

      if val == '()':
	 return []

      vals = re.sub("[\(\)]", "", val)

      if re.search(',', val) is None:
	 return [re.sub("[()]", "", val),]

      return re.split("," , vals)

   def loadFeatures(self, feat_list, mql):
      q = "GET FEATURES %s" % feat_list[0]
      for feat in feat_list[1:]:
	 q = "%s, %s" % (q, feat)
      q = "%s FROM OBJECTS WITH ID_DS = %d" % (q, self.id_d)
      q = "%s [%s] GO" % (q, self.otype)
      mql.doQuery(q)
      table = mql.getPyTable()




   def List2Str(self, lst):
       ret = re.sub("[\"\']", "", repr(tuple(lst)))
       ret = re.sub(",\)[ ]*$", ")", ret)
       return ret

   def appendPyObject(self, obj):
      if obj is not None:
	 self.sheaf.appendPyObject(obj)
	 if self.monads is None:
	    self.monads = obj.monads
	 else:
	    self.monads.unionWith(obj.monads)

   def appendPyStraw(self, straw):
      if straw is not None:
	  self.sheaf.appendPyStraw(straw)

   def refreshMonads(self):
      self.sheaf.refreshMonads()
      # NB: This does not refresh the monads of the object itself,
      # only of its internal sheaf. 

   def copy(self):
      newObject = PyObject()
      newObject.otype = copy.deepcopy(self.otype)
      newObject.monads = SetOfMonads(self.monads)
      newObject.id_d = copy.deepcopy(self.id_d)
      newObject.focus = copy.deepcopy(self.focus)
      newObject.featureKeys = copy.deepcopy(self.featureKeys)
      newObject.sheaf = copy.deepcopy(self.sheaf)
      newObject.features = copy.deepcopy(self.features)
      return newObject

   def toXML(self, indent=""):
      newindent = indent + "   "
      r = '%s<%s>\n%sid_d=%s\n' % (indent, self.otype, newindent, 
                                   repr(self.id_d) )
      if self.monads is not None and not self.monads.isEmpty():
	    r += '%smonads="%s"\n' % (newindent, self.monads.toString())
      r += '%sfocus="%s"\n'  % (newindent, repr(self.focus))
      for f in self.features.keys():
	 r += '%s%s="%s"\n' % (newindent, f, self.featureStrings[f])
      if self.sheaf is not None:
	 if type(self.sheaf) == list: # self.flatten() has been used
	    for obj in self.sheaf:
		r += obj.toXML(indent=newindent)
         else:
	    r += self.sheaf.toXML(newindent) 
      r += indent + "</%s>\n" % self.otype
      return r


   def toString(self, indent=""):
      newindent = indent + "   "
      r = "%s<%s>\n%sid_d=%s" % (indent, self.otype, newindent, 
                                   repr(self.id_d) )
      if self.monads is not None and not self.monads.isEmpty():
	    r += self.monads.toString() 
      r += " focus=" + repr(self.focus) + "\n"
      for f in self.features.keys():
         r += newindent + f + "="  + self.featureStrings[f] + '\n'
         #r += newindent + f + "="  + repr (self.features[f]) + '\n'
      if self.sheaf is not None:
	 if type(self.sheaf) == list: # self.flatten() has been used
	    r += repr(self.sheaf)
         else:
	    r += self.sheaf.toString(newindent) 
      r += indent + "</%s>\n" % self.otype
      return r


   def getCSVCols(self, col_heads=[]):
      cols = copy.deepcopy(col_heads)
      for f in sorted(self.features.keys()):
	 if self.isListValue(self.features[f]):
	    for v in sorted(self.features[f]):
	       if v not in cols: 
		  cols.append(v)
	 elif f not in cols:
	    cols.append(f)
      return cols
	    
   def toCSV(self, do_header=False, col_heads=[]):
      ret = ""
      if do_header:
	 ret += 'otype, id_d'
	 for f in col_heads:
	    ret += ', %s' % f
         ret += '\n'
      ret += self.otype + ', '
      ret += str(self.id_d) 
      for col in col_heads:
	 ret += ', '
	 if col in self.features.keys():
	    ret += '%s' % self.featureStrings[col]
	 else:
	    for f in sorted(self.features.keys()):
		if self.isListValue(self.features[f]):
		    for v in self.features[f]:
			if v == col:
			    ret += '%s' % v
			    break
      return ret


   def __repr__(self):
      return self.toString()
      #return self.toMQL()

   def getMonads(self):
      return self.monads

   def hasFeature(self, f):
      return (f in self.features.keys())

   def addFeature(self, f, v):
      self.featureKeys.append(f)
      self.features[f] = v
      if type(v) == int:
	 self.featureStrings[f] = repr(v)
      elif type(v) in (list, tuple):
	 self.featureStrings[f] = self.List2Str(v)
      elif type(v) == str:
	 self.featureStrings[f] = v
      else:
	 exitOnError("feature value of unrecognized type: %s" % v)


   def isListValue(self,v):
      return type(v) == list

   def OldisListValue(self,v):
      if type(v) != str:
	 return False
      else:
	 return (re.search("^\([A-Za-z_, ]*\)$", v) is not None)


   def featureType(self, f):
      if not self.hasFeature(f):
	 return None
      elif self.isListValue(self.features[f]):
	 return 'listval'
      else:
	 return type(self.features[f])
    
   def hasValue(self, f, v):
      if self.hasFeature(f) and self.features[f] == v:
	 return True
      else:
	 return False

   def hasListValue(self, f, v):
      l = self.features[f]
      if type(l) == list:
	 return (v in l)
      else:
	 return False



   def addListValue(self, f, v):
      #if v == '_no_foot_cstr':
	 #import pdb; pdb.set_trace()
      if not self.features.has_key(f):
	 self.features[f] = []
      if type(self.features[f]) <> list:
	 raise Exception('PyObject.addListValue(f, v): feature f (%s) must be a list value' % f)

      if v not in self.features[f]:
	 self.features[f].append(v)
	 self.featureStrings[f] = self.List2Str(self.features[f])
	 return True

   def OldaddListValue(self, f, v):
      if type(v) != str:
	 v = str(v)
      if not self.features.has_key(f):
	 self.features[f] = "()"
      oldlist = self.features[f]
      if oldlist == "()":
	 newlist = "(%s)" % v
      elif not re.search("[(,]%s[),]" % v, oldlist):
	 newlist = re.sub("\)", ",%s)" %v, oldlist)
      else: # the value already is in the list -> leave list as is
	 newlist = oldlist
	 #raise Exception('Problem in PyObject.addListValue("%s, %s"), probably duplicate object.' % (f, v))
      self.features[f] = newlist.strip()
	 

   def delListValue(self, f, v):
      if type(self.features[f]) <> list:
	 return False
      
      self.features[f].remove(v)


   def OlddelListValue(self, f, v):
      if type(v) != str:
	 v = str(v)

      if not self.features.has_key(f):
	 return 
      oldlist = self.features[f]
      if oldlist == "()":
	 return
      elif not re.search("[(,]%s[),]" % v, oldlist):
	 return
      else: # the value already is in the list
	 newlist = re.sub('(%s)'  % v, '()', oldlist)
	 newlist = re.sub('%s,'  % v, '', oldlist)
	 newlist = re.sub(',%s)' % v, ')', oldlist)
      self.features[f] = newlist.strip()

	 
   def getValueList(self, f):
      if type(self.features[f]) <> list:
	 return None

      return self.features[f]


   def OldgetValueList(self, f):
      val = self.features[f]
      if not self.isListValue(val):
	 return None
      else:
	  if re.search("[a-zA-Z_]", val): # list of identifiers, not of integers
	      val = re.sub("(?P<token>[a-zA-Z_]+)", "'\g<token>'", val)
	  return list(eval(val))


   def containsFocus(self): # objects

      if self.focus:
	 return True
      elif self.sheaf is None:
	 return False
      else:
	 return self.sheaf.containsFocus()


   def toCreateMQL(self):
      q = "CREATE OBJECT FROM %s\n" % self.monads.toString()
      q += '[%s' %self.otype
      if self.focus:
	 q += ' focus := true;'
      if self.featureKeys:
	  q += '\n'
      for f in self.featureKeys:
	 q += '%s%s := %s;\n' % (TAB, f, self.featureStrings[f])
      q += ']\nGO'
      return q


   def toMQL(self, tab = "", create=False, outer=True):  # object
      if create:
	 return self.toCreateMQL()

      if outer:
	 q = "SELECT ALL OBJECTS IN %s WHERE\n" % self.monads.toString()
      else:
	q = ''

      # OBJECT TYPE PLUS EXTRA INFO
      q += '%s[%s' %(tab, self.otype)

      if self.focus:
	 q += ' focus'

      if not outer:
	 q += "   // monads =%s\n" %(self.monads.toString())

      q += tab + TAB + 'self = %d' % self.id_d

      for f in self.featureKeys:


	 val = self.features[f]
	 valtype = self.featureType(f)
	 if valtype == 'listval':
	     #listvals = self.expandListValues(f)
	     #for v in listvals:
             for v in val:
		 if v == '': continue
		 if val.index(v) > 0:
		 #if listvals.index(v) > 0:
		    q += '\n'
		 q += '%sAND %s HAS %s' % (tab + TAB, f, v)

	 else:
	    q += '\n' + tab + TAB + 'AND '
	    if valtype == str:
		val = '%s' % val
	    else:
	       val = repr(val)
	    #q += '%s%s %s %s' % (tab + TAB, f, operator, val)
	    q += '%s = %s' % (f, val)

      if self.sheaf is not None:
	 q += self.sheaf.toMQL(tab=tab+TAB, outer=False)
      q += "\n%s]" % tab

      if outer:
	 q += "\nGO"
      return q


   def feature(self, key):
      return self.features[key]
    
   def feat(self, key):
      return self.features[key]
   
   def featureString(self, key):
      return self.featureStrings[key]
   
   def featStr(self, key):
      return self.featureStrings[key]

   # temporarily disabled, to spot problematic use
   def __getitem__(self, key):
      if self.features.has_key(key):
	  return self.features[key]
      else:
	 raise Exception('no feature %s [%s id_d=%d]' % (key, self.otype, self.id_d))


   def __setitem__(self, key, val):
    self.features[key] = val
    if type(val) == str:
	self.featureStrings[key] = val
    elif type(val) == int:
	self.featureStrings[key] = str(val)
    elif type(val) == bool:
	if val:
	    self.featureStrings[key] = 'true'
	else:
	    self.featureStrings[key] = 'false'
    else:
	try:
	    self.featureStrings[key] = val.toString()
	except:
	    raise Exception("unknown value type for %s = %s" % (key, str(val)))

class PyStraw:
   def __init__(self):
      self.objects = []
      self.monads = SetOfMonads()

   def appendPyObject(self, o):
      if o is not None:
	  self.objects.append(o)
	  self.monads.unionWith(o.monads)

   def len(self):
      return len(self.objects)

   def getMonads(self):
      return self.monads

   def refreshMonads(self):
      self.monads = SetOfMonads()
      for o in self.objects:
	 self.monads.unionWith(o.monads)

   def __getitem__(self,key):
      if not self.objects:
         return None
      else:
         return self.objects[key]

   def __len__(self):
      return len(self.objects)

   def index(self, obj):
       return self.objects.index(obj)

   def toString(self, indent=""):
      newindent = indent + "   "
      r = indent + "<straw>\n"
      for o in self.objects:
         r += o.toString(newindent)
      r += indent + "</straw>\n"
      return r

   def toXML(self, indent=""):
      newindent = indent + "   "
      r = indent + "<straw>\n"
      for o in self.objects:
         r += o.toXML(newindent)
      r += indent + "</straw>\n"
      return r


   def toCSV(self, do_header=False, col_heads=[]):
      ret = ""
      ret += self.objects[0].toCSV(do_header, col_heads=col_heads)
      for o in self.objects[1:]:
	 ret += '\n%s' % o.toCSV(do_header=False, col_heads=col_heads)
      return ret

   def __repr__(self):
      return self.toString()

   def containsFocus(self): # straw
      if not self.objects:
	 return None
      else:
	 for obj in self.objects:
	    if obj.containsFocus():
	       return True


   def filterFocus(self): # straw
      new_straw = PyStraw()

      for obj in self.objects:
	 if obj.focus:
	    new_straw.appendPyObject(obj)
	 elif obj.containsFocus:
	    if obj.sheaf and obj.sheaf.containsFocus():
		int_sheaf = obj.sheaf.filterFocus()
		for s2 in int_sheaf:
		    for o2 in s2:
			new_straw.appendPyObject(o2)
      return new_straw
	 


   def toMQL(self, tab = "", create=False, outer=True): # straw

      def adjacent(obj1, obj2):
	 return  obj2.monads.first() == (obj1.monads.last() + 1)

      if create:
	 return self.toCreateMQL()

      q = ''

      if not self.objects:
	 return ''

      for obj in self.objects:
	 if (not outer) or (self.objects.index(obj) > 0):
	    q += '\n'

	 i = self.objects.index(obj)
	 if i > 0:
	    if not adjacent(self.objects[i-1], obj):
	       if not outer:
		   q += tab + '..\n'
	       else:
		  q += '\n'
	 q += obj.toMQL(tab, outer=outer)

      return q


   def getRecObjectList(self):
      object_list = []
      for straw in self.straws:
	 for obj in straw:
	    object_list.append(obj)
	    if obj.sheaf is not None:
	       int_obj_list = obj.sheaf.getRecObjectList()
	       for obj2 in int_obj_list:
		   object_list.append(obj2)
      return object_list


   def toCreateMQL(self):      
      q = ''
      object_list = self.getRecObjectList()
      for obj in object_list:
	 if object_list.index(obj) > 0:
	    q += '\n\n'
	 q += obj.toCreateMQL()
      return q
      

class PySheaf (Sheaf):

   def __init__(self, sheaf=None, PyMonads=False, spin=None):
      self.straws = []
      if PyMonads==True:
         self.monads = PySetOfMonads(SetOfMonads())
      else:
         self.monads = SetOfMonads()
      self.focusList = None

      if sheaf is not None:
         shi = sheaf.const_iterator()
         while shi.hasNext():
            if self.straws is None: self.straws = []
            straw = PyStraw()
            si = (shi.next()).const_iterator()
            while si.hasNext():
	       if spin is not None: spin.next()
               o = si.next()
               straw.appendPyObject(PyObject(o))
            self.appendPyStraw(straw)

   def len(self):
      return len(self.straws)
     
   def appendPyObject(self, obj, insert=False):
      # the new object should come inside its own straw,
      # unless insert == True, in which case the object is
      # inserted into the last already existing straw

      if obj:
	 if (self.straws == []) or (not insert):
	    self.appendPyStraw(PyStraw())

	 self.straws[-1].appendPyObject(obj) # append to last straw of sheaf
	 self.straws[-1].monads.unionWith(obj.monads)
	 self.monads.unionWith(obj.monads)


   def appendPyStraw(self, straw):
      self.straws.append(straw)
      self.monads.unionWith(straw.monads)

   def replacePyStraw(self, i, straw):
      if self.straws == []:
	self.appendPyStraw(straw)
      else:
	  self.straws[i] = straw
	  self.refreshMonads()

   def getMonads(self):
      return self.monads

   def refreshMonads(self):
      self.monads = SetOfMonads()
      for s in self.straws:
	 s.refreshMonads()
	 self.monads.unionWith(s.monads)
	 

   def isFlatSheaf(self):
      return self.flat

   def isEmpty(self):
      return not self.straws

   def __getitem__(self,key):
      return self.straws[key]


   def copy(self):
      newsheaf = PySheaf()
      for straw in self.straws:
	 newsheaf.appendPyStraw(straw)
      return newsheaf


   def toXML(self, indent= ""):
      newindent = indent + "   "
      if self.straws is None:
         return 'None'
      else:
         r = indent + "<sheaf>\n"
      for s in self.straws:
         r += s.toXML(newindent)
      return r + "%s</sheaf>\n" % indent

   def toString(self, indent= ""):
      newindent = indent + "   "
      if self.straws is None:
         return 'None'
      else:
         r = indent + "<sheaf>\n"
      for s in self.straws:
         r += s.toString(newindent)
      return r + "%s</sheaf>\n" % indent



   def getCSVCols(self, col_heads=[]):
      cols = copy.deepcopy(col_heads)
      for straw in self.straws:
	 for obj in straw:
	    cols = obj.getCSVCols(col_heads=cols)
      return cols

   def toCSV(self, do_header=True, col_heads=[]):
      ret = ""
      if do_header:
	 col_heads = self.getCSVCols(col_heads=copy.deepcopy(col_heads))
      ret += self.straws[0].toCSV(do_header, col_heads=col_heads)
      for s in self.straws[1:]:
	 ret += '\n%s' % s.toCSV(do_header=False, col_heads=col_heads)
      return ret


   def __repr__(self):
      return self.toString()

   def __len__(self):
      return len(self.straws)

   def insert(self, i, straw):
      self.straws.insert(i, straw)
      self.monads.unionWith(straw.monads)


   def pop(self, i):
      self.monads.difference(self.straws[i].monads)
      return self.straws.pop(i)


   def noOfObjects(self):
      n = 0
      for s in self.straws:
         n += len(s)
      return n


   def containsFocus(self): # sheaf
      if self.straws:
	  for straw in self.straws:
	     if straw.containsFocus():
		return True
      return False

	    
   def filterFocus(self, outer=True):  # sheaf

	if self is None:
	    return None

	if not self.containsFocus():
	    if outer:
	       return self

	else:
	    new_sheaf = PySheaf()
	    for straw in self:
		if straw.containsFocus():
		    new_sheaf.appendPyStraw(straw.filterFocus())
	    return new_sheaf


   def toMQL(self, tab='', outer=True, create=False):  # sheaf
      q = ''
      for straw in self.straws:
	 if self.straws.index(straw) > 0:
	    q += '\n'
	 q += straw.toMQL(tab=tab, outer=outer, create=create)
      return q

   def flatten(self):
      flat_list = []
      for straw in self.straws:
	 for obj in straw:
	    if obj.sheaf is not None:
	       obj.sheaf = obj.sheaf.flatten()
	    flat_list.append(obj)
      return flat_list


def test1(mql):
   q = 'SELECT ALL OBJECTS WHERE [verse last] GO'
   monads = mql.getPySheafFromQuery(q).monads.toString()
   q = "GET OBJECTS HAVING MONADS IN %s [word GET ALL] GO" % monads
   if mql.doQuery(q):
	sheaf = mql.getFlatPySheaf()
	for obj in sheaf[0]:
	    if obj is not None:
		print(obj.toMQL(create=True) + '\n')
		if obj != sheaf[-1]:
		   print('')

def test2(mql):
   q =  "SELECT ALL OBJECTS WHERE\n"
   q += "[chapter chapter < 5\n"
   q += "   [verse focus verse = 5\n"
   q += "       [phrase focus last\n"
   q += "           [word first get g_word, lex, vt]\n"
   q += "           [word focus get g_word, lex, vt]\n"
   q += "       ]\n"
   q += "   ]\n"
   q += "   [verse verse = 6\n"
   q += "       [word focus first get g_word]\n"
   q += "       [word focus get g_word, lex, vt]\n"
   q += "   ]\n"
   q += "]\n"
   q += "GO\n"

   print("query:")
   print(q)
   if mql.doQuery(q):
      sheaf = mql.getPySheaf().filterFocus()
      print("results:")
      print(sheaf)
      print(sheaf.toMQL())
      print("done.")
   else:
      writeln('query failed.')

def test3(mql):
   q =  "SELECT ALL OBJECTS WHERE\n"
   q += "[verse first\n"
   q += "   [verseline\n"
   q += "       [colon first]\n"
   q += "       [colon focus]\n"
   q += "   ]\n"
   q += "]\n"
   q += "GO\n"
   print("query:")
   print(q)
   if mql.doQuery(q):
      sheaf = mql.getPySheaf()
      fSheaf = sheaf.filterFocus()
      print("unfiltered:")
      print(sheaf.toMQL())
      print("filtered:")
      print(sheaf.toMQL())
      print("done.")
   else:
      writeln('query failed.')

def test4(mql):
   q = 'SELECT ALL OBJECTS WHERE\n'
   q+= '[poem first\n'
   q+= '[strophe first [colon focus first get prosodic_labels] ]\n'
   q+= '..\n'
   q+= '[strophe focus last get prosodic_labels [word last get pdp, vt, prosodic_labels]]\n'
   q+= ']\n'
   q+= 'GO'
   if mql.doQuery(q):
      sheaf =  mql.getPySheaf()
      filtered_sheaf = sheaf.filterFocus()
      print sheaf.toMQL()
      print '##########' 
      print filtered_sheaf.toMQL()

if __name__ == "__main__":

   from MQLEngine import *
   mql = MQLEngine(database= 'threni_hjb', usr='hjb', pwd='aap')

   q = ''
   for l in sys.stdin:
     q += l

   mql.doQuery(q)
   pyS = PySheaf(mql.getSheaf()).filterFocus()
   obj = pyS[0][0] 
   print obj
   obj.loadFeatures(("typ", "mother", "prosodic_labels", "syntactic_labels"), mql)
   print obj
   for l in obj['prosodic_labels']:
    print l,
