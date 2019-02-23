from EmdrosPy import *
from MQLEngine import *
from QueryList import *

class PyMonadsIterator:

   def __init__(self, SoM, name='my_monad_set'):
      self.monads = SoM
      self.index = 0

   def hasNext(self):
      if self.index < (len(self.monads.monads)):
         return True
      else:
         return False

   def next(self):
      if self.hasNext():
         ret = self.monads[self.index]
         self.index += 1
      else:
         ret = None
      return ret

   def reset(self):
      self.index = 0


class PySetOfMonads:

   def __init__(self,SoM=None, query=None,query_files=None, filterFocus=False,
		name=None, mql=None):

      import time
      self.monads = []
      if name is None:
	name = 'tmp_%.0f' % time.time()
      self.name = name

      if SoM is not None:
         self.set(SoM)
      elif query_files is not None:
	 self.set(self.byQueryFiles(query_files, filterFocus=filterFocus))
      elif query is not None:
	 self.set(self.byQuery(query, mql=mql, filterFocus=filterFocus))

   def set(self, SoM):
      i = SoM.const_iterator()
      while i.hasNext():
         mse = i.next()
         self.monads.append( [mse.first(), mse.last()] )

   def byQuery(self, q, mql=None, filterFocus=False):
      if mql is None:
	 mql = MQLEngine('bhs4' , 'emdf', 'changeme')
      if mql.doQuery(q):
	if filterFocus:
	    return(mql.getPySheaf().filterFocus().monads)
	else:
	    return(mql.getPySheaf().monads)
      else:
	 return SetOfMonads()


   def byQueryFiles(self, file_names, mql=None, filterFocus=False):
      SoM = SetOfMonads()
      if type(file_names) == str:
	file_names = [file_names,]
      for fN in file_names:
	 for q in QueryList(fN):
	    SoM.unionWith(self.byQuery(repr(q), filterFocus=filterFocus))
      return SoM
	 

   def __getitem__(self, mse, mon=None):
      if mon == None:
         return self.monads[mse]
      else:
         return self.monads[mse][mon]

	 
   def __len__(self):
      return len(self.monads)


   def const_iterator(self):
      return PyMonadsIterator(self)

   def first(self):
      return self.monads[0][0]

   def last(self):
      return self.monads[-1][-1]

   def contains(self,m):
      for mse in self.monads:
         if m >= mse[0] and m <= mse[1]:
            return True
      return False

   def unionWith(self, PyM2):
      if PyM2 <> None:
         for mse in PyM2:
            self.monads.append(mse)
      return self


   def toString(self):
      repStr = '{'
      for mse in self.monads:
         repStr += repr(mse[0])
         if mse[0] <> mse[1]:
            repStr += '-%s' % repr(mse[1])
         if mse <> self.monads[-1]:
            repStr += ','
      return repStr + '}'

   def toList(self):
      lst = []
      for mse in self.monads:
	 for m in range(mse[0], mse[1]+1):
	    lst.append(m)   
      return lst

   def __repr__(self):
      return self.toString()

   def __str__(self):
      return self.toString()

   def commit(self, name=None, mql=None):
	if name is None:
	    name = self.name
	q = "CREATE MONAD SET %s WITH MONADS = %s GO" % (name, self.toString())
	if mql is not None:
	    return mql.doQuery(q)
	else:
	    writeln(q)
	    return True

   def drop(self, name=None, mql=None):
	if name is None:
	    name = self.name
	q = "DROP MONAD SET %s GO" % name
	if mql is not None:
	    return mql.doQuery(q)
	else:
	    writeln(q)
	    return True

def test():
   SoM = SetOfMonads(1,3)
   SoM.unionWith(SetOfMonads(5,6))
   SoM.unionWith(SetOfMonads(9,9))
   SoM.unionWith(SetOfMonads(11,14))
   PyM = PySetOfMonads(SoM)
   print 'whole monad set:', PyM
   print 'first and last:', PyM[0][0], PyM[-1][-1]
   print 'subsets',
   for mse in PyM:
      print mse[0],
      if mse[0] <> mse[1]: 
         print '-', mse[1], ',',
      else: print ',',
   print
   print 'testing the iterator'
   i = PyM.const_iterator()	 
   while i.hasNext():
      print i.next()
   print 'contains 13', PyM.contains(13)
   print 'contains 10', PyM.contains(10)

if __name__ == '__main__':
   import sys
   PyM = PySetOfMonads(query_files=sys.argv[1:], filterFocus=True)
   print PyM
   #PyM.commit()
   #PyM.drop()

