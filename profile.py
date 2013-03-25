#Capture and parse profiles from Chromium

import os
from subprocess import *
from config import *
import logging as log
import shutil
import zipfile, zlib
import json

STR_PROFILE = "profile"
STR_INFOFILE = "info.json"
STR_LOGFILE = "stdout.log"

#Profiling output from a Chrome execution
# (i.e. from v8.log)
#@author ishafer
class Profile():
	#@param srcloc the source location (v8.log)
	#@param ofloc the stdout location (stdout.log)
	#@param outdir where to place parsed profiling results
	def __init__(self,srcloc,ofloc,outdir):
		self.srcloc = srcloc
		self.ofloc = ofloc
		self.outdir = outdir

	#Parse a profile using the given command-line flags.
	#Save the output to a place in outdir
	def parse(self,flags=[]):
		cfg = Config()
		fname = ".".join([STR_PROFILE] + [f.strip("-") for f in flags] + ["json"])
		outloc = os.path.join(self.outdir,fname)

		runnable = os.path.join(cfg.scriptdir, "tools", "linux-tick-processor")
		outfp = open(outloc,"w")
		cmdline = [runnable] + flags + [self.srcloc] 
		log.info("Parse profile %s to %s" % (self.srcloc,outloc))
		proc = Popen(cmdline, stdout=outfp, close_fds=True)
		proc.wait()

	#Build a full parsed profiling output
	def build(self):
		if (os.path.exists(self.srcloc)):
			self.parse(["-c"])
			self.parse(["-j"])
			zf = zipfile.ZipFile(os.path.join(self.outdir,"v8.log.zip"),mode="w")
			try:
				log.info("Adding %s to v8.log" % (self.srcloc))
				zf.write(self.srcloc,arcname="v8.log",compress_type=zipfile.ZIP_DEFLATED)
			finally:
				zf.close()
		if (os.path.exists(self.ofloc)):
			shutil.copyfile(self.ofloc,os.path.join(self.outdir,STR_LOGFILE))

# A parsed profile output, as generated from a Profile
#@author ishafer
class ProfileParse():
	def __init__(self,loc):
		self.loc = loc
		self.profs = dict()
		self.cnts = dict()
		self.read()

	#scan all profiles
	def read(self):
		for fname in os.listdir(self.loc):
			fullpath = os.path.join(self.loc,fname)
			fst, snd = os.path.splitext(fname)
			#we have a profile. Parse it!
			if fst.startswith(STR_PROFILE):
				self.parse(fst[len(STR_PROFILE)+1:],fullpath)
			elif fname == STR_LOGFILE:
				self.parselog(fullpath)
			elif fname == STR_INFOFILE:
				fp = open(fullpath,"r")
				self.loadedinfo = json.load(fp)
				fp.close()

	#parse the profile from fname into key
	def parse(self,key,fname):
		fp = open(fname,"r")
		obj = json.load(fp)
		fp.close()

		totalt = 0
		for (ttype,times) in obj["times"].iteritems():
			for (time,fn) in times:
				totalt += time

		self.profs[key] = obj
		self.profs[key]["totaltime"] = totalt

	#parse stdout.log into counters
	def parselog(self,fname):
		fp = open(fname,"r")
		S_OUTSIDE = 0
		S_INHEADER = 1
		S_INCOUNT = 3
		state = S_OUTSIDE
		curtick = 0

		STR_TICKHEAD = "****TICK"
		STR_NORMHEAD = "+-------"

		for line in fp:
			if state == S_OUTSIDE:
				if line.startswith(STR_TICKHEAD):
					state = S_INHEADER
					curtick = line[len(STR_TICKHEAD):]
				elif line.startswith(STR_NORMHEAD):
					state = S_INHEADER
			elif state >= S_INHEADER and state < S_INCOUNT:
				state += 1
			elif state == S_INCOUNT:
				split = line.split("|")
				if len(split) == 4:
					name = split[1].strip()
					number = int(split[2].strip())
					#TODO: look at counters over time?
					self.cnts[name] = number
				else:
					state = S_OUTSIDE
		fp.close()

	#get metadata from the profile
	def info(self):
		return self.loadedinfo

	#summarize the "profile" part, if it exists
	def summary(self):
		DEF = "j" #default for getting summary profile info
		if DEF in self.profs:
			return {
				"compiler": self.profs["c"]["totaltime"], #ticks in compiler
				"js": self.profs["j"]["totaltime"], #ticks in javascript
				"all": self.profs[DEF]["info"]["total"], #total ticks
				"unaccounted": self.profs[DEF]["info"]["unaccounted"] #unaccounted
			}

	#return the summary of the "counters" part, if it exists
	def counters(self):
		return self.cnts

def get_sample_profile():
	cfg = Config()
	return Profile(os.path.join(cfg.chromeloc,"profile","v8.log"),cfg.tmpdir)

#test a single filter on the profile
def test_profile_parse():
	prof = get_sample_profile()
	prof.parse(["-j"])

def test_profile_build():
	prof = get_sample_profile()
	prof.build()

def test_profileparse():
	cfg = Config()
	pp = ProfileParse(os.path.join(cfg.tmpdir,"1334304589"))
	print pp.info()
	print pp.summary()
	print pp.counters()

if __name__ == "__main__":
	#test_profile_build()
	test_profileparse()