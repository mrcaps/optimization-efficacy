# Quantifying Optimization Efficacy

 * Instrumenting V8 to Measure the Efficacy of Dynamic Optimizations on Production Code
 * 15-745, Spring 2012

## Contents

This folder contains the source code for the framework described in the accompanying paper. It consists of multiple parts:

 * `*.py`: The analysis and launch framework for Chromium
 * `*.sikuli`: Sikuli scripts used for UI automation
 * `v8` folder: Modified internal source of v8 for adding counter instrumentation. These replace source files in the `src/v8` subdirectory of the Chromium browser, revision 128907.
 * `tools`: A modified version of the tick aggregator for the V8 sampling profiler.
 * `res`: A few assorted notes

## Configuration

First, build Chromium following the build instructions and the modified sources in the `v8` folder to produce a `chromium` executable and install the Sikuli UI testing framework.

Create a `config.json` file and enter the following, but with the correct location for your Chromium and Sikuli installs and a temporary directory for the benchmarking output:

```
{
	"chromeloc":"/usr0/home/mmaass/chromium/src/out/Debug",
	"sikuliloc":"/usr0/home/mmaass/Downloads/Sikuli/Sikuli-IDE",
	"tmpdir":"/usr0/home/mmaass/v8_bench",
	"loglevel":20
}
```

There cannot be a space in the path to Sikuli.

The picture of the cup must be in the Pictures directory of the Ubuntu install that is running the Wordpress sikuli test.

## Running Tests

To run one of the automated tests, take a look inside `test.py`. The `testwrap` wrapper contains a number of examples of how to run tests - execute `python test.py` to see it run. Run configuration is controlled with:

 * `run.flags(flag_dict)` specifies which optimizations should be disabled/enabled when running Chrome. See the paper for details on what these flags control.
 * `run.launch(target_site,ui_script,profiling_on)` opens an instance of Chromium to site `target_site` using automation script `ui_script`. `profiling_on=True` turns on the profiler, and `profiling_on=False` records internal counter information.

Results will be placed in the `tmpdir` specified in `config.json` under a timestamped directory. The `info.json` output file within that folder will contain information about the run parameters. `chrome.py` does the work of bootstrapping Chromium.

## Analyzing Results

`plots.py` and its associated analysis scripts (`analyze.py`, `profile.py`) perform the results analysis. The three figures in the paper are generated with `plots_overall()` and `plots_selopts()`. We have not included the test output required to generate these results since it is large (100MB); please contact us if you would like it. It is possible to regenerate it by following the test instructions above, but this is a nontrivial endeavor.