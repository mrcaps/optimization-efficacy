#Analyze saved results

from profile import *
import os
import re

TDX_ISPROF = 0
TDX_URL = 1
TDX_HFLAGS = 2
TDX_PROF = 3

#Analyzes a set of ProfileParses from a directory
#@author ishafer
class Analyzer():
	def __init__(self,rootdir):
		self.rootdir = rootdir
		self.parses = []
		#broken down across a couple useful axes
		self.byflags = dict()
		self.byurls = dict()
		#for cubing
		self.tuples = []

	def hashflags(self,pp):
		flags = pp.info()["flags"]
		keys = flags.keys()
		keys.sort()
		hashstr = ""
		for key in keys:
			hashstr += key + str(flags[key])
		return hashstr

	#get the short form of a url
	def shorturl(self,url):
		if "facebook" in url:
			return "Facebook"
		elif "wordpress" in url:
			return "WordPress"
		elif "gmail" in url:
			return "Gmail"
		elif "project" in url:
			return "Trac"
		elif "benchmark" in url:
			return "Bench"
		elif "benchmod" in url:
			return "BenchM"
		else:
			return url

	def print_tuples(self):
		for tup in self.tuples:
			print "%s %5s %9s %4d" % \
				(os.path.split(tup[TDX_PROF].loc)[1],
				"prof" if tup[TDX_ISPROF] else "count", 
				self.shorturl(tup[TDX_URL]), 
				len(tup[TDX_HFLAGS]))

	def loadall(self):
		for fname in os.listdir(self.rootdir):
			fullpath = os.path.join(self.rootdir,fname)
			if os.path.isdir(fullpath):
				pp = ProfileParse(fullpath)

				self.parses.append(pp)
				hashflags = self.hashflags(pp)
				url = pp.info()["url"]
				isprofile = pp.info()["isprofile"]
				self.byflags[hashflags] = pp
				self.byurls[url] = pp
				self.tuples.append((isprofile,url,hashflags,pp))

#categorize the group name for a given function name
#return a single-word string corresponding to the category:
#	Parser, Assembler, Lithium, Hydrogen, ... 
def categorize(fname):
	dx = fname.find("(")
	if dx > -1:
		fname = fname[:dx]
	fname = re.sub(r'\<[^\<]*\>','',fname)
	parts = fname.split("::")

	dx = parts[0].find(" ")
	if dx > -1:
		parts[0] = parts[0][dx+1:]

	if parts[0] == "v8":
		if len(parts) > 0:
			if parts[1] == "preparser":
				return "Parser"
			if parts[1] == "internal":
				if parts[2] in [ \
					"BufferedUtf16CharacterStream",
					"ExternalTwoByteString",
					"ExternalTwoByteStringUtf16CharacterStream",
					"FuncNameInferrer",				
					"GenericStringUtf16CharacterStream",
					"InitializationBlockFinder",
					"InitScriptLineEnds",
					"Match",
					"MaterializedLiteral",
					"ObjectLiteralPropertyChecker",
					"Parser",
					"ParserApi",
					"Scanner",
					"ThisNamedPropertyAssignmentFinder"]:
					return "Parser"

				if parts[2] in [ \
					"Assembler",
					"AssemblerBase",
					"FullCodeGenerator",
					"GlobalObjectOperand",
					"IncrementalMarking",
					"Label",
					"MacroAssembler",
					"NullCallWrapper",
					"PositionsRecorder",
					"RelocInfoWriter",
					"RelocIterator", #relocation information is (e.g.) pc->code marks in generated code
					"StringCharLoadGenerator"]:
					return "Assembler"

				if parts[2] in [ \
					"ArrayLiteral",
					"Assignment",
					"AstConstructionVisitor",
					"AstNode",
					"AstNodeFactory",
					"AstVisitor",
					"BinaryOperation",
					"Block",
					"BreakableStatement",
					"BreakStatement",
					"Call",
					"CallNew",
					"CallRuntime",
					"CaseClause",
					"CompareOperation",
					"Conditional",
					"CountOperation",
					"EmptyStatement",
					"Expression",
					"ExpressionStatement",
					"FieldOperand",
					"ForStatement",
					"FunctionDeclaration",
					"FunctionLiteral",
					"IfStatement",
					"Interface",
					"IterationStatement",
					"Literal",
					"ObjectLiteral",
					"Operand",
					"Processor",
					"Property",
					"RegExpLiteral",
					"ReturnStatement",
					"Rewriter",
					"Scope",
					"ScopeInfo",
					"SequentialSymbolKey",
					"ThisFunction",
					"Throw",
					"Translation",
					"TryCatchStatement",
					"UnaryOperation",
					"Variable",
					"VariableMap",
					"VariableProxy",
					"VariableProxy* v8"]:
					return "AST"

				#Memory related operations like static allocation,
				#  shared function information
				if parts[2] in [ \
					"FreeList",
					"Heap",
					"IncrementalMarkingMarkingVisitor",
					"LargeObjectSpace",
					"MakeOrFindTwoCharacterString",
					"Malloced",
					"MarkCompactCollector",
					"MemoryAllocator",
					"PagedSpace",
					"TemplateHashMapImpl",
					"VirtualMemory",
					"Zone",
					"ZoneList",
					"ZoneListAllocationPolicy",
					"ZoneScope"]:
					return "Memory"

				#Lithium
				if parts[2] in [ \
					"ElementsKindToShiftSize",
					"LAddI",
					"LAllocator",
					"LArithmeticT",
					"LBoundsCheck",
					"LBranch",
					"LCallConstantFunction",
					"LCallFunction",
					"LCallKnownGlobal",
					"LCallNamed",
					"LCheckFunction",
					"LCheckMap",
					"LCheckNonSmi",
					"LCheckPrototypeMaps",
					"LChunk",
					"LChunkBuilder",
					"LCmpIDAndBranch",
					"LCmpMapAndBranch",
					"LCodeGen",
					"LConstantT",
					"LContext",
					"LControlInstruction",
					"LDeoptimize",
					"LFastLiteral",
					"LGap",
					"LGapResolver",
					"LGoto",
					"LInstruction",
					"LInstruction* v8",
					"LInstructionGap",
					"LJSArrayLength",
					"LLabel",
					"LLazyBailout",
					"LLoadContextSlot",
					"LLoadElements",
					"LLoadGlobalCell",
					"LLoadKeyedFastElement",
					"LLoadKeyedGeneric",
					"LLoadNamedField",
					"LLoadNamedFieldPolymorphic",
					"LLoadNamedGeneric",
					"LNumberTagD",
					"LNumberTagI",
					"LNumberUntagD",
					"LParallelMove",
					"LParameter",
					"LPointerMap",
					"LPushArgument",
					"LReturn",
					"LStackCheck",
					"LStoreContextSlot",
					"LStoreGlobalCell",
					"LStoreKeyedFastElement",
					"LStoreNamedGeneric",
					"LTaggedToI",
					"LTemplateInstruction",
					"LThisFunction",
					"LUnallocated",
					"SafepointTableBuilder",
					"TranslationBuffer",
					"UnhandledSortHelper",
					"UseInterval",
					"VariableDeclaration"]:
					return "Lithium"

				#Hydrogen
				if parts[2] in [ \
					"EffectContext",
					"FunctionState",
					"HAdd",
					"HApplyArguments",
					"HArgumentsObject",
					"HArithmeticBinaryOperation",
					"HBasicBlock",
					"HBinaryCall",
					"HBinaryOperation",
					"HBitwise",
					"HBlockEntry",
					"HBoundsCheck",
					"HBranch",
					"HCall",
					"HCallConstantFunction",
					"HCallKnownGlobal",
					"HCallNamed",
					"HCallNew",
					"HChange",
					"HCheckFunction",
					"HCheckMap",
					"HCheckNonSmi",
					"HCheckPrototypeMaps",
					"HCompareGeneric",
					"HCompareIDAndBranch",
					"HCompareMap",
					"HCompareObjectEqAndBranch",
					"HConstant",
					"HContext",
					"HControlInstruction",
					"HDiv",
					"HEnvironment",
					"HFixedArrayBaseLength",
					"HFunctionLiteral",
					"HGlobalObject",
					"HGlobalReceiver",
					"HGlobalReceiver",
					"HGlobalValueNumberer",
					"HGoto",
					"HGraph",
					"HGraphBuilder",
					"HInferRepresentation",
					"HInstanceOfKnownGlobal",
					"HInstruction",
					"HInstruction* v8",
					"HIsNilAndBranch",
					"HIsSmiAndBranch",
					"HJSArrayLength",
					"HLeaveInlined",
					"HLoadContextSlot",
					"HLoadElements",
					"HLoadGlobalCell",
					"HLoadKeyedFastDoubleElement",
					"HLoadKeyedFastElement",
					"HLoadKeyedGeneric",
					"HLoadNamedField",
					"HLoadNamedFieldPolymorphic",
					"HLoadNamedGeneric",
					"HLoopInformation",
					"HMul",
					"HParameter",
					"HPhase",
					"HPhi",
					"HPushArgument",
					"HRangeAnalysis",
					"HReturn",
					"HSar",
					"HShl",
					"HSimulate",
					"HSoftDeoptimize",
					"HStackCheck",
					"HStoreContextSlot",
					"HStoreKeyedGeneric",
					"HStoreNamedField",
					"HStoreNamedGeneric",
					"HStringAdd",
					"HSub",
					"HTemplateControlInstruction",
					"HTemplateInstruction",
					"HThisFunction",
					"HTransitionElementsKind",
					"HType",
					"HUnaryCall",
					"HUnaryControlInstruction",
					"HUnaryOperation",
					"HUnknownOSRValue",
					"HUseConst",
					"HUseIterator",
					"HValue",
					"HValueMap",
					"IsFastLiteral",
					"IsLiteralCompareNil",
					"LiveRange",
					"MakeCrankshaftCode",
					"MatchLiteralCompareTypeof",
					"StoringValueNeedsWriteBarrier",
					"TypeFeedbackOracle",
					"ValueContext"]:
					return "Hydrogen"

				if parts[2] in [ \
					"DeoptimizationInputData",
					"Deoptimizer",
					"AdvanceToNonspace",
					"ArgumentsAccessStub",
					"AsciiSymbolKey",
					"BinaryOpStub",
					"BitVector",
					"Builtins",
					"CallConstructStub",
					"CallFunctionStub",
					"CallICBase",
					"CallOptimization",
					"CallStubCompiler",
					"CEntryStub",
					"Code",
					"CodeGenerator",
					"CodeStub",
					"CompareIC",
					"CompilationCache",
					"CompilationCacheEval",
					"CompilationCacheScript",
					"CompilationCacheTable",
					"CompilationInfo",
					"Compiler",
					"CompileTimeValue",
					"Context",
					"CopyChars",
					"CPU",
					"DescriptorArray",
					"Dictionary",
					"ExitFrame",
					"ExternalReference",
					"Factory",
					"FastCloneShallowArrayStub",
					"FastCloneShallowObjectStub",
					"FastNewContextStub",
					"FixedArray",
					"FlattenGetString",
					"GenerateFastCloneShallowArrayCommon",
					"GetIsolateForHandle",
					"GlobalObject",
					"HandleScope",
					"HashTable",
					"HeapObject",
					"IC",
					"ICCompareStub",
					"InnerPointerToCodeCache",
					"InternalStringToDouble",
					"InternalStringToIntDouble",
					"Isolate",
					"JavaScriptFrame",
					"JSFunction",
					"JSObject",
					"JSReceiver",
					"List",
					"LiveEditFunctionTracker",
					"LoadIC",
					"MakeFunctionInfo",
					"Map",
					"NoAllocationStringAllocator",
					"NumberDictionaryShape",
					"RecordWriteStub",
					"Runtime",
					"Safepoint",
					"SetExpectedNofPropertiesFromEstimate",
					"SharedFunctionInfo",
					"SmallMapList",
					"StackCheckStub",
					"StackFrame",
					"StackFrameIterator",
					"StackGuard",
					"StackLimitCheck",
					"StackTraceFrameIterator",
					"StandardFrame",
					"StoreIC",
					"String",
					"StringCharCodeAtGenerator",
					"StringDictionary",
					"StringInputBuffer",
					"StringKey",
					"StringSearch",
					"StringStream",
					"StringToDouble",
					"Strtod",
					"StubCache",
					"SymbolTable",
					"TestContext",
					"Thread",
					"ToBooleanStub",
					"ToNumberStub",
					"TwoByteSymbolKey",
					"TwoCharHashTableKey",
					"UnseededNumberDictionary",
					"V8"]:
					return "Shared"

				if parts[2] in [ \
					"LinuxMutex",
					"random_base"]:
					return "LowLevel"

				if parts[2] in [ \
					"Debugger",
					"GetScriptLineNumber",
					"HistogramTimer",
					"Logger",
					"LogMessageBuilder",
					"OS",
					"SingletonLogger",
					"StatsCounter"]:
					return "Tracing"

	elif parts[0] in ["__write","_IO_vfprintf",
		"memcpy","madvise","__lll_lock_wait",
		"strchrnul","qsort_r","memmove","new[]",
		"__pthread_getspecific","_IO_default_xsputn",
		"__vsnprintf_chk","_init","__pthread_mutex_lock",
		"__pthread_mutex_unlock","__libc_free",
		"__libc_malloc","_IO_fwrite","_IO_file_sync",
		"_IO_file_xsputn","_IO_fflush","mmap64",
		"_IO_file_write","syscall","delete[]",
		"__mempcpy","__gettimeofday","qsort",
		"_IO_setb","_IO_do_write","_IO_file_xsputn",
		"TCMalloc_SystemAlloc","delete","new","brk",
		"memset","__lll_unlock_wake","sbrk"]:
		return "LowLevel"
	elif parts[0] == "unibrow":
		return "Parser"
	elif parts[0] == "WebCore":
		return "Shared"
	elif parts[0] == "tcmalloc":
		return "Memory"
	elif parts[0] == "base":
		if parts[1] in [ \
			"Debugger",
			"Histogram",
			"StatisticsRecorder"]:
			return "Tracing"
	elif parts[0] == "AddHistogramSample":
		return "Tracing"
	elif parts[0] == "WTF":
		if parts[1] in ["StringImpl"]:
			return "Shared"

	return "Other"

if __name__ == '__main__':
	cfg = Config()
	ana = Analyzer(os.path.join(cfg.tmpdir,"overall"))
	ana.loadall()
	ana.print_tuples()