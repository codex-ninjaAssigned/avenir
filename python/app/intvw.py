#!/usr/local/bin/python3

# avenir-python: Machine Learning
# Author: Pranab Ghosh
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

import os
import sys
from random import randint
import time
sys.path.append(os.path.abspath("../lib"))
sys.path.append(os.path.abspath("../mlextra"))
from util import *
from sampler import *
from hbias import *

"""
candidate phone interview
"""
def setParam(incFeat, pfeCol):
	"""
	set up 
	"""
	fe = [2, "B"] if incFeat else None
	pfe = [1, "M"] if pfeCol == 1 else [4, "L"]
	cl = [6, "T"]
	return (fe, pfe, cl)

if __name__ == "__main__":

	op = sys.argv[1]
	classes = ["T", "F"]
	sex = ["M", "F"]
	education = ["H", "B", "M"]
	ftypes = [3, "int", 5, "int"]


	if op == "gen":
		"""
		generate data
		"""
		numSample = int(sys.argv[2])
		noise = float(sys.argv[3])
	
		selDistr = CategoricalRejectSampler(("T", 30), ("F", 70))
		featCondDister = {}

		#sex
		key = ("T", 0)
		distr = CategoricalRejectSampler(("M", 60), ("F", 40))
		featCondDister[key] = distr
		key = ("F", 0)
		distr = CategoricalRejectSampler(("M", 60), ("F", 40))
		featCondDister[key] = distr
		
		#education
		key = ("T", 1)
		distr = CategoricalRejectSampler(("H", 20), ("B", 40), ("M", 30))
		featCondDister[key] = distr
		key = ("F", 1)
		distr = CategoricalRejectSampler(("H", 30), ("B", 20), ("M", 10))
		featCondDister[key] = distr
		
		#experience
		key = ("T", 2)
		distr = NonParamRejectSampler(1, 1, 10, 20, 35, 60, 60)
		featCondDister[key] = distr
		key = ("F", 2)
		distr = NonParamRejectSampler(1, 1, 25, 30, 15, 10, 5)
		featCondDister[key] = distr
		
		#employment gap
		key = ("T", 3)
		distr = CategoricalRejectSampler(("L", 80), ("H", 20))
		featCondDister[key] = distr
		key = ("F", 3)
		distr = CategoricalRejectSampler(("L", 30), ("H", 70))
		featCondDister[key] = distr

		#phone interview
		key = ("T", 4)
		distr = NonParamRejectSampler(1, 1, 10, 20, 30, 40, 45)
		featCondDister[key] = distr
		key = ("F", 4)
		distr = NonParamRejectSampler(1, 1, 35, 25, 15, 10, 5)
		featCondDister[key] = distr

		sampler = AncestralSampler(selDistr, featCondDister, 5)
		egsampler = dict()
		egsampler["M"] = CategoricalRejectSampler(("L", 80), ("H", 20))
		egsampler["F"] = CategoricalRejectSampler(("L", 30), ("H", 70))

		for i in range(numSample):
			(claz, features) = sampler.sample()
			egap = egsampler[features[0]].sample()
			features[3] = egap
			claz = addNoiseCat(claz, classes, noise)
			strFeatures = list(map(lambda f : toStr(f, 3), features))
			rec =  genID(10) + "," + ",".join(strFeatures) + "," + claz
			print(rec)

	elif op == "rgen":
		"""
		removes gender
		"""
		fpath = sys.argv[2]
		columns = [0,2,3,4,5,6]
		for rec in fileSelFieldsRecGen(fpath, columns):
			print(",".join(rec))
		
	elif op == "bias":
		"""
		add human bias
		"""
		fpath = sys.argv[2]
		bias = int(sys.argv[3])
		for rec in fileRecGen(fpath):
			if isEventSampled(bias):
				if rec[1] == "M":
					rec[6] = "T"
			print(",".join(rec))

	elif op == "elift":
		"""
		extended lift
		"""
		fpath = sys.argv[2]
		incFeat = sys.argv[3] == "f"
		pfeCol = int(sys.argv[4])
		bd = BiasDetector(fpath, ftypes)
		(fe, pfe, cl) = setParam(incFeat, pfeCol)
		re = bd.extLift(pfe, cl, fe)
		printMap(re, "item", "value", 3, 32)
		
	elif op == "pelift":
		"""
		proxy extended lift
		"""
		fpath = sys.argv[2]
		incFeat = sys.argv[3] == "f"
		pfeCol = int(sys.argv[4])
		bd = BiasDetector(fpath, ftypes)
		(fe, pfe, cl) = setParam(incFeat, pfeCol)
		ppfe = [4, "L"]
		re = bd.proxyExtLift(fpath, ftypes, fpath, ftypes, pfe, ppfe, cl, fe)
		printMap(re, "item", "value", 3, 32)

	elif op == "clift":
		"""
		contrasted lift
		"""
		fpath = sys.argv[2]
		incFeat = sys.argv[3] == "f"
		pfeCol = int(sys.argv[4])
		bd = BiasDetector(fpath, ftypes)
		fe = [2, "B"] if incFeat else None
		pfe = [1, "M", "F"] if pfeCol == 1 else [4, "L", "H"]
		cl = [6, "T"]
		re = bd.contrLift(pfe, cl, fe)
		printMap(re, "item", "value", 3, 40)

	elif op == "pclift":
		"""
		proxy contrasted lift
		"""
		fpath = sys.argv[2]
		incFeat = sys.argv[3] == "f"
		pfeCol = int(sys.argv[4])
		bd = BiasDetector(fpath, ftypes)
		fe = [2, "B"] if incFeat else None
		pfe = [1, "M", "F"] if pfeCol == 1 else [4, "L", "H"]
		cl = [6, "T"]
		ppfe = [4, "L", "H"]
		re = bd.proxyContrLift(fpath, ftypes, fpath, ftypes, pfe, ppfe, cl, fe)
		printMap(re, "item", "value", 3, 32)

	elif op == "odds":
		"""
		extended lift
		"""
		fpath = sys.argv[2]
		incFeat = sys.argv[3] == "f"
		pfeCol = int(sys.argv[4])
		bd = BiasDetector(fpath, ftypes)
		(fe, pfe, cl) = setParam(incFeat, pfeCol)
		re = bd.odds(pfe, cl, fe)
		printMap(re, "item", "value", 3, 32)

	elif op == "olift":
		"""
		extended lift
		"""
		fpath = sys.argv[2]
		incFeat = sys.argv[3] == "f"
		pfeCol = int(sys.argv[4])
		bd = BiasDetector(fpath, ftypes)
		(fe, pfe, cl) = setParam(incFeat, pfeCol)
		re = bd.olift(pfe, cl, fe)
		printMap(re, "item", "value", 3, 32)

	elif op == "sparity":
		"""
		statistical parity
		"""
		fpath = sys.argv[2]
		bd = BiasDetector(fpath, ftypes)
		pfe = [1, "M"]
		cl = [6, "T"]
		re = bd.statParity(pfe, cl)
		printMap(re, "item", "value", 3, 32)

	else:
		exitWithMsg("invalid command")
		
		