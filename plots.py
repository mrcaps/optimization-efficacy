from analyze import *
from pylab import *
import numpy as np
import re

matplotlib.rcParams.update({
	"font.size": 8
#	"font.sans-serif": "Lucida Grande"
})

PLOTSOUT = "../report"

def color(n):
	return ["#0A23C8","#FFB65F","#529D4B","#007D9B","#FBBEA9","#CFAB00",
		"#666666","#999999","#CCCCCC"][n]

def saveplot(name):
	savefig(os.path.join(PLOTSOUT,name+".pdf"))

#Plot overall performance graph across benchmarks
#Expects data from default (no flags), crankshaft with opts turned off, nocrankshaft cases
#@author ishafer 
def plot_percentages(ana):
	xbins = ana.byurls.keys()
	remurl = "http://v8.googlecode.com/svn/data/benchmarks/v7/run.html"
	if remurl in xbins:
		del xbins[xbins.index(remurl)]

	def comparator(n1,n2):
		n1 = ana.shorturl(n1)
		n2 = ana.shorturl(n2)
		if n1 == n2:
			return 0
		elif n1 < n2:
			return -1
		else:
			return 1
	xbins.sort(comparator)
	caselens = [0,256,257]
	
	items = dict()
	for xb in xbins:
		items[xb] = dict()
		for cl in caselens:
			items[xb][cl] = []

	for tup in ana.tuples:
		if not tup[TDX_ISPROF]:
			continue
		url = tup[TDX_URL]
		lenflags = len(tup[TDX_HFLAGS])
		if not lenflags in caselens:
			continue
		if not url in xbins:
			continue
		items[url][lenflags].append(tup[TDX_PROF].summary())

	fig = figure(figsize=(6,2))
	fig.subplots_adjust(left=0.1,right=0.95,bottom=0.1,top=0.95)

	width = 0.2
	barspace = 0.04
	ind = width
	xinds = []
	labels = []
	for url in xbins:
		normt = np.mean([it["js"] + it["compiler"] for it in items[url][257]])
		for cl in caselens:
			its = [float(it["js"]) / normt  for it in items[url][cl]]
			m1 = np.mean(its)
			handle1 = bar(ind,m1,width,color=color(0),yerr=np.std(its),ecolor="k",linewidth=0.5)

			its = [float(it["compiler"]) / normt for it in items[url][cl]]
			m2 = np.mean(its)
			handle2 = bar(ind,m2,width,color=(0.7,0.7,0.7),yerr=np.std(its),bottom=m1,ecolor="k",linewidth=0.5)
			pctimp = (m1+m2)*-100+100
			text(ind+width/2,max(1.04,1.0+(-pctimp/100)*4),str(int(pctimp)),horizontalalignment="center",verticalalignment="bottom")
			ind += width + barspace

		xinds.append(ind-len(caselens)*float(width+barspace)/2.0)
		labels.append(ana.shorturl(url))

		ind += width

	handle3 = plot([0,ind-width],[1,1],'k-',color=color(1),linewidth=1)
	legend([handle1,handle2],["Javascript","Compiler"],loc="upper right",ncol=2)

	ylim((0,1.5))
	aprops = dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90,rad=10")
	basex = width*3.0/2.0 #base x position to annotate
	annotate("default: Ships in Chromium",(basex,1.1),xytext=(basex+0.1,1.4),xycoords="data",arrowprops=aprops)
	basex += width+barspace
	annotate("sel_off: Select Optimizations Off",(basex,1.1),xytext=(basex+0.2,1.3),xycoords="data",arrowprops=aprops)
	basex += width+barspace
	annotate("no_opt: No Optimization",(basex,1.1),xytext=(basex+0.2,1.2),xycoords="data",arrowprops=aprops)

	xticks(xinds,labels)
	ylabel("Normalized Ticks")

#Create plots from overall set of data
def plots_overall():
	cfg = Config()
	ana = Analyzer(os.path.join(cfg.tmpdir,"overall"))
	ana.loadall()

	plot_percentages(ana)
	saveplot("fig_overallperf")

#Create plots from switched optimization set of data
#@param ana analyzer
#@param case which case to look at (string for shortened name)
#@param dolegend turn on the legend if true
#@author ishafer
def plot_opts(ana,case,dolegend=False):
	xbins = [
		("default", lambda f: len(f) == 0),
		("sel_off", lambda f: f["crankshaft"] \
			and len(filter(lambda x: x, f.values())) == 1), 
		("no_opt", lambda f: not f["crankshaft"]),
		("canonical", lambda f: f["use_canonicalizing"]),
		("gvn", lambda f: f["use_gvn"]),
		("licm", lambda f: f["loop_invariant_code_motion"]),
		("range", lambda f: f["use_range"]),
		("deadphi", lambda f: f["eliminate_dead_phis"]),
		("for_in", lambda f: f["optimize_for_in"]),
		("use_inline", lambda f: f["use_inlining"] \
			and not f["limit_inlining"] \
			and not f["inline_arguments"] \
			and not f["polymorphic_inlining"] \
			and not f["inline_construct"]),
		("limit_inline", lambda f: f["limit_inlining"]),
		("args_inline", lambda f: f["inline_arguments"]),
		("poly_inline", lambda f: f["polymorphic_inlining"]),
		("cons_inline", lambda f: f["inline_construct"])
	]
	items = [list() for n in xrange(len(xbins))]

	"""
	{
		"crankshaft":False,
		"use_canonicalizing":False,
		"use_gvn":False,
		"loop_invariant_code_motion":False,
		"use_range":False,
		"eliminate_dead_phis":False,
		"use_inlining":False,
		"limit_inlining":False,
		"inline_arguments":False,
		"always_opt":False,
		"polymorphic_inlining":False,
		"inline_construct":False,
		"optimize_for_in":False
	}
	"""

	for tup in ana.tuples:
		if not tup[TDX_ISPROF]:
			continue
		shorturl = ana.shorturl(tup[TDX_URL])
		if shorturl != case:
			continue
		pp = tup[TDX_PROF]
		for dx in xrange(len(xbins)):
			if xbins[dx][1](pp.info()["flags"]):
				items[dx].append(pp.summary())
				break

	fig = figure(figsize=(3.2,2.5))
	ind = np.arange(len(xbins))
	ind[3:] += 1 #apparently pylab can't deal with float ind spacing

	width = 1.0
	#normalize to sel_opt (1) case
	normt = np.mean([it["js"] + it["compiler"] for it in items[1]])

	m1 = [np.mean([float(it["js"]) / normt for it in subitem]) for subitem in items]
	m2 = [np.mean([float(it["compiler"]) / normt for it in subitem]) for subitem in items]
	s1 = [np.std([float(it["js"]) / normt for it in subitem]) for subitem in items]
	s2 = [np.std([float(it["compiler"]) / normt for it in subitem]) for subitem in items]
	handle1 = bar(ind,m1,width,color=color(0),yerr=s1,ecolor="k",linewidth=0.5)
	handle2 = bar(ind,m2,width,color=(0.7,0.7,0.7),yerr=s2,ecolor="k",linewidth=0.5,bottom=m1)
	pctimp = [(mi1+mi2)*-100+100 for (mi1,mi2) in zip(m1,m2)]
	for dx in xrange(len(ind)):
		text(ind[dx]+width/2.0,\
			max(1.04,1.0+(-pctimp[dx]/100)+0.025),\
			str(int(pctimp[dx])),\
			horizontalalignment="center",verticalalignment="bottom")
			
	ylim((0,1.2))
	handle3 = plot([0,max(ind)+width],[1,1],'k-',color=color(1),linewidth=1)
	if dolegend:
		legend([handle1,handle2],["Javascript","Compiler"],loc="upper left",ncol=2)

	ylabel("Normalized Ticks")
	xticks(ind+width/2.0-0.15,[b[0] for b in xbins],rotation=-40,horizontalalignment="left")
	xlim((0,max(ind)+width))

	fig.subplots_adjust(left=0.15,right=0.85,bottom=0.25,top=0.9)
	title("%s Selective Optimization" % (case))

def plots_selopts():
	cfg = Config()
	ana = Analyzer(os.path.join(cfg.tmpdir,"sel_opts"))
	ana.loadall()

	plot_opts(ana,"Gmail",dolegend=False)
	saveplot("fig_sel_opts_gmail")
	plot_opts(ana,"BenchM",dolegend=False)
	saveplot("fig_sel_opts_benchm")

	plot_compilerpcts(ana)
	saveplot("fig_sel_compilerpct")

def categorizetime(lst):
	times = dict()
	for item in lst:
		time = item[0]
		fname = item[1]
		cat = categorize(fname)
		if cat not in times:
			times[cat] = 0
		#if cat == "Other": #uncategorized names
		#	print time, fname
		times[cat] += time
	return times

#Plot percentages of time taken for different parts of the compiler
# (Lithium, Hydrogen, Assembler, parsing, ...)
#@author ishafer
def plot_compilerpcts(ana):
	testbins = [
		"BenchM",
		"Gmail"
	]
	casebins = [
		("default", lambda f: len(f) == 0),
		("sel_off", lambda f: f["crankshaft"] \
			and len(filter(lambda x: x, f.values())) == 1), 
		("no_opt", lambda f: not f["crankshaft"])
	]
	partbins = [
		("Assembler","Write native code"),
		("Lithium","Produce low-level IR"),
		("Hydrogen","Build, optimize high-level IR"),
		("AST","Create and traverse tree"),
		("Parser","Scan, lex JavaScript source"),
		("LowLevel","Locking, memory, ..."),
		("Shared","Stubs, ICs, deoptimization, ..."),
		("Tracing","Counters, profiling overhead"),
		("Other","Uncategorized")
	]

	items = dict()
	for test in testbins:
		items[test] = dict()
		for (ct,_) in casebins:
			items[test][ct] = dict()
			for (part,_) in partbins:
				items[test][ct][part] = []

	for tup in ana.tuples:
		pp = tup[TDX_PROF]
		if not tup[TDX_ISPROF]:
			continue
		surl = ana.shorturl(tup[TDX_URL])
		if not surl in testbins:
			continue
		for (ct,cf) in casebins:
			if cf(pp.info()["flags"]):
				#compiler C++ time
				cated = categorizetime(pp.profs["c"]["times"]["CPP"])
				for (part,_) in partbins:
					val = 0
					if part in cated:
						val = cated[part]
					else:
						print "%s %s: no time for %s" % (surl, ct, part)
					items[surl][ct][part].append(val)
				break

	fig = figure(figsize=(3.2,6))
	fig.subplots_adjust(left=0.15,right=0.95,bottom=0.05,top=0.7)

	barspace = 0.04
	hs = []
	spdx = 1 #subplot index
	for surl in testbins:
		width = 0.2
		ind = width
		subplot(1,2,spdx)
		ymax = 0
		casedx = 0
		xind = np.arange(len(casebins), dtype=np.float) # x ticks
		for ct in [i for (i,_) in casebins]:
			ystart = 0
			dx = 0
			for (part,_) in partbins:
				m = np.mean(items[surl][ct][part])
				s = np.std(items[surl][ct][part])
				h = bar(ind,m,width,color=color(dx),yerr=s,ecolor="k",linewidth=0.5,bottom=ystart)
				if hs is not None:
					hs.append(h)
				ystart += m
				ymax = max(ystart,ymax)
				dx += 1
			xind[casedx] = ind
			casedx += 1
			ind += width + barspace

			#only create legend once
			if hs is not None:
				hs.reverse()
				pbrev = partbins[:]
				pbrev.reverse()
				pbrev = ["%s: %s" % (f,s) for (f,s) in pbrev]
				legend(hs,pbrev,bbox_to_anchor=(0.0,1.06,2.2,0.5), \
					loc=3,mode="expand", borderaxespad=0.0,prop={'size':8.0})
				hs = None

		ylim(0,(ymax+m)*1.05)
		locs,labels = yticks()
		for lbl in labels:
			lbl.set_rotation(90)
		xticks(xind+width/2.0,[i for (i,_) in casebins])
		if spdx == 1:
			ylabel("Profiler Ticks")
		spdx += 1

		title(surl,fontsize=13)

	#print "\t", filter(lambda (k,v): v, info["flags"].iteritems()) 

#Print time taken out of JS execution time for deoptimization
#@author ishafer
def print_deopttime():
	cfg = Config()
	ana = Analyzer(os.path.join(cfg.tmpdir,"sel_opts"))
	ana.loadall()
	FMTSTR = "%-8s %10s %4s %s"
	print FMTSTR % ("Scenario", "Flags", "Deopt", "Total times")
	for tup in ana.tuples:
		info = tup[TDX_PROF].info()
		if "always_opt" in info["flags"] and info["flags"]["always_opt"]:
			was_always = True
		elif len(info["flags"]) == 0:
			was_always = False
		else:
			continue

		if info["isprofile"]:
			#look for compile time
			surl = ana.shorturl(tup[TDX_URL])
			prof = tup[TDX_PROF]
			deopt_t = 0
			for subi in prof.profs["c"]["times"]["CPP"]:
				#print subi
				if "FullCode" in subi[1]:
					deopt_t += subi[0]
			print FMTSTR % \
				(surl, "always_opt" if was_always else "default", str(deopt_t), prof.summary())
			#print , tup[TDX_PROF].summary()	

if __name__ == '__main__':
	#plots_overall()
	plots_selopts()
	
	#print_deopttime()