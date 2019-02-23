########### FUNCTIONS TO EXPAND FILENAMES TO FULL PATHS
import re

def addPath(fn, path):
    if fn == None: return None
    if not re.search('\/', fn):
        fn =  path + fn
    return fn

def addExt(fn, ext):
    if fn == None: return None
    if ext[0] <> '.':
	ext = '.' + ext
    if not re.search("%s$" % ext, fn):
	fn = fn + ext
    return fn

def addPathAndExt(fn, path, ext):
   return addPath(addExt(fn, ext), path)

def addPathExt(fn, path, ext):
   return addPathAndExt(fn, path, ext)
