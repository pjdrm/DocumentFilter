import os
import shutil
from boto import config

def mw2jacob_corpus_gen(labelsPath, outDir):
    with open(labelsPath) as f:
        lins = f.readlines()
        n_clusters = len(lins)
        docSegDic = {}
        for lin in lins:
            lin = lin[:-1]
            linSplit = lin.split(" ")[1:]
            for seg in linSplit:
                segSplit = seg.split("::")
                docId = segSplit[0]
                if not docId in docSegDic:
                    docSegDic[docId] = []
                limSplit = segSplit[1].split("-")
                docSegDic[docId].append(int(limSplit[0]))
                docSegDic[docId].append(int(limSplit[1]))
                
    for docId in docSegDic:
        docSegDic[docId].sort()
        docFileName = labelsPath.split("/")[-1]
        rootDir = labelsPath.replace(docFileName, "")
        docFullPath = os.path.join(rootDir, docFileName[:-5] + str(docId))
        converted_doc = corpus_converter(docSegDic[docId], docFullPath, docId)
        with open(os.path.join(outDir, docFileName[:-5] + str(docId) + ".ref"), "w+", encoding="utf8", errors='ignore') as f:
            f.write(converted_doc)
        
def corpus_converter(segs, docFileName, docId):
    segs = fill_missing_segs(segs, docFileName)
    with open(docFileName, encoding="utf8", errors='ignore') as f:
        lins = f.readlines()
        j = 1
        converted_txt = "==========\n"
        for i, lin in enumerate(lins):
            converted_txt += lin                
            if j < len(segs)-1 and i == segs[j]:
                converted_txt += "==========\n"
                j += 2
        converted_txt += "=========="
    return converted_txt

def fill_missing_segs(segs, docFilePath):
    new_seg = []
    i = 1
    if not segs[0] == 0:
        new_seg.append(0)
        new_seg.append(segs[0] - 1)
        
    while i < len(segs):
        new_seg.append(segs[i-1])
        new_seg.append(segs[i])
        if i < len(segs) - 1 and not segs[i] + 1 == segs[i + 1]:
            new_seg.append(segs[i] + 1)
            new_seg.append(segs[i + 1] - 1)
        i += 2
        
    n_lins = get_doc_n_lines(docFilePath)
    if not segs[-1] == n_lins - 1:
        new_seg.append(segs[-1] + 1)
        new_seg.append(n_lins-1)
    return new_seg

def get_doc_n_lines(docFilePath):
    with open(docFilePath, encoding="utf8", errors='ignore') as f:
        lins = f.readlines()
        return len(lins)
    
def run_converter(rootDir, outDir):
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)
    os.makedirs(outDir)
    i = 0
    for fileName in os.listdir(rootDir):
        if "label" in fileName:
            dest = os.path.join(outDir, "domain" + str(i))
            os.makedirs(dest)
            i += 1
            mw2jacob_corpus_gen(os.path.join(rootDir, fileName), dest)
    
def run(docDirs, results_rootDir, configs, resDirs):
    if os.path.isdir(results_rootDir):
        shutil.rmtree(results_rootDir)
    os.makedirs(results_rootDir)
    script = "CLASSPATH=\"classes:lib/colt.jar:lib/lingpipe-3.4.0.jar:lib/MinCutSeg.jar:lib/mtj.jar:lib/options.jar:lib/log4j-1.2.14.jar\"\n"
    for config, resDir in zip(configs, resDirs):
        os.makedirs(os.path.join(results_rootDir, resDir))
        for dir in os.listdir(docDirs):
            dest = os.path.join(results_rootDir, resDir, dir)
            os.makedirs(dest)
            script += "java -cp ${CLASSPATH} edu.mit.nlp.segmenter.SegTester -config " + config + " -dir data/physics_lectures_md/" + dir + " -suff .txt > " + dest + "/results.txt\n"
        with open("run_jacob_exp.sh", "w+") as f:
            f.write(script[:-1])
        
run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted", "jacob_results", ["config/dp.config", "config/mcsopt.ai.config", "config/lcseg.config", ], ["bayeseg", "mincut", "lseg"])
#run_converter("/home/pjdrm/Desktop/minwoo_datasets/News/", "mw_data2_jacob")