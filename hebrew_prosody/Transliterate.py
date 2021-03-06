from emdros_application import *
import re
import copy

def transCons(cons, dagesh='', format=None, wordsep = '', cfg=None):

    # default values for chars that fit none of the conditions below
    if format == 'latex':
        ret = r'{\\bf ' + cons + '?}'
    else:
        ret = '|%s?|' % cons
        
    # ETCBC format is the input format, leave as is
    if format == 'etcbc':
        ret = cons
        if dagesh not in ('', 'forte'):
            ret += '.'

    # universal characters
    elif cons == '' : ret = ""
    elif cons == ' ': ret = " "
    elif cons == '!': ret = "!"
    elif cons == '[' : ret = "["
    elif cons == ']' : ret = "]"


    # Going to work
    elif cons == '>' : ret = "'"
    elif cons == 'B' : 
        if dagesh <> '':
            ret = "b"
        elif format == 'latex':
            ret = r"\\b{b}"
        elif format == 'ascii':
            ret = 'v'
	elif format == 'utf8':
	    ret = "b" + u"\u0332"
    elif cons == 'G' : ret = "g"
    elif cons == 'D' : ret = "d"
    elif cons == 'H' : ret = "h"
    elif cons == 'W' : ret = "w"
    elif cons == 'Z' : ret = "z"
    elif cons == 'X' : 
        if format == 'latex':
            ret = r"\d{h}"
        elif format == 'ascii':
            ret = "ch"
	elif format == 'utf8':
	    ret = "h" + u"\u0323"
    elif cons == 'V' : 
        if format == 'latex': 
            ret = r"\d{t}"
        elif format == 'ascii':
            ret = "t"
	elif format == 'utf8':
	    ret = "t" + u"\u0323"
    elif cons == 'J' : ret = "y"
    elif cons == 'JW':
        if format == 'latex':
            ret = r'\\v{u}'
        elif format == 'ascii':
            ret = 'v'
	elif format == 'utf8':
	    ret = "v" + u"\u0306"
    elif cons in ('K', 'k') : 
        if dagesh <> '':
            ret = "k"
        elif format == 'latex':
            ret = r"\\b{k}"
        elif format == 'ascii':
            ret = "kh"
	elif format == 'utf8':
	    ret = "k" + u"\u0332"
    elif cons == 'L' : ret = "l"
    elif cons in ('M', 'm') : ret = "m"
    elif cons in ('N', 'n') : ret = "n"
    elif cons == 'S' : ret = "s"
    elif cons == '<' : ret = "`"
    elif cons in ('P', 'p') : 
        if dagesh <> '':
            ret = "p"
        else:
            ret = "f"
    elif cons in ('Y', 'y') :
        if format == 'latex':
            ret = r"\d{s}"
        elif format == 'ascii':
            ret = "ts"
	elif format == 'utf8':
	    ret = "s" + u"\u0323"
    elif cons == 'Q' : ret = "q"
    elif cons == 'R' : ret = "r"
    elif cons == 'F' : 
        if format == 'latex':
            ret = r"\'{s}"
        elif format == 'ascii':
            ret = "s"
	elif format == 'utf8':
	    ret = "s" + u"\u0301"
    elif cons == 'C' : 
        if format == 'latex':
            ret = r"\\v{s}"
        elif format == 'ascii':
            ret = "sh"
	elif format == 'utf8':
	    ret = "s" + u"\u030C"
    elif cons == 'T' : 
	ret = "t"
    elif cons == '*':
        if format == 'latex':
            ret = r'\emph{(Q) }'
        elif format in ('ascii', 'utf8'):
            ret = "(Q) "
        else:
            raise Exception("unknown output format %s" % repr(format))
    return ret # '%r' % ret
    if format in ('utf8', 'utf8_heb'):
	return ret # DEBUG .decode('utf-8')
    else:
	return ret # '%r' % ret


def transDouble(char, dagesh='', format=None):
    if char <> '':
        if format == 'etcbc':
            dagesh = ''
	if re.search("\.", char):
	    dagesh ='.'
	    char = re.sub("\.", "", char)
        return transCons(cons=char, dagesh=dagesh, format=format)
    else:
        return ''


def stripETCBC(vowel):
    rep = copy.deepcopy(vowel)
    rep = re.sub('forte', '.', rep)
    rep = re.sub('lene', '.', rep)
    rep = re.sub('mob', ':', rep)
    rep = re.sub('qui', ':', rep)
    rep = re.sub('@[ao]', '@', rep)
    return rep

    
def transVowel(vowel, format=None):
    
    if format == 'latex':
        ret = r'{\\bf ' + vowel + '?}'
    else:
        ret = "%s?" % vowel

    if format == 'etcbc':
        ret = stripETCBC(vowel)
        
    elif vowel == '' : ret = ""

    elif vowel == 'A' : ret = "a"

    elif vowel in ['A:',':A'] : 
        if format == 'latex':
            ret = "$^a$"
        elif format in ('ascii', 'utf8'):
            ret = "(a)"
	elif format == 'utf8':
	    ret = u"\u2090"

    elif vowel in ['@H', '@>'] : 
        if format == 'latex':
            ret = r"\^{a}"
        elif format == 'ascii':
            ret = "a"
	elif format == 'utf8':
	    ret = 'a' + u"\u0302"


    elif vowel in ['@', '@a'] : 
        if format == 'latex':
            ret = r"\={a}"
        elif format == 'ascii':
            ret = 'a'
	elif format == 'utf8':
	    ret = 'a' + u"\u0305"

    elif vowel == '@o' : ret = "o"

    elif vowel in ['@:', ':@'] : 
        if format == 'latex':
            ret = "$^o$"
        elif format == 'ascii':
            ret = "(o)"
	elif format == 'utf8':
	    ret = u"\u2092"

    elif vowel == ';' : 
        if format == 'latex':
            ret = r"\={e}"
        elif format == 'ascii': 
            ret = "ee"
	elif format == 'utf8':
	    ret = 'e' + u"\u0305"

    elif vowel == ';a' : 
        if format == 'latex':
            ret = r"\={e}$\_{a}$"
        elif format == 'ascii':
            ret = "ea"
	elif format == 'utf8':
	    ret = 'e' + u"\u0305" + u"\u2090"

    elif vowel == ';J' : 
        if format == 'latex':
            ret = r"\={e}y"
        elif format == 'ascii':
            ret = "ey"
	elif format == 'utf8':
	    ret = 'e' + u"\u0305" + 'y'

    elif vowel == 'E' : 
	ret = 'e'


    elif vowel == 'Ea' : 
        if format == 'latex':
            ret = r"e$\_{a}$"
        elif format == 'ascii':
            ret = "ea"
	elif format == 'utf8':
	    ret = 'e' + u"\u0300" +  u"\u2090"

    elif vowel in [':E', 'E:'] : 
        if format == 'latex': 
            ret = "$^e$" 
        elif format == 'ascii':
            ret = "(e)"
	elif format == 'utf8':
	    ret = u"\u2091"

    elif vowel == 'EJ' : 
        if format == 'latex': 
            ret = r"\^{e}" 
        elif format == 'ascii':
            ret = "ey"
	elif format == 'utf8':
	    ret = 'e' + u"\u0302" + 'y'

    elif vowel == 'EJa' : 
        if format == 'latex': 
            ret = r"\^{e}$\_{a}$" 
        elif format == 'ascii':
            ret = "eya"
	elif format == 'utf8':
	    ret = 'e' + u"\u0302" + 'a'

    elif vowel == ';H' : 
        if format == 'latex': 
            ret = r"\^{e}" 
        elif format == 'ascii':
            ret = "eh"
	elif format == 'utf8':
	    ret = 'e' + u"\u0302"

    elif vowel == ';>' :
        if format == 'latex': 
            ret = r"\^{e}'"
        elif format == 'ascii':
            ret = "e'"
	elif format == 'utf8':
	    ret = 'e' + u"\u0302"
        
    elif vowel == 'EH' :
        if format == 'latex': 
            ret = r"\^{e}" 
        elif format == 'ascii':
            ret = "eh"
	elif format == 'utf8':
	    ret = 'e' + u"\u0302"

    elif vowel == 'I' : ret = "i"

    elif vowel == 'Ia' : 
        if format == 'latex':
            ret = r"i$\_{a}$"
        elif format == 'ascii':
            ret = "ia"
	elif format == 'utf8':
	    ret = 'i' + u"\u2090"

    elif vowel == 'IJ' : 
        if format == 'latex':
            ret = r"\^{\i}"
        elif format == 'ascii':
            ret = "i"
	elif format == 'utf8':
	    ret = 'i' + u"\u0302"
    
    elif vowel == 'IJa' : 
        if format == 'latex':
            ret = r"\^{\i}$\_{a}$"
        elif format == 'ascii':
            ret = "iya"
	elif format == 'utf8':
	    ret = 'i' + u"\u0302" + u"\u2090"

    elif vowel == 'O' : ret = "o"

    elif vowel == 'Oa' : 
        if format == 'latex':
            ret = r"o$\_{a}$"
        elif format == 'ascii':
            ret = "oa"
	elif format == 'utf8':
	    ret = 'o' + u"\u2090"

    elif vowel == 'OW' : 
        if format == 'latex': 
            ret = r"\^{o}"
        elif format == 'ascii':
            ret = "o"
	elif format == 'utf8':
	    ret = 'o' + u"\u0302"
        
    elif vowel == 'OH' :
        if format == 'latex': 
            ret = r"\^{o}"
        elif format == 'ascii':
            ret = "oh"
	elif format == 'utf8':
	    ret = 'o' + u"\u0302"

    elif vowel == 'O>' :
        if format == 'latex': 
            ret = r"\^{o}'"
        elif format == 'ascii':
            ret = "o'"
	elif format == 'utf8':
	    ret = 'o' + u"\u0302"

    elif vowel == 'OWa' :
        if format == 'latex':
            ret = r"\^{o}$\_{a}$"
        elif format == 'ascii':
            ret = "oa"
	elif format == 'utf8':
	    ret = 'o' + u"\u0302" + u"\u2090"

    elif vowel == 'U' : ret = "u"

    elif vowel == 'Ua' : 
        if format == 'latex': 
            ret = r"u$\_{a}$"
        elif format == 'ascii':
            ret = "ua"
	elif format == 'utf8':
	    ret = 'u' + u"\u2090"
        else: raise Exception("unknown output format %s" % repr(format))

    elif vowel == 'W.' :
        if format == 'latex':
            ret = r"\^{u}"
	elif format == 'utf8':
	    ret = 'u' + u"\u0302"
        elif format == 'ascii':
            ret = "u"

    elif vowel == 'W.a' : 
        if format == 'latex':
            ret = r"\^{u}$\_{a}$"
        elif format == 'ascii':
            ret = "ua"
	elif format == 'utf8':
	    ret = 'u' + u"\u2090"
        else:
            raise Exception("unknown output format %s" % repr(format))

    elif vowel == 'AI' : 
        if format == 'latex': 
            ret = r"a$\_{i}$"
        elif format in ('ascii', 'utf8'):
            ret = "ai"
        else:
            raise Exception("unknown output format %s" % repr(format))

    elif vowel == '@I' : 
        if format == 'latex':
            ret = r"\={a}$\_{i}$"
        elif format == 'ascii':
            ret = "ai"
	elif format == 'utf8':
	    ret = 'a' + u"\u0304"
        else:
            raise Exception("unknown output format %s" % repr(format))

    elif vowel == 'mob' : 
        if format == 'latex':
            ret = "$^e$"
        elif format == 'ascii':
            ret = "(e)"
	elif format == 'utf8':
	    ret = u"\u0304"

    elif vowel == 'qui' : ret = ""


    if format in ('utf8', 'utf8_heb'):
	return ret #DEBUG .decode('utf-8')
    else:
	return ret # '%r' % ret
    
    
def transExtras(extra, format=None, wordsep=''):
    
    ret = ''
    if format == 'etcbc':
        ret = extra

    elif extra in ('_S', '_P', '_s', '_p', '&&') :
	ret += ''
        
    elif '&' in extra:
	ret += '-'

    elif extra == '-':
	ret += wordsep

    elif extra == '--':
	ret += wordsep + wordsep

    elif extra == '---':
	ret += wordsep + wordsep + wordsep
    else:
        ret += extra # unknown extras, simply add

    if format in ('utf8', 'utf8_heb'):
	return ret.decode('utf-8')
    else:
	return ret # '%r' % ret


def transAcc(acc, format):
    if format == 'etcbc':
	if len(acc) == 1:
	    ret = acc.zfill(2)
	else:
	    ret = acc
    else:
        ret = ''
    if format in ('utf8', 'utf8_heb'):
	return ret.decode('utf-8')
    else:
	return ret # '%r' % ret


def translitConsonantBox(currBox, format=None, wordsep=''):
    #if re.search("&", currBox.dump()): DEBUG(currBox.dump())
    #DEBUG("|%s|" % currBox.cons)
    #DEBUG("|%s|" % currBox.vow)
    #DEBUG("|%s|" % currBox.dag)
    #DEBUG("|%s|" % currBox.acc)
    #DEBUG("|%s|" % currBox.double)
    #DEBUG("|%s|" % currBox.extra, pause=True)

    if format == 'utf8_heb':
	format = 'utf8'
    trans = ''
    trans += transCons(currBox.cons, currBox.dag, format)
    trans += transVowel(currBox.vow, format)
    trans += transAcc(currBox.acc, format)
    trans += transDouble(currBox.double, currBox.dag, format)
    trans += transExtras(currBox.extra, format, wordsep)
    return trans
    


def latexOpen(title=None, author=None):
    l  = '\\documentclass[12pt]{article}\n'
    l += '\\usepackage{palatino}\n'
    #l += '\\usepackage{dsea12}\n'
    if title <> None:
        l += '\\title{%s}\n' % title
    if author <> None:
        l += '\\author{%s}\n' % author
    l += '\\begin{document}\n'
    if title <> None or author <> None:
        l += '\\maketitle\n'
    return l


def latexClose():
    return '\\end{document}'


    
