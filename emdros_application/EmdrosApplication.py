from sys import *
import syscfg.config
import EmdrosPy
from utils.Paths import *
from utils.Options import *
from utils.IOTools import *
from utils.Configuration import *
from output.ReferenceManager import *
from output.OutputManager import *
from labelman.LabelManager import *
from mql_engine.MQLEngine import *
from gui.GUI import *


class EmdrosApplication:

    def __init__(self, options=None, title='EmdrosApplication',
                       DO_REF=True, DO_OUT=True, DO_LBL=True):
	if options is None:
	    options = Options()
        kernel_cfg_name = options.get('kernel')
        if kernel_cfg_name is not None:
            kernel_cfg_name = 'emdros_application.syscfg.' + re.sub('\.py[c]?$', '', kernel_cfg_name)
        else:
            kernel_cfg_name = syscfg.config.DEFAULT_KERNEL
	import importlib
        kernel = importlib.import_module(kernel_cfg_name)
	self.kernel = kernel
        #kernel = __import__(kernel_cfg_name)


        self.title = title
	self.DO_REF = DO_REF
	self.DO_OUT = DO_OUT
	self.DO_LBL = DO_LBL
        self.title = title

	self.spinner = Spinner()

	if options is None:
	    self.options = Options(addPathAndExt('options', kernel.CFG_DIR,
                                                            kernel.CFG_EXT))
	else:
	    self.options = options

        self.cfg      = self.configure(self.options, kernel)
        self.modeCfgs = self.setupModeConfigurations(kernel)

	self.mql = MQLEngine(database=self.database,
			usr=self.usr, pwd=self.pwd, be=self.backend,
			domainfile=self.domainqueryfile, domain=self.domain,
			VERBOSE=self.VERBOSE, verbose=self.verbose,
			test=self.test, outstream=self.outstream,
			errstream=self.errstream,
                        kernel=kernel)

        if self.DO_OUT or self.DO_REF:
            self.ref, self.out = self.setupOutput(kernel=kernel)

        if self.DO_LBL:
            self.lbl = self.setupLabelManagers(options.args, kernel=kernel)

        if self.options.get('gui'):
            self.gui = GUI(title=title, app=self)
            self.gui.mainloop()
        else:
            self.gui = None
                    

    # overload this with something useful
    def next(self):
	if self.gui:
	    self.gui.writeln('EmdrosApplication says: "next"')

    # overload this with something useful
    def quit(self):
	exit()


    def configure(self, options, kernel):

        # CFG_FILE is initially defined in the kernel configuration
        # program option -C (--CFG) overrides it

        cfg_name = options.get('CFG')
        #if cfg_name is not None:
            #CFG_FILE = cfg_name
        #else:
	if cfg_name is None:
            cfg_name = kernel.DEFAULT_KERNEL_CFG
        self.cfg = Configuration(cfg_name, kernel=kernel)
        
        # settings in local_cnf override settings in CONFIG_FILE
        local_cfg = options.get('cfg')
        if local_cfg is not None:
            local_cfg = Configuration(local_cfg, kernel=kernel)
            self.cfg.overrideWith(local_cfg)

        # settings in command line options override settings in
        # CONFIG_FILE and local_cnf

        self.cfg.overrideWith(options.toConfiguration(kernel=kernel))


        ### set global variables

        self.auto      = self.cfg.get('auto')
        self.verbose   = self.cfg.get('verbose')
        self.VERBOSE   = self.cfg.get('VERBOSE')

        backends = {'NO_BACKEND' : EmdrosPy.kBackendNone,
                    'POSTGRES'   : EmdrosPy.kPostgreSQL,
                    'MYSQL'      : EmdrosPy.kMySQL,
                    'SQL2'       : EmdrosPy.kSQLite2,
                    'SQL3'       : EmdrosPy.kSQLite3}

        if self.cfg.get('backend') is not None:
            self.backend  = backends[self.cfg.get('backend')]
        else:
            try:
                self.backend = backends[kernel.DEFAULT_BACKEND]
            except:
                exitOnError('no backend defined in configuration files')

	self.database = self.cfg.get('database')
        if self.cfg.get('usr'):
            self.usr      = self.cfg.get('usr')
        else:
            self.usr       = DEFAULT_USR
        if self.cfg.get('pwd'):
            self.pwd      = self.cfg.get('pwd')
        else:
            self.pwd       = DEFAULT_PWD

        if self.cfg.has_key('modes'):
            self.modes = self.cfg.get_multi('modes') # has proper order
        else:
            self.modes    = self.options.validVals('mode')
	self.mode     = self.cfg.get('mode')

        if self.cfg.has_key('formats'):
            self.formats = self.cfg.get_multi('formats')
        else:
            self.formats  = self.options.validVals('format')
            self.cfg.set_multi('formats', self.formats)
	self.format   = self.cfg.get('format')
	self.json     = self.cfg.get('jsonoverride')

	self.domain          = self.cfg.get('domain')
	self.domainqueryfile = self.cfg.get('domainqueryfile')

	self.test      = self.cfg.get('test')

        self.outstream = eval(self.cfg.get('stdout'))
        self.errstream = eval(self.cfg.get('stderr'))

        return self.cfg


    def setupModeConfigurations(self, kernel):
        modeCfgs = {}
        for m in self.modes:
            if self.cfg.has_key('modecfg', m):
                cfgname = self.cfg.get('modecfg', m)
                cfg = Configuration(cfgname, kernel=kernel, verbose=self.VERBOSE)
                if cfg is not None:
                    self.Vmsg('cfg for %s mode: %s' % (m, cfgname))
                modeCfgs[m] = cfg
            else:
                warning("no key 'modecfg' defined for mode %s in configuration file" % m)
        return modeCfgs



    def setupLabelManagers(self, opt_otypes, kernel=None):
        self.lblManagers = {}
        for m in self.modes:
            if m == self.mode:
                opt_o = opt_otypes
            else:
                opt_o = []
            try:
                self.lblManagers[m]=LabelManager(mql=self.mql, mode=m, globalcfg=self.cfg, local_cfg=self.modeCfgs[m], opt_otypes = opt_o, kernel=kernel)
            except:
                exitOnError()    
        if self.options.get('sync'):
            if self.options.get('auto'):
                mlist = self.modes
            else:
                mlist = userCheckList(self.modes,
                                    question="toggle modes to update")

            if mlist == []:
                writeln('no labels will be updated',
                                outstream=self.errstream)
            else:
                for m in mlist:
                    self.updateLabels(m)

        return self.lblManagers[self.mode]



    def setupOutput(self, kernel):
	if self.DO_REF:
	    ref = ReferenceManager(self.mql, self.cfg, kernel=kernel)
	else:
	    ref = None

	if self.DO_OUT:
	    out = OutputManager(self.mql, self.cfg,
			format=self.format,
			json=self.json, outstream=self.outstream,
			msgstream=self.errstream,
			verbose=self.verbose, VERBOSE=self.VERBOSE, kernel=kernel)
            if out is None:
               writeln('output manager based on %s could not be initiated' % self.json)
        else:
	    out = None
        return ref, out



    def Vmsg(self, msg):
	if self.VERBOSE:
	    writeln(msg, outstream = self.errstream)


    def vmsg(self, msg):
	if self.verbose or self.VERBOSE:
	    writeln(msg, outstream = self.errstream)


    def setMode(self, mode):
	if mode not in self.modes:
	    raise Exception('wrong value %s in EmdrosApplication.setMode(): %s' % \
			    mode, repr(self.modes))
	else:
	    self.mode = mode
	    self.mql.mode = mode
	    if self.DO_OUT and self.out is not None:
		self.out.mode = mode
	    if self.DO_LBL and self.lblManagers is not None:
		self.lbl = self.lblManagers[mode]


    def setFormat(self, format):
	if format not in self.formats:
	    raise Exception('wrong value %s in EmdrosApplication.setMode(): %s' % \
			    format, repr(self.formats))
	else:
	    self.format = format
	    if self.out is not None:
		self.out.format = format


    def updateLabels(self, mode=None, forced=False, mql=None, objTypes=None):
	if mode is None: mode = self.mode
	if self.lblManagers is None or self.lblManagers[mode] is None:
	    warning('no label manager for %s existing' % mode)
	else:
	    if mql is None: mql = self.mql
	    self.lblManagers[mode].updateAll(forced=forced, mql=mql, objTypes=objTypes)


    def write(self, msg='', outstream=None):
	if self.gui:
	    self.gui.write(msg, outstream=outstream)
	else:
	    write(msg, outstream=outstream)



    def writeln(self, msg='', outstream=None):
	if self.gui:
	    self.gui.writeln(msg)
	else:
	    writeln(msg, outstream=outstream)


    def userMultiLineInput(self, msg=None):
	if self.gui:
	    return self.gui.userMultiLineInput()
	else:
	    return userMultiLineInput(msg)
