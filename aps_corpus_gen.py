'''
Created on Aug 30, 2016

@author: root
'''
import os
from shutil import copyfile
import ntpath
import shutil

configTemplate = "-run\n-preference -1\n-damping 0.9\n-windowSize 250\n-inputDir $INPUT_DIR\n-outputDir $OUTPUT_DIR\n-inputExtensions txt\n-corpusExtensions dev,txt\n-resultFile summary_results.txt\n-sparse true\n-useSegmentDf true\n-numTFIDFsegments 30\n-smoothingAlpha 1.45\n-smoothingWindow 2"
script_template = "java -jar -Xms1000m -Xmx6500m build/jar/APS.jar -config $APS_DIR/$CONFIG > $RESULTS"

def gen_aps_corpus(docsDir, outDir):
    for doc in os.listdir(docsDir):
        if "html" in doc:
            dest = os.path.join(outDir, "docs_html")
        elif "pdf" in doc:
            dest = os.path.join(outDir, "docs_pdf")
        elif "ppt" in doc:
            dest = os.path.join(outDir, "docs_ppt")
        elif "_v" in doc:
            dest = os.path.join(outDir, "docs_video")
        with open(os.path.join(docsDir, doc), encoding="utf8", errors='ignore') as f:
            str_doc = f.read()
            str_doc = str_doc[11:]
            str_doc = str_doc.replace("==========", "\n==========")
        with open(os.path.join(dest, doc), "w+") as f1:
            f1.write(str_doc)
            
        with open(os.path.join(dest, doc), "w+") as f1:
            f1.write(str_doc)
            
        with open(os.path.join(outDir, "docs_all/", doc), "w+") as f2:
            f2.write(str_doc)
        
def run(docsDir, dataDir, configDir, resultsDir, apsRoot):
    if os.path.isdir(dataDir):
        shutil.rmtree(dataDir)
    os.makedirs(dataDir)
    
    if os.path.isdir(configDir):
        shutil.rmtree(configDir)
    os.makedirs(configDir)
    
    if os.path.isdir(resultsDir):
        shutil.rmtree(resultsDir)
    os.makedirs(resultsDir)
        
    script_txt = "APS_DIR=.\n"
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
            os.makedirs(os.path.join(resultsDir, dir, doc_type_dir))
            testDir = os.path.join(dest, doc_type_dir)
            os.makedirs(testDir)

            configFile = os.path.join(configDir, dir, dir + "_" + doc_type_dir + ".xml")
            with open(configFile, "w+") as f:
                f.write(configTemplate.replace("$INPUT_DIR", apsRoot + testDir).replace("$OUTPUT_DIR", os.path.join(apsRoot, resultsDir, dir, doc_type_dir)))
                
            script_txt += script_template.replace("$CONFIG", configFile).replace("$RESULTS", os.path.join(resultsDir, dir, doc_type_dir, "individual_results.txt")) + "\n"
        gen_aps_corpus(os.path.join(docsDir, dir), dest)
    with open("aps_experiments.sh", "w+") as f:
        f.write(script_txt[:-1])
        
run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted/", "aps_corpus", "aps_config", "aps_results", "/home/pjdrm/workspace/ap_segmentation/")
        