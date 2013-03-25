OptimizationsHGraphBuilder::VisitForInStatement

# Hydrogen
 See https://github.com/v8/v8/blob/master/src/hydrogen.cc in HGraphBuilder::CreateGraph()

## Main graph build
 * Set up entry point
 * HGraph::OrderBlocks()
 * HGraph::AssignDominators()
 * if debug, verify graph
 * HGraph::PropagateDeoptimizingMark()
 * HGraph::EliminateRedundantPhis()
 * `--eliminate_dead_phis` controls HGraph::EliminateUnreachablePhis()
 * HGraph::CollectPhis()
 * on-stack replacement and phi nodes
 * `--use-canonicalizing` controls HGraph::Canonicalize()
 * `--use_gvn` controls HGlobalValueNumberer
   * `--loop_invariant_code_motion` controls LoopInvariantCodeMotion()
 * `--use_range` controls HRangeAnalysis
 * HGraph::ComputeMinusZeroChecks()
 * HStackCheckEliminator

## Things we might consider commenting out
 * InitializeInferredTypes (in CreateGraph)
 * HInferRepresentation specialized representation of value based on param
 * IsAllocationInlineable

## Other places
 * HGraphBuilder::TryInline()
   * `--use_inlining=false` bails from function
   * `--limit_inlining=false` bails under certain conditions (code size too large)
   * `--inline_arguments=false` will bail if code uses arguments variable
 * HGraphBuilder::BuildLoadNamedGeneric
   * `--always_opt` controls adding a HSoftDeoptimize
 * HGraphBuilder::HandlePolymorphicCallNamed
   * `--polymorphic_inlining` controls whether we try to inline the call
 * HGraphBuilder::VisitCallNew()
   * `--inline_construct=false` will bail from inlining
 * HGraphBuilder::VisitForInStatement()
   * `--optimize-for-int`

#Important non-Hydrogen
 * `--use_ic` - inline caching is critical (v8 benchmarks for example become MUCH slower)

