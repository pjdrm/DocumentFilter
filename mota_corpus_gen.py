'''
Created on Aug 30, 2016

@author: root
'''
import os
from shutil import copyfile
import ntpath
import shutil

configTemplate = "﻿<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<config language=\"en\">\n<counts>\n<enhancer>\n<!-- Dir where the documents that will ehance the counts of a target document are-->\n<docsDir>$ENHANCER_DIR</docsDir>\n<!-- Maximum number of used enhancing sentences\nN = 5 means that each sentence will be added the counts of the 5 most similar ones-->\n<N>20</N>\n<nTfIdf>100</nTfIdf>\n</enhancer>\n</counts>\n</config>"
script_template = "/usr/lib/jvm/java-7-openjdk-amd64/bin/java -cp \"classes:lib/commons-io-2.4.jar:lib/colt.jar:lib/lingpipe-3.4.0.jar:lib/MinCutSeg.jar:lib/mtj.jar:lib/options.jar:lib/log4j-1.2.14.jar\" edu.mit.nlp.segmenter.SegTester -config config/dp.config -dir $TEST_DIR -suff .txt -configEnhancer $CONFIG_FILE > $RESULTS"

def gen_mota_corpus(docsDir, outDir):
    for doc in os.listdir(docsDir):
        if "html" in doc:
            dest = os.path.join(outDir, "docs_html")
        elif "pdf" in doc:
            dest = os.path.join(outDir, "docs_pdf")
        elif "ppt" in doc:
            dest = os.path.join(outDir, "docs_ppt")
        elif "_v" in doc:
            dest = os.path.join(outDir, "docs_video")
        copyfile(os.path.join(docsDir, doc), os.path.join(dest, "tests", doc))
        copyfile(os.path.join(docsDir, doc), os.path.join(dest, "enhancers", doc))
        copyfile(os.path.join(docsDir, doc), os.path.join(outDir, "docs_all/tests", doc))
        copyfile(os.path.join(docsDir, doc), os.path.join(outDir, "docs_all/enhancers", doc))
        
def run(docsDir, dataDir, configDir, resultsDir):
    if os.path.isdir(dataDir):
        shutil.rmtree(dataDir)
    os.makedirs(dataDir)
    
    if os.path.isdir(configDir):
        shutil.rmtree(configDir)
    os.makedirs(configDir)
    
    if os.path.isdir(resultsDir):
        shutil.rmtree(resultsDir)
    os.makedirs(resultsDir)
        
    script_txt = ""
    for dir in os.listdir(docsDir):
        os.makedirs(os.path.join(configDir, dir))
        os.makedirs(os.path.join(resultsDir, dir))
        dest = os.path.join(dataDir, dir)
        os.makedirs(dest)
        exp_dirs = ["docs_all"]
        exp_dirs += ["docs_html"]
        exp_dirs += ["docs_pdf"]
        exp_dirs += ["docs_ppt"]
        exp_dirs += ["docs_video"]
        for doc_type_dir in exp_dirs:
            testDir = os.path.join(dest, doc_type_dir, "tests")
            enhanceDir = os.path.join(dest, doc_type_dir, "enhancers")
            os.makedirs(testDir)
            os.makedirs(enhanceDir)
            
            configFile = os.path.join(configDir, dir, dir + "_" + doc_type_dir + ".xml")
            with open(configFile, "w+") as f:
                f.write(configTemplate.replace("$ENHANCER_DIR", enhanceDir))
                
            script_txt += script_template.replace("$TEST_DIR", testDir).replace("$CONFIG_FILE", configFile).replace("$RESULTS", os.path.join(resultsDir, dir, doc_type_dir + "_results.txt")) + "\n"
        gen_mota_corpus(os.path.join(docsDir, dir), dest)
    with open("mota_experiments.sh", "w+") as f:
        f.write(script_txt[:-1])
run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted/", "mota_corpus", "mota_config", "mota_results")
        