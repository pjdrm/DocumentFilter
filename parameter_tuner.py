import subprocess
import time

class Parameter(object):
    def __init__(self, paramName, stepSize, param_init, maxSteps = 5):
        self.param_val = param_init
        self.stepSize = stepSize
        self.maxSteps = maxSteps
        self.paramName = paramName
    
    def step_val(self, dir):
        self.param_val += self.stepSize*dir
        
class SegmentationParamOptimizer(object):
    def __init__(self, parameters, maxIter, testDir, configEnhancer, resFile):
        self.parameters = parameters
        self.maxIter = maxIter
        self.testDir = testDir
        self.configEnhancer = configEnhancer
        self.bestWD = 1.0
        self.resFile = resFile
        
    def param_tuner(self, param, dir):
        newBestWD = self.bestWD
        bestParamVal = param.param_val
        for i in range(param.maxSteps):
            prev_val = param.param_val
            param.step_val(dir)
            if param.param_val <= 0:
                break
            currentWD = self.testParameters(self.parameters)
            #print("%s %d %s %d WD =%f" % (self.parameters[0].paramName, self.parameters[0].param_val, self.parameters[1].paramName, self.parameters[1].param_val, currentWD))
            if currentWD < newBestWD:
                newBestWD = currentWD
                bestParamVal = param.param_val
        param.param_val = bestParamVal    
        return newBestWD
            
    def optimize(self):
        for i in range(self.maxIter):
            start_time = time.time()
            for param in self.parameters:
                base_val = param.param_val
                wd = self.param_tuner(param, 1)
                if wd < self.bestWD:
                    self.bestWD = wd
                    continue                
                wd = self.param_tuner(param, -1)
                if wd < self.bestWD:
                    self.bestWD = wd
                    continue
                else:
                    param.param_val = base_val
            print("Iter %d WD: %f" % (i, self.bestWD))
            print("--- %s seconds ---" % (time.time() - start_time))
        self.genConfig(self.parameters)
        print("N %d nTfidf %d WD %f" % (self.parameters[0].param_val, self.parameters[1].param_val, self.bestWD))
        with open(self.resFile, "w+") as f:
            f.write("WD: " + str(self.bestWD))
                    
    def genConfig(self, params):
        configTemplate = "﻿<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<config language=\"en\">\n<counts>\n<enhancer>\n<docsDir>"+ self.testDir.replace("tests", "") + "enhancers</docsDir>\n<N>" + str(params[0].param_val) + "</N>\n<nTfIdf>" + str(params[1].param_val) + "</nTfIdf>\n<minSim>0.2</minSim>\n</enhancer>\n</counts>\n</config>"
        with open(self.configEnhancer, "w+") as f:
            f.write(configTemplate)
        
    def getWD(self, result_str):
        try:
            return float(str(result_str[-1]).split(" ")[-1][:-3])
        except:
            return 1.0
    
    def testParameters(self, params):
        self.genConfig(params)
        command = "java -cp \"/home/pjdrm/workspace/bayeseg-MD/classes:/home/pjdrm/workspace/bayeseg-MD/lib/commons-io-2.4.jar:/home/pjdrm/workspace/bayeseg-MD/lib/colt.jar:/home/pjdrm/workspace/bayeseg-MD/lib/lingpipe-3.4.0.jar:/home/pjdrm/workspace/bayeseg-MD/lib/MinCutSeg.jar:/home/pjdrm/workspace/bayeseg-MD/lib/mtj.jar:/home/pjdrm/workspace/bayeseg-MD/lib/options.jar:/home/pjdrm/workspace/bayeseg-MD/lib/log4j-1.2.14.jar\" edu.mit.nlp.segmenter.SegTester -config /home/pjdrm/workspace/bayeseg-MD/config/dp.config -dir " + self.testDir + " -suff .txt -configEnhancer " + self.configEnhancer
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = ""
        result = p.stdout.readlines()
        return self.getWD(result)
    
maxSteps = 10
nDocsParam = Parameter("N", 10, 10, maxSteps)
nTfidfParam = Parameter("nTfidf", 10, 20, maxSteps)
nIters = 20

'''
optimizer = SegmentationParamOptimizer([nDocsParam, nTfidfParam], nIters, "/home/pjdrm/workspace/TopicSegmentationScripts/parameter_tuning/dev_set/L03/video/tests", "parameter_tuning/best_configs/L03/L03_docs_video_tuned.xml", "parameter_tuning/results/L03/video_results.txt")
optimizer.optimize()

optimizer = SegmentationParamOptimizer([nDocsParam, nTfidfParam], nIters, "/home/pjdrm/workspace/TopicSegmentationScripts/parameter_tuning/dev_set/L03/html/tests", "parameter_tuning/best_configs/L03/L03_docs_html_tuned.xml", "parameter_tuning/results/L03/html_results.txt")
optimizer.optimize()

optimizer = SegmentationParamOptimizer([nDocsParam, nTfidfParam], nIters, "/home/pjdrm/workspace/TopicSegmentationScripts/parameter_tuning/dev_set/L03/pdf/tests", "parameter_tuning/best_configs/L03/L03_docs_pdf_tuned.xml", "parameter_tuning/results/L03/pdf_results.txt")
optimizer.optimize()

optimizer = SegmentationParamOptimizer([nDocsParam, nTfidfParam], nIters, "/home/pjdrm/workspace/TopicSegmentationScripts/parameter_tuning/dev_set/L03/ppt/tests", "parameter_tuning/best_configs/L03/L03_docs_ppt_tuned.xml", "parameter_tuning/results/L03/ppt_results.txt")
optimizer.optimize()
'''

optimizer = SegmentationParamOptimizer([nDocsParam, nTfidfParam], nIters, "/home/pjdrm/workspace/TopicSegmentationScripts/parameter_tuning/dev_set/L03/docs_all/tests", "parameter_tuning/best_configs/L03/L03_docs_all_tuned.xml", "parameter_tuning/results/L03/all_results.txt")
optimizer.optimize()
    
    