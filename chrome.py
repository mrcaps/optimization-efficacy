#Chrome controller

import os, sys, stat
import shutil
from config import *
from subprocess import *
from profile import *
import logging as log
import time

STR_CHROME="chrome"
STR_V8LOG="v8.log"
STR_OUTLOG="stdout.log"

#Manager for v8 javascript flags
#@author ishafer
class JSFlags():
	__defaults = None

	def __init__(self,helploc=os.path.join("res","d8help.txt")):
		if JSFlags.__defaults is None:
			JSFlags.__defaults = self.parse_defaults(helploc)

		self.overrides = dict()

	#set a js flag to the given value.
	def __setitem__(self,flag,val):
		if not flag in self.__defaults:
			log.error("Couldn't find JS flag: %s" % flag)
			return
		if type(val) != type(self.__defaults[flag]):
			log.error("Mismatched types for JS flag: %s=%s" % (flag, str(val)))
			return
		self.overrides[flag] = val

	#Remove all overrides
	def reset(self):
		self.overrides = dict()

	#convert the JS flags override to actual JS flags
	def to_jsflags(self):
		flagarr = []
		for (k,v) in self.overrides.iteritems():
			if type(v) == type(True):
				flagarr.append(k if v else "no" + k)
			elif type(v) == type(""):
				#don't quote strings for now
				flagarr.append("%s=%s" % (k, v))
			elif type(v) == type(42):
				flagarr.append("%s=%d" % (k, v))
			else:
				log.error("Unknown override type: %s" % v)
		
		return ["--" + v for v in flagarr]

	#parse default JS flags from d8 help
	def parse_defaults(self,helploc):
		fp = open(helploc,"r")
		MODE_OTHER = 0
		MODE_ARG = 1

		flags = dict()

		mode = MODE_OTHER
		curarg = ""
		for lineraw in fp:
			line = lineraw.strip()
			if line.startswith("--"):
				curarg = line.lstrip("-")
				curarg = curarg[:curarg.index(" ")]
				mode = MODE_ARG
			else:
				if mode == MODE_ARG:
					info = line.split()
					assert info[0] == "type:"
					assert info[2] == "default:"
					thetype = info[1]
					if len(info) == 4:
						theval = info[3] #polymorphic
					else:
						theval = ""
					if thetype == "bool":
						theval = (theval == "true")
					elif thetype == "string":
						pass
					elif thetype == "int":
						theval = int(theval)
					flags[curarg] = theval
				mode = MODE_OTHER

		fp.close()

		return flags

#Creates instances of Chrome
#@author ishafer
class ChromeBuilder():
	def __init__(self,chromedir=Config().chromeloc,profdir="profile",jsflags=JSFlags()):
		self.exeloc = os.path.join(chromedir,STR_CHROME)
		if not os.path.exists(os.path.join(chromedir,STR_CHROME)):
			log.error("Could not find chrome executable in " + chromedir)

		#by default created under the chrome directory
		self.profdir = os.path.join(chromedir,profdir)
		self.logpath = os.path.join(self.profdir,STR_V8LOG)
		self.flags = jsflags

	def clean_profdir(self):
		if os.path.exists(self.profdir):
			shutil.rmtree(self.profdir)
		os.makedirs(self.profdir)
		#os.chmod(self.profdir, 0o777)

	def get_standard_args(self):
		return ["--no-first-run",
			"--no-sandbox", \
			"--disable-application-cache", \
			"--allow-file-access", \
			#"--disable-web-security", \
			]

	def get_js_args(self,profileon=False):
		flags = ["--logfile=" + self.logpath]
		flags.append("--prof-browser-mode")
		if profileon:
			flags.append("--noprof-lazy")
		else:
			flags.append("--dump_counters")
		#flags.append("--trace-deopt")
		flags.extend(self.flags.to_jsflags())
		return flags

	#Start Chrome with this factory's jsflags
	#@param target the invocation target
	#@param profileon do we have profiling enabled?
	# (we can't dump counters and profile at the same time)
	def invoke(self,target,profileon=False):
		self.clean_profdir()
		cmdline = [self.exeloc]
		cmdline.append("--args")
		cmdline.append("--user-data-dir=" + self.profdir)
		cmdline.extend(self.get_standard_args())
		jsargs = str(" ".join(self.get_js_args(profileon)))
		log.info("Running chrome with jsargs " + jsargs)
		cmdline.append('--js-flags="%s"' % jsargs)
		cmdline.append(target)

		#we need shell=True and the explicit commandline to handle jsflags
		ofloc = os.path.join(self.profdir,STR_OUTLOG)
		fpout = open(ofloc,"w")
		proc = Popen(" ".join(cmdline),stdout=fpout,shell=True,close_fds=True)
		return Chrome(proc=proc,profpath=self.logpath,ofloc=ofloc,\
			jsflags=self.flags,url=target,isprofile=profileon)

#An instance of Chrome
#@author ishafer
class Chrome():
	#@param proc Chrome process
	#@param profpath the path to v8.log
	#@param ofloc the location of stdout.log
	#@param jsflags list of JS flags used for the invocation
	#@param url the URL opened
	#@param isprofile was this opened with profileon?
	def __init__(self,proc,profpath,ofloc,jsflags,url,isprofile):
		self.proc = proc
		self.profpath = profpath
		self.ofloc = ofloc
		self.jsflags = jsflags
		self.url = url
		self.isprofile = isprofile
		self.starttime = time.time()

	#Build the profile for this instance of Chrome
	def profile(self,outdir):
		if not os.path.exists(outdir):
			os.makedirs(outdir)

		#write the run information
		rinfo = dict()
		rinfo["flags"] = self.jsflags.overrides
		rinfo["starttime"] = self.starttime
		rinfo["donetime"] = time.time()
		rinfo["url"] = self.url
		rinfo["isprofile"] = self.isprofile

		fp = open(os.path.join(outdir,STR_INFOFILE),"w")
		json.dump(rinfo,fp,indent=2)
		fp.close()

		return Profile(self.profpath,self.ofloc,outdir)

	def wait(self):
		self.proc.wait()

def test_builder():
	builder = ChromeBuilder()
	#builder.flags["crankshaft"] = False
	#builder.flags["use_inlining"] = False
	#builder.flags["unbox_double_arrays"] = False
	builder.invoke("http://www.google.com",True)

def test_jsflags():
	flags = JSFlags()
	flags["crankshaft"] = False
	arr = flags.to_jsflags()
	assert len(arr) == 1
	assert arr[0] == "--nocrankshaft"
	flags.reset()
	assert len(flags.to_jsflags()) == 0
	flags["blahblahblah"] = "foobar"
	assert len(flags.to_jsflags()) == 0

if __name__ == "__main__":
	#test_jsflags()
	test_builder()
	