import re
from shlex import *
from emdros_application.utils.IOTools import *
from Query import *

START_TOKENS = ["SELECT", "GET", "CREATE", "DROP"]
END_TOKENS   = ["GO",]

class QueryList(list):

    def __init__(self, fN=None, query_list=None):
	if fN is not None:
	    Q = open(fN, 'r')
	    QUERY = False
	    lines = Q.readlines()
	    Q.close()
	    tmp_query = "" 
	    for l in lines:
		for token in list(shlex(l)):
		    if token in START_TOKENS:
			QUERY = True
			tmp_query = token
		    elif token in END_TOKENS:
			tmp_query += ' ' + token
			self.append(Query(tmp_query))
			QUERY = False
		    elif QUERY:
			tmp_query += ' ' + token
		    else:
			pass
		if QUERY:
		    tmp_query += '\n'
	   	 

if __name__ == '__main__':
    ql = QueryList('/projects/aio1/aio1.2/lbl/lexical.word.lbl')
    for q in ql:
	print(q)
	print q.insertGetPhrase('get g_cons, g_word')
