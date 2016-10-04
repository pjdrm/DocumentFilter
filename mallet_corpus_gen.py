'''
Created on Aug 23, 2016

@author: root
'''
import os
import shutil

def getSegments(docsDir):
    files_list = []
    file_names = []
    for path, dirs, files in os.walk(docsDir):
            for f in files:
                if f in file_names:
                    continue
                files_list.append(os.path.join(path, f))
    docs = []
    for file_path in files_list:
        with open(file_path, encoding="utf8", errors='ignore') as f:
            doc = f.read()
            docSegs = doc.split("==========\n")[1:]
            docSegs[-1] = docSegs[-1][:-11]
            for seg in docSegs:
                docs.append(seg)
    return docs

def getDocs(docsDir):
    files_list = []
    file_names = []
    for path, dirs, files in os.walk(docsDir):
            for f in files:
                if f in file_names:
                    continue
                files_list.append(os.path.join(path, f))
    docs = []
    for file_path in files_list:
        with open(file_path, encoding="utf8", errors='ignore') as f:
            doc = f.read()
            doc = doc.replace("==========\n", "")[:-11]
            docs.append(doc)
    return docs

def run(docsDir, outDir, corpusType):
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)
    os.makedirs(outDir)
    txts = None
    if corpusType == "segs":
        txts = getSegments(docsDir)
    elif corpusType == "docs":
        txts = getDocs(docsDir)
        
    for i, seg in enumerate(txts):
        with open(os.path.join(outDir, "seg_" + str(i) + ".txt"), "w+", encoding="utf8", errors='ignore') as f:
            f.write(seg)

run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted/L02", "mallet_corpus/segs", "segs")
run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted/L02", "mallet_corpus/docs", "docs")
