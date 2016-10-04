import os

def test_gs_file(filePath):
    with open(filePath) as f:
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
            segs = docSegDic[docId][1:]
            n_segs = 1
            if not get_doc_n_lines(filePath, docId) == segs[-1] + 1:
                n_segs += 1
            i = 0
            while i < len(segs)-1:
                if not segs[i] + 1 == segs[i+1]:
                    n_segs += 1
                n_segs += 1
                i += 2
            if not n_segs == n_clusters:
                print("file: %s docId: %s #segs %i #Clusters %i" % (filePath.split("/")[-1], docId, n_segs, n_clusters))
                
def get_doc_n_lines(labelsPath, docId):
    fileName = labelsPath.split("/")[-1]
    rootDir = labelsPath.replace(fileName, "")
    with open(os.path.join(rootDir, fileName[:-5] + str(docId)), encoding="utf8", errors='ignore') as f:
        lins = f.readlines()
        return len(lins)
    
def check_label_files(rootDir):
    for dir in os.listdir(rootDir):
        for fileName in os.listdir(os.path.join(rootDir, dir)):
            if "label" in fileName:
                test_gs_file(os.path.join(rootDir, dir, fileName))
                
check_label_files("/home/pjdrm/Desktop/minwoo_datasets")
        