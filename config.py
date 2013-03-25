#Framework configuration
import json
import os
import logging as log

#Global configuration information from config.json
# usage: cfg = Config(); cfg.<config-key-name>
#@author ishafer
class Config():
	__cfg = None

	def __init__(self,loc="config.json"):
		if Config.__cfg is None:
			#load Config
			fp = open(loc)
			Config.__cfg = json.load(fp)
			Config.__cfg["scriptdir"] = \
				os.path.dirname(os.path.realpath(__file__))
			log.basicConfig(level=self.loglevel)
			fp.close()

	def __getattr__(self, attr):
		return self.__cfg[attr]

def test_config():
	cfg = Config()
	print "chromeloc:", cfg.chromeloc
	print "sikuliloc:", cfg.sikuliloc
	print "script:", cfg.scriptdir

def check_config():
	cfg = Config()
	if not os.path.exists(cfg.chromeloc):
		print "Error: Could not find directory " + cfg.chromeloc

if __name__ == "__main__":
	check_config()

