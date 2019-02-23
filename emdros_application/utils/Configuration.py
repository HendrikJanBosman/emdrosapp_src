from emdros_application.syscfg.config import *
from re import *
from types import *
from Paths import *
from IOTools import *
#from Options import *


class Configuration:
    
   def __init__(self, filename=None, name=None, verbose=False, kernel=None):

      if kernel is None:
	  import importlib
          self.kernel = importlib.import_module(DEFAULT_KERNEL)
      else:
         self.kernel = kernel

      try:
	 self.CFG_DIR = self.kernel.CFG_DIR
      except:
         self.CFG_DIR = emdros_application.syscfg.config.CFG_DIR
      
      #self.CFG_EXT = emdros_application.syscfg.config.CFG_EXT
      self.CFG_EXT = CFG_EXT
      self.verbose = verbose
      self.filename = filename
      self.name = name

      if filename is not None:
	 self.readConfFile(self.filename)
      else:
         if self.name is not None:
            self.filename = self.name
         else:
            self.filename = "generic"
            self.name = filename
	 self.conf = {}
      self.set('cfg_src', self.filename)


   def readConfFile(self, fileName=None):

      def valType(val):
	 if val is None: return Nonconfig
	 try:                               # try integer
	    vt = int(val)
	 except:
	    if re.search('^\"[-]?[0-9]*\"$', val) or \
	       re.search("^\'[-]?[0-9]*\'$", val): # string repr of integer
	       vt = val[1:-1]
	    elif val in ('True', 'true', 'TRUE'):     # else, try boolean
	       vt = True
	    elif val in ('False', 'false', 'FALSE'):
	       vt = False
	    else:
	       vt = val                      # else, keep as a string
	 return vt

	    
      subpattern = compile('([^ \t\n=]+)\s*=\s*([^ \t\n\.]+)\.([^ \t\n]+)', I)
      assignmentpattern = compile('([^ \t\n=]*)\s*=\s*([^ \t\n,]*)', I)

      self.conf = {}

      self.filename = fileName
      if self.verbose: write('opening config file %s: ' % \
		       addPathAndExt(self.filename, './', self.CFG_EXT))
      try:
	 cf = open("%s" % addPathAndExt(self.filename, './', self.CFG_EXT), 'r') # try in pwd
	 if self.verbose: writeln('OK')
      except:
	 if self.verbose: writeln('failed')
	 self.filename =  addPathAndExt(self.filename, self.kernel.CFG_DIR, CFG_EXT)
	 if self.verbose: write('opening config file %s: ' % self.filename)
         try:
            cf = open(self.filename, 'r')       # then, try standard config dir
	    if self.verbose: writeln('OK')
         except:
	    if self.verbose: writeln('failed')
            raise Exception('unable to open %s' % self.filename)


      for l in cf:
         l = l.strip()
	 l = sub("#.*$", "", l)
	 if l == "":
	    continue
         mo = search(subpattern, l)
         if mo != None:
            key = mo.group(1)       # e.g., reference_feature
            subkey = mo.group(2)    # e.g., verse
            value  = mo.group(3)    # e.g., verse_label
            if self.conf.has_key(key):
               tmp = self.conf[key]
	       if type(tmp) == TupleType:
		  raise Exception("error in config file at key '%s' (probably a missing subkey)\nfix %s" % (key, self.filename))
               if tmp.has_key(subkey):
                  t = list(tmp[subkey])
                  t.append(valType(self.do_constants(value)))
                  tmp[subkey] = tuple(t)
               else:
                  tmp[subkey] = (valType(self.do_constants(value)),) # HJB
               self.conf[key] = tmp
               del tmp
            else:
               self.conf[key] = {subkey : (valType(self.do_constants(value)),)}
         else:
            del mo
            mo = search(assignmentpattern, l)
            if mo != None: 
               key   = self.do_constants(mo.group(1))
               value = valType(self.do_constants(mo.group(2)))
               if self.conf.has_key(key):
                  tmplist = list(self.conf[key])
                  tmplist.append(value)
                  self.conf[key] = tuple(tmplist)
               else : self.conf[key] = (value,)
               continue
      cf.close()

   def __repr__(self):
      def repr_entry(parent, k, l):
	 maxlen = 60
	 indent = len(parent) + len(k) + 3
	 line = ''
	 rep  = '%s%s = ' % (parent, k)
	 for e in l:
	    val = repr(e)
	    if len(line  + val + ', ') > maxlen:
	       rep += line + '\n' + ' '.ljust(indent)
	       line = ''
	    line += val + ', '
	 rep += line[:-2]
	 return rep

      rep = underlined(self.conf['cfg_src'][0]) + '\n'
      for k in self.conf.keys():
	 if k == 'cfg_src': continue
	 parent_key = ''
	 if type(self.conf[k]) <> dict:
	    rep += repr_entry('', k, self.conf[k])
	    if k <> self.conf.keys()[-1]:
	       rep += '\n'
	 else:
	    for sk in self.conf[k].keys():
	       rep += repr_entry('%s (' % k, '%s)' % sk, self.conf[k][sk]) + '\n'
	 
      return re.sub("\n$", "", rep)

   def list(self): 
      r = '%s\n' % self.filename
      for k in self.keys():
	 if self.has_subkeys(k):
	    for s in self.subkeys(k):
	       r += '%s.%s: %s\n' % (k,s, self.get(k,s))
	 else: r += '%s : %s\n' % (k, self.get(k))
      return r


   def __getitem__(self, key):
      return self.conf[key]

   def keys(self):
      return self.conf.keys()

   def subkeys(self, key):
      if self.has_subkeys(key):
	 return self.conf[key].keys()
      else:
	 return None

   def has_key(self, key, subkey=None):
      if subkey == None:
         return self.conf.has_key(key)
      else:
         if self.conf.has_key(key):
            if self.has_subkeys(key):
               return (self.conf[key]).has_key(subkey)
            else:
               return False

   def hasKey(self, key=None, subkey=None):
      return self.has_key(key, subkey)

   def has_subkeys(self, key):
      return (type(self.conf[key]) == dict)

   def has(self, key, value):
      if self.conf.has_key(key):
         return value in self.conf[key]
      else:
         return False

   def addKey(self, key, subkey=None):
      if not self.hasKey(key, subkey):
	 if subkey is None:
	    self.conf[key] = []
	 else:
	    self.conf[key] = {subkey : []}


   def set(self, key, value, subkey = None, uniq=True):
      if not self.hasKey(key, subkey):
	 self.addKey(key, subkey)
      if subkey is None:
	 self.conf[key] = [value]
      else:
	 self.conf[key][subkey] = [value]


   def set_multi(self, key, lst, subkey=None):
      if not self.has_key(key):
	self.conf[key] = []
      for x in lst:
	 if not self.has(key, x):
	     self.append(key, x, subkey)

   def copy_key(self, key, other):
      if other.has_key(key):
	 self.conf[key] = other.conf[key]

   def append(self, key, value, subkey = None, uniq=True):
      if not self.hasKey(key, subkey):
	 self.set(key, value, subkey, uniq)
      elif subkey is None:
	self.conf[key].append(value)
      else:
	self.conf[key][subkey].append(value)

   def get(self, key, subkey=None):
      g = self.get_multi(key, subkey)
      if g == None:
	return None
      else:
          return g[0]
    
   def getmulti(self, key, subkey = None):
      return self.get_multi(key, subkey)    
    
   def getMulti(self, key, subkey = None):
      return self.get_multi(key, subkey)    

   def get_multi(self, key, subkey = None):
      if not self.has_key(key):
         return None
      elif subkey == None:
	 return self.conf[key]
      elif not self.hasKey(key, subkey):
	 return None
      else:
	 return self.conf[key][subkey]


   def do_update(self, orig_dict, new_dict):
	import collections
	for key, val in new_dict.iteritems():
	    if isinstance(val, collections.Mapping):
		tmp = self.do_update(orig_dict.get(key, { }), val)
		orig_dict[key] = tmp
	    elif isinstance(val, list):
		orig_dict[key] = (orig_dict[key] + val)
	    else:
		orig_dict[key] = new_dict[key]
	return orig_dict


   def mergeConfiguration(self, other):
      self.conf = self.do_update(self.conf, other.conf)

   def overrideWith(self, other):

      for k in other.keys():

         if k == 'cfg_src':
            continue

         elif not self.has_key(k):
            self.conf[k] = other.conf[k]

         elif other.has_subkeys(k):
            for sk in other.conf[k].keys():
               if other.get(k, sk) is not None:
                  self.set(k, other.get(k, sk), sk)

         elif other.get(k) is not None:
            self.conf[k] = other[k]



   def do_constants(self, token):

      t = token

      VAR = search("{([^}]*)}", t)
      #i = 1
      while VAR <> None:
         myvar = VAR.group(1)
         t = sub('{%s\}' % myvar, self.conf[myvar], t)
         VAR = search("{([^}]*)}", t)

      t = sub('SPACE', ' ', t)
      t = sub('~', ' ', t)
      t = sub('`', '.', t)     # use ` as substitute for period
      t = sub('COMMA', ',', t)
      t = sub('COMMA_SPACE', ', ', t)
      t = sub('COLON', ':', t)
      t = sub('COLON_SPACE', ': ', t)
      t = sub('PERIOD', '.', t)
      t = sub('TAB', '\t', t)
      t = sub('NEWLINE', '\n', t)
      t = sub('DASH', '-', t)
      t = sub('HASH', '#', t)
      t = sub('OPENPARENTHESIS', '\(', t)
      t = sub('CLOSEPARENTHESIS', '\)', t)
      t = sub('OPENBRACE', '{', t)
      t = sub('CLOSEBRACE', '}', t)
      t = sub('BACKSLASH', '\\\\', t)
      t = sub('QUOTES', '"', t)
      t = sub('QUOTE', "'", t)
      t = sub('EQUALS', '=', t)
      t = sub('NIL', '', t)
      #t = sub('NONE', '', t)
      if t == 'NONE': t = None
      return t


   def encode(self, token):
      t = token
      if type(token) in (int, bool):
	 t = str(token)
      else: 
	 t = sub(' ', 'SPACE', t)
	 t = sub(':', 'COLON', t)
	 t = sub(': ', 'COLON_SPACE', t)
	 t = sub('\.', 'PERIOD', t)
	 t = sub('\t', 'TAB', t)
	 t = sub('\n', 'NEWLINE', t)
	 t = sub('#', 'HASH', t)
	 t = sub('\(', 'OPENPARENTHESIS', t)
	 t = sub('\)', 'CLOSEPARENTHESIS', t)
	 t = sub('\\\\', 'BACKSLASH', t)
	 t = sub('"', 'QUOTES', t)
	 t = sub('=', 'EQUALS', t)
	 t = sub(',$', ',NIL', t)
	 t = sub(';$', ';NIL', t)
	 #t = sub('NONE', '', t)
	 if t == "": t = "NIL"
	 if t == None: t = "NONE"
      return t


   def check(self, keys) :
      for k in keys:
         if not self.conf.has_key(k):
            raise Exception('%s is not defined in configuration' % k)

   def configure_by_gui(self):
      cnf = self.conf

   def save(self, filename=None):
      if filename == None:
	 filename = self.filename
      cf = open(filename, 'w')
      for k in self.conf.keys():
	 key = self.encode(k)
	 if self.has_subkeys(k):
	    for sk in self.conf[k].keys():
	       subkey  = self.encode(sk)
	       for v in self.conf[k][sk]:
	          val = self.encode(v)
		  cf.write("%s = %s.%s\n" % (key, subkey, val))
	 else:
	       for v in self.conf[k]:
		  val = self.encode(v)
		  cf.write("%s = %s\n" % (key, val))
	 cf.write('\n')


   ### doOptions reads the options in a Options.Options object
   ### and adds these as key / values records to the config

   def doOptions(self, options):
      for key in options.keys():
	 val = None
	 val = options[key]
	 if val == None:
	    val = self.get(key)
	 if val == None and options.isForced(key):
	    val = userInput('enter %s:' % key)
	 self.set(key,val)


   def isEmpty(self):
	return self.conf.keys() != {}

