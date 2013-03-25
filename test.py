from config import *
from chrome import *
from profile import *
import time
import os

"""
Exciting places to test:
jslinux:
	crankshaft: all:13289 js:6483 compiler:297
	nocrankshaft: all:15539 js:6768 compiler:62
v8 benchmark: http://v8.googlecode.com/svn/data/benchmarks/v7/run.html
	crankshaft: all:25063 js:19561 compiler:1652 (10937 on benchmark)
	nocrankshaft: all:29040 js:24458 compiler:1332 (3935 on benchmark)
v8 modbenchmark:
	crankshaft: all:6854 js:4238 compiler:438
	crankshaft flagsoff: all:8231 js:5375 compiler:486
	nocrankshaft: all:12897 js:10665 compiler:479
"""

#stateless test runner
class Runner():
	def __init__(self):
		self.builder = ChromeBuilder()

	#set flags
	#@param dct a map of flag names to values
	def flags(self,dct):
		self.builder.flags.reset()
		for (k,v) in dct.iteritems():
			self.builder.flags[k] = v

	#@param url the http address to visit
	#@param sikuli the directory of the sikuli script to run
	#@param profileon is profiling turned on? If so, run profiling, else enable counters
	def launch(self,url,sikuli,profileon):
		cfg = Config()

		inst = self.builder.invoke(url,profileon)
		Popen("%s -r %s" % ( \
			os.path.join(cfg.sikuliloc,"sikuli-ide.sh"),
			os.path.join(cfg.scriptdir,sikuli) ),
			shell=True, cwd=cfg.sikuliloc)
		inst.wait()
		prof = inst.profile(os.path.join(cfg.tmpdir,str(int(time.time()))))
		prof.build()
		pp = ProfileParse(prof.outdir)
		print pp.summary()

def testwrap():
	run = Runner()
	run.flags({
		"crankshaft":True,
		"use_canonicalizing":False,
		"use_gvn":False,
		"loop_invariant_code_motion":False,
		"use_range":False,
		"eliminate_dead_phis":False,
		"use_inlining":False,
		"limit_inlining":False,
		"inline_arguments":False,
		"always_opt":True,
		"polymorphic_inlining":False,
		"inline_construct":False,
		"optimize_for_in":False
	})

	#run.flags({})

	#run.launch("http://172.19.149.117/wordpress/wp-login.php","wordpress_create_post.sikuli",True)
	#run.launch("http://www.facebook.com","facebook_post_picture_tag.sikuli", True)
	#run.launch("http://gmail.com","gmail_popup_search.sikuli", True)
	#run.launch("http://172.19.149.117:8000/project","trac_search_spoon.sikuli", True)
	#run.launch("http://v8.googlecode.com/svn/data/benchmarks/v7/run.html","v8_benchmarks.sikuli",True)
	run.launch("http://172.19.149.117/benchmod/run.html","v8_benchmarks.sikuli",False)

if __name__ == "__main__":
	testwrap()

