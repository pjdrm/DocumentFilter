import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')

def segs_count(seg_dic, filePath):
    with open(filePath, encoding="utf8", errors='ignore') as f:
        lins = f.readlines()[1:-1]
        i = 0
        for lin in lins:
            lin = lin.strip()
            if lin == "==========":
                seg_dic[i-1] += 1
            else:
                i += 1
                
    return seg_dic

def init_seg_dic(doc_full_dir):
    doc = os.listdir(doc_full_dir)[0]
    seg_dic = {}
    with open(os.path.join(doc_full_dir, doc)) as f:
        lins = f.readlines()
        i = 0
        for lin in lins:
            lin = lin.strip()
            if lin == "==========":
                continue
            else:
                seg_dic[i] = 0
                i += 1
    return seg_dic

def plot_annotations(seg_dic, fileName, outFile):
    pd_dic = {'celltype': range(len(seg_dic.keys()))}
    y_vals = []
    for i in seg_dic:
        y_vals.append(seg_dic[i])
    pd_dic["Seg Counts"] = y_vals
    df = pd.DataFrame(pd_dic)
    y_labels = ["Seg Counts"]
    y_labels.append("celltype")
    df = df[y_labels]
    df.set_index(["celltype"],inplace=True)
    ax = df.plot(kind='bar',alpha=0.75, rot=0, title = "Document \"" + fileName + "\" annotations")
    ax.set_ylabel("#Segments")
    plt.xlabel("Line Number")
    #plt.yticks(np.arange(0, 1.1, 0.1))
    #plt.show()
    plt.savefig(outFile)
    
def process_annotations(anno_dir, resDir):
    for doc_dir in os.listdir(anno_dir):
        doc_full_dir = os.path.join(anno_dir, doc_dir)
        if doc_full_dir == resDir:
            continue
        seg_dic = init_seg_dic(doc_full_dir)
        for anno_file in os.listdir(doc_full_dir):
            seg_dic = segs_count(seg_dic, os.path.join(doc_full_dir, anno_file))
        plot_annotations(seg_dic, doc_dir, os.path.join(resDir, doc_dir + "_results.png"))
        
process_annotations("/home/pjdrm/workspace/TopicSegmentationScripts/human_annotations", "/home/pjdrm/workspace/TopicSegmentationScripts/human_annotations/results")