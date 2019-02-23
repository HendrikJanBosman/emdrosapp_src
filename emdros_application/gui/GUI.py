from emdros_application.utils.IOTools import *

from Tkinter import *
from ScrolledText import *

class GUI(Frame):

    def __init__(self, master=None, app=None, title=''):

	self.engine = app

        Frame.__init__(self, master)
	self.master.title(title)
        self.grid()
        self.createWidgets()

    def createWidgets(self):

        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.nextButton = Button(self, text="next", command = self.next)
        self.nextButton.grid(row=0,column=0, sticky=S)

        self.quitButton = Button(self, text="quit", command = self.quit)
        self.quitButton.grid(row=0,column=1, sticky=S)

        self.inWindow = Text()
        self.inWindow.grid(row=1,column=0,sticky=N+E+S+W)

        self.outWindow = ScrolledText()
        self.outWindow.grid(row=2,column=0,sticky=N+E+S+W)

    def next(self):
	if self.engine <> None:
	    self.engine.next()
	else:
	    self.clearInput()

    def quit(self):
        self.master.destroy()
	self.engine.quit()

    def write(self, s):
	write(s, outstream=None, widget= self.outWindow)

    def writeln(self, s):
	writeln(s, outstream=None, widget= self.outWindow)

    def get(self):
	return self.inWindow.get(1.0, END)

    def userMultiLineInput(self):
	return self.get()
    
    def clearOutput(self):
	self.outWindow.delete(1.0, END)
    
    def clearInput(self):
	self.inWindow.delete(1.0, END)

    def clearInput(self):
	self.inWindow.delete(1.0, END)

if __name__ == '__main__':
    app = GUI(title="Generic GUI EmdrosApplication classes")
    app.mainloop()
