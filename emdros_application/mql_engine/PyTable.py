from string import atoi
from EmdrosPy import *
from emdros_application.utils.IOTools import *

class PyTable:

   def __init__(self, CTable = None, columns = None):
      self.col_width = {0:0}
      if columns is None:
	 if CTable is None:
	    self.py_table = []
	 else:
	    self.py_table = self.CTable2PyTable(CTable)
      else:
	 self.py_table = self.get_CTable_columns(CTable, columns)

      self.cur = 0

   def __repr__(self):
      repStr = ""
      repStr += '+'

      for c in range(0, len(self.col_width)):
	  for i in range(0, self.col_width[c]+3): repStr += '-'
	  repStr += '+'
      repStr += '\n'

      for row in self.py_table:
	 for c in range(0, len(self.col_width)):
	    cell = row[c]
	    if type(cell) == int:
		cell = str(cell)
	    col_width = self.col_width[c] + 2
	    repStr += '| '
	    repStr += cell.ljust(col_width)
	 repStr += '|\n'
	 #if row != self.py_table[-1]:
	    #repStr += '\n'

      repStr += '+'
      for c in range(0, len(self.col_width)):
	  for i in range(0, self.col_width[c]+3): repStr += '-'
	  repStr += '+'
      return repStr
	 
   def __getitem__(self, row):
      return self.py_table[row]


   def __setitem__(self, x, val):
      #p = list(self.py_table)
      #p[x] = val
      self.py_table[x] = val
      #del self.py_table
      #self.py_table = tuple(p)

   def __getslice__(self, min, max):
      return self.py_table[min:max]

   def __delslice__(self, min, max):
      del self.py_table[min:max]


   def getColumn(self, i):
      col = []
      for r in self.py_table:
	col.append(r[i])
      return col

   def getRow(self, i):
     row = []
     for c in self.py_table[i]:
	row.append(c)
     return row


   def __len__(self):
      return len(self.py_table)

   def first(self):
      self.cur = 0

   def hasNext(self):
      if len(self.py_table) == 0:
	 return 0
      return (self.cur < len(self.py_table) - 1)

   def next(self):
      r = self.pytable[self.cur]
      self.cur = self.cur + 1
      return r

   def cmp_by_id_d(self, row1, row2):
      return cmp(row1[0], row2[0])

      if row1[0] < row2[0]:
	 return -1
      if row1[0] == row2[0]:
	 return 0
      if row1[0] > row2[0]:
	 return 1

   def sort_by_id_d(self):
      self.py_table.sort(self.cmp_by_id_d)

   def cmp_by_monads(self, row1, row2):
      # sort on first monads; if these are equal, sort on last monads
      c = cmp(row1[1], row2[2])
      if c:
	 return c
      else:
	 return cmp(row1[2], row2[2])

      if row1[1] < row2[1]:
	 return -1

      if row1[1] == row2[1]:
	 if row1[2] < row2[2]:
	    return -1
	 if row1[2] == row2[2]:
	    return 0
	 if row1[2] > row2[2]:
	    return 1

      if row1[1] > row2[1]:
	 return 1

   def sort_by_monads(self):
      self.py_table.sort(self.cmp_by_monads)
    
   def cmp_by_col(self, row1, row2):
      if row1[self.sortColIndex] > row2[self.sortColIndex]:
	 return 1
      if row1[self.sortColIndex] < row2[self.sortColIndex]:
	 return -1
      if row1[self.sortColIndex] == row2[self.sortColIndex]:
	 return 0

   def sortbyCol(self,i):
      self.sortColIndex = i 
      self.py_table.sort(self.cmp_by_col)

   def get(self):
      return self.py_table

   def get_cell(self, row, col):
      return self.py_table[row][col]
    

   def app_row(self, row):
      self.py_table.append(row)

   def app_cell(self, cell):
      self.py_table[-1].append(cell)

   def CTable2PyTable(self, CTable): 
      self.py_table = []
      ti = CTable.iterator()
      while ti.hasNext():
	 col_counter = 0
	 row = []
	 ri = (ti.next()).iterator()
	 while ri.hasNext() :
	    cell = ri.next()
	    try:
	       cint = atoi(cell)
	    except:
	       row.append(cell)
	    else:
	       row.append(cint)
	    if not self.col_width.has_key(col_counter):
	       self.col_width[col_counter] = 0
	    if len(cell) > self.col_width[col_counter]:
	       self.col_width[col_counter] = len(cell)
	    col_counter += 1
	 self.py_table.append(tuple(row))
      #return tuple(self.py_table)
      return self.py_table


   def get_CTable_columns(self, CTable, columns): 
      pytbl = []
      ti = CTable.iterator()
      while ti.hasNext():
	 row = []
	 ri = (ti.next()).iterator()
	 for c in columns:
	    cell = ri.getColumn(c)
	    try:
	       cint = atoi(cell)
	    except:
	       row.append(cell)
	    else:
	       row.append(cint)
	 pytbl.append(tuple(row))
      #return tuple(pytbl)
      return pytbl

   def get_columns(self, columns):
      pytbl = []
      for r in self.py_table:
	 row = []
	 for c in columns:
	    row.append(r[c])
	 pytbl.append(tuple(row))
      #return tuple(pytbl)
      return pytbl

   def find(self, target):
      f = None
      for r in range(0,len(self.py_table)):
         for c in range(0,len(self.py_table[r])):
            if self.py_table[r][c] == target:
               if f is None:
                  f = []
               f.append((r,c))
      return f

      
   def merge(self, other):
      new_table = []
      id_d = 0
      i = 0
      r2 = None
      for r1 in self.py_table:
	 new_row = []
	 idd1 = r1[0]
	 mon1 = r1[1]
	 mon2 = r1[2]
	 if idd1 != id_d:
	    id_d = idd1
	    r2 = other[i]
	    i += 1
	    idd2 = r2[0]
	    if idd1 != idd2:
	       raise 'id_d mismatch (%d and %d) in PyTable.merge()' % (idd1, idd2)
	 for c in r1:
	    new_row.append(c)
	 for c in r2[1:]:
	    new_row.append(c)
	 new_table.append(tuple(new_row))
      del self.py_table
      #self.py_table = tuple(new_table)
      self.py_table = new_table


