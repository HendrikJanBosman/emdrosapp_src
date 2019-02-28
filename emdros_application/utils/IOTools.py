from __future__ import print_function
import sys, os, subprocess, time

import tempfile
from subprocess import call
from emdros_application.syscfg.config import *

import re
import copy

class Spinner:

    def __init__(self, outstream=sys.stderr, delay=0):
	self.outstream = outstream
	self.delay = delay
	self.pattern=['-','\\','|','/','-','\\','|']
	self.i = 0

    def next(self):
	self.outstream.write("%s " % self.pattern[self.i])
	self.outstream.flush()
	self.outstream.write("\b\b")
	time.sleep(self.delay)
	self.i += 1
	if self.i >= len(self.pattern):
	    self.i = 0

    def spin(delay=None):
	if delay == None: spin = self.delay
	while 1:
	    for i in pattern:
		sys.stderr.write(i + " ")
		sys.stderr.flush()
		sys.stderr.write("\b\b")
		time.sleep(delay)


def errorMsg():
    return sys.exc_info()[1]


def exitOnError(msg=None, outstream=None, do_raise=False):
    if do_raise:
	raise Exception(msg)
    else:
	if msg is not None:
	    writeln(msg, outstream=outstream)
	else:
	    writeln(sys.exc_info()[1], outstream=outstream)
	exit()

def exitOnError_old(msg=None, outstream=None):
    write("exit on error: ")
    if msg <> None:
	writeln(msg, outstream=outstream)
    else:
	writeln(sys.exc_info()[1], outstream=outstream)
    sys.exit(1)


def write(m, widget=None, outstream=sys.stdout):
   if m == None:
      m = 'None'
   if widget==None:
      print(m, end='', file=outstream)
   else:
      widget.insert("end", m)

def write_stderr(m, widget=None):
    write(m, outstream=sys.stderr)
      
def writeln(m="", widget=None, outstream=sys.stdout):
   write("%s\n" % m, widget=widget, outstream=outstream)

def writeln_stderr(m, widget=None):
    writeln(m, outstream=sys.stderr)

def warning(m, widget=None, outstream=sys.stderr):
    writeln("\n*** %s\n" % m, outstream= outstream)

def DEBUG(m=None, pause=False, widget=None, dbx=True, outstream=sys.stderr):
    if dbx:
	if m == None: m = "None"
	if type(m) == str:
	    writeln("DEBUG: %s" % m, outstream=outstream)
	else:
	    writeln("DEBUG: %s" % repr(m), outstream=outstream)
	if pause:
	    userInput("<Enter> to continue", outstream=outstream)

   
def cls(widget=None, outstream=sys.stderr):
   if widget == None:
      import os
      if os.name == 'posix':
          #os.system('clear')
          subprocess.call('clear', stderr=outstream)
      elif os.name == 'nt':
          #os.system('cls')
          subprocess.call('cls', stderr=outstream)
      else:
          writeln('\n' * 12, widget, outstream)
   else:
      widget.delete("1.0", "end")


def underlined(s, ulc="-"):
    if s in ('', None):
        return ''
    else:
        ul = re.sub(".", ulc, s)
        return "%s\n%s" % (s, ul)


def userInput(question=None, outwidget=None, inwidget=None, outstream=sys.stderr, instream=sys.stdin):
   if question:
      write(question + ' ', widget=outwidget, outstream=outstream)
   if inwidget == None:
      return instream.readline()[:-1] # lose trailing newline
   else:
      writeln('input widget %s not implemented in userInput()' % repr(inwidget))


def pause(m="<Enter> to continue", outwidget=None, inwidget=None,
				   outstream=sys.stderr, instream=sys.stdin, 
				   cancelOK=False, cancelMsg=None,
				   cancelStr="c"):

    if cancelOK: 
	if cancelMsg == None:
	    m += " (or '%s' to cancel)" % cancelStr
	else:
	    m += cancelMsg
    return userInput(m,outwidget=outwidget, inwidget=inwidget,
				   outstream=outstream, instream=instream)
    

def userMultiLineInput(question=None, outwidget=None,
		       inwidget=None, outstream=sys.stderr,
		       confirm=False, emptyOK=False):
   STOP = False
   while not STOP:
      inp = ""
      if question:
	 writeln(underlined(question), widget=outwidget, outstream=outstream)
      writeln("(extra <Enter> to submit)", widget=outwidget, outstream=outstream)
      l = userInput('', outwidget=outwidget,
					 inwidget=inwidget, outstream=outstream)
      while l <> "":
	 if inp <> "":
	    inp = "%s\n" % inp
	 inp = "%s%s" % (inp, l)
         l = userInput('', outwidget=outwidget,
					 inwidget=inwidget, outstream=outstream)
      if re.search("^[ \t\n][ \t\n]*$", inp):  # empty input
	 if emptyOK: 
	    if confirm:
		STOP = userAffirms("you entered only blanks, proceed anyway?")
	    else:
		STOP = True
	 else:
	    writeln("empty input, try again", widget=outwidget, outstream=outstream)
	    STOP = False
      elif confirm:
	 STOP = userAffirms("\ninput OK?",  cancelOK=True)
	 if STOP == -1: # cancelled
	    return None
      else:
	 STOP = True
   return inp


def userIntInput(question=None, min=None, max=None, outwidget=None, inwidget=None, outstream=sys.stderr,
		 cancelOK=False):
    return  userIntegerInput(question=question, min=min, max=max, outwidget=outwidget, inwidget=inwidget, outstream=outstream,
		     cancelOK=cancelOK)


def userIntegerInput(question=None, min=None, max=None, outwidget=None, inwidget=None, outstream=sys.stderr,
		 cancelOK=False):
   correct = False
   i = 0
   while not correct:
      if question:
	 if cancelOK: question += ' (<Enter> to cancel)'
         write(question + ' ', widget=outwidget, outstream=outstream)
      if inwidget == None:
	 inpString = sys.stdin.readline()[:-1] # lose trailing newline
         try:
            i = int(inpString)
            correct = True
         except:
	    if cancelOK and inpString == "":
		i = None
		correct = True
	    else:
		writeln('wrong input, not a number', widget=outwidget, outstream=outstream)
		correct = False
      else:
         writeln('input widget not implemented in IOTools.userIntInput()', widget=outwidget, stream=outstream)

      if i <> None:
	  if min is not None and i < min:
	     writeln ('number too small, must be >= %d' % min, widget=outwidget, outstream=outstream)
	     correct = False
	  if max is not None and i > max:
	     writeln ('number too large, must be <= %d' % max, widget=outwidget, outstream=outstream)
	     correct = False
   return i


def userAffirms(question, cancelOK=False, cancelMsg = " / c(ancel)",
		    confirm=False, confY=False, confN=False,
		    q2="Are you sure?", q2Y="Are you sure?",
		    q2N="Are you sure?",
		    outwidget=None, inwidget=None,
		    outstream=sys.stderr):
   question = question + ' y(es) / (n)o'
   if cancelOK:
      question += ' ' + cancelMsg
   question += ': '
   if confirm:
      confN = False
      confY = False

   OK = False
   res = -1
   while not OK:
      response = userInput(question, outwidget, inwidget, outstream)
      if response in ("", None):
	   if not cancelOK:
	      writeln("empty input, try again.")
	      OK = False
	   else:
	       OK = True
      elif response[0] in ('Y', 'y', 'J', 'j'):
	    res = True
	    OK = True
      elif response[0] in ('N', 'n'):
	    res = False
	    OK = True 
      elif cancelOK and (response=="" or response[0] in ('C','c')):
	 res = -1 # return None doesn't work, it is equivalent to False
	 OK = True
      else:
	 writeln("wrong input, try again.")
	 OK = False

      if confirm:
	 OK = userAffirms(q2, confirm=False)
      if confY and (res == True):
	 OK = userAffirms(q2Y)
      if confN and (res == False):
	 OK = userAffirms(q2N)
   return res


def userNumberedOption(optionsList, getInt=False, question=None, 
	    cancelOK=True, cancelMsg=None, outwidget=None, inwidget=None, outstream=sys.stderr):
   if cancelMsg == None:
    cancelMsg = ", or <Enter> for none"
   if len(optionsList) == 0:
      if getInt:
	 return -1 
      else:
	 return None
   valid = False
   choice = None
   while not valid:
      validChoices = []
      if question <> None:
          writeln(underlined(question), widget=outwidget, outstream=outstream)
      for option in optionsList:
         o = optionsList.index(option)
         writeln('%i. %s' % (o + 1, option), widget=outwidget, outstream=outstream)
         validChoices.append(repr(o + 1))
         validString = '%s-%s' % (validChoices[0], validChoices[-1])
	 if cancelOK:
	    validString += ' ' + cancelMsg
      if cancelOK:
	 validChoices.append("")
      answer = userInput('\nmake choice (%s)' % validString, outwidget, inwidget, outstream)
      if answer in validChoices: # or (cancelOK and answer == ""):
	 if (cancelOK and answer == ""):
	    choice = -1
	    if not getInt:
		choice = None
	    valid = True
         else:
	     choice = validChoices.index(answer)  # the index number
	     if not getInt:                       # the string
		choice = optionsList[validChoices.index(answer)]
	     valid = True
      else:
         writeln('wrong input, choose %s' % validString, widget=outwidget, outstream=outstream)
         #userInput('hit <Enter> to continue', outwidget, inwidget, outstream)
         choice = answer
   return choice

      
def userMenu(optionsList, getInt=False, question=None, 
	    cancelOK=True, cancelMsg=None, outwidget=None, inwidget=None, outstream=sys.stderr):
    return userNumberedOption(optionsList, getInt=getInt, question=question, 
	    cancelOK=cancelOK, cancelMsg=cancelMsg, outwidget=outwidget, inwidget=inwidget, outstream=outstream)


def userKeyPress(optionsList, question=None, fullkey=False, cancelOK=True, cancelMsg=None,
	 splitlines=False, integerOK=False, header=False, outwidget=None, inwidget=None, outstream=sys.stderr):

   if len(optionsList) == 0:
      return None
   valid = False
   validList = []
   if question <> None:
      if header:
	 writeln(underlined(question), widget=outwidget, outstream=outstream)
      else:
	 if question <> None:
	     write("%s " % question,  widget=outwidget, outstream=outstream)
   while valid == False:
      for o in optionsList:
         if len(o) == 1:
            write(o, widget=outwidget, outstream=outstream)
            validList.append(o)
         else:
            write('%s(%s)' % (o[0],o[1:]), widget=outwidget, outstream=outstream)
         if o <> optionsList[-1]:
	    if splitlines:
		write('\n', widget=outwidget, outstream=outstream)
	    else:
		write(' ', widget=outwidget, outstream=outstream)
	 if o <> "":
	    validList.append(o[0])
      if cancelOK:
	 validList.append('')
	 if splitlines:
	    writeln(widget=outwidget, outstream=outstream)
	 else:
	    write(' ', widget=outwidget, outstream=outstream)
	 if cancelMsg is None:
	    cancelMsg = "(<Enter> for none)"
         write(cancelMsg, widget=outwidget, outstream=outstream)
      write(': ', widget=outwidget, outstream=outstream)


      choice = userInput(None, outwidget, inwidget, outstream)
      if choice == "":
         if cancelOK:
	    choice = None
            valid = True
         else:
            writeln('wrong input, ', widget=outwidget, outstream=outstream)
      elif not (choice in validList):
	    if integerOK:
		try:
		    return int(choice)
		except:
		    pass
            writeln('wrong input, ', widget=outwidget, outstream=outstream)
      else:
	 choice = choice[0]
	 valid = True

   if choice <> None and fullkey:
       return optionsList[validList.index(choice)]
   else: 
       return choice

def userOneCharOption(optionsList, question=None, fullkey=False, cancelOK=True, integerOK=False,
	 splitlines=False, header=False, outwidget=None, inwidget=None, outstream=sys.stderr):
    return userKeyPress(optionsList, question=question, fullkey=fullkey, cancelOK=cancelOK, integerOK=integerOK,
	 splitlines=splitlines, header=header, outwidget=outwidget, inwidget=inwidget, outstream=outstream)



def userCheckList(optionsList, question=None, cancelMsg=None, outwidget=None,
	    inwidget=None, outstream=sys.stderr, prechecked=[]):
    if question == None:
	question = "toggle the options you want"
    if cancelMsg == None:
	cancelMsg = '<Enter> when done'
    options = list(optionsList)
    for i in range(0, len(options)):
	if options[i] in prechecked:
	    options[i] = "*%s" % options[i]

    while 1 == 1:
	cls()
	check = userNumberedOption(options, question=question,
		cancelOK=True, cancelMsg=cancelMsg, outwidget=outwidget,
		inwidget=inwidget, outstream = outstream)
	if check in (None, -1):
	    break
	elif not re.match('\*', check):
	    options[options.index(check)] = '*' + check
	elif re.match('\*', check):
	    options[options.index(check)] = check[1:]
    r = []
    for o in options:
	if re.match('\*', o):
	    r.append(o[1:])
    return r


def editFile(fname, editor=None):
    if editor is None: editor = EDITOR
    #os.system(editor + " " +  fname)
    subprocess.call([editor, fname], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def editString(content='', editor=None):
    if editor is None: editor = EDITOR
    f = tempfile.NamedTemporaryFile(mode='w+', dir=TMP_DIR)
    if content:
        f.write(content)
        f.flush()
    #command = editor + " " + f.name
    #status = os.system(command)
    status = subprocess.call([editor, f.name], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    f.seek(0, 0)
    text = f.read()
    f.close()
    assert not os.path.exists(f.name)
    return (text)

