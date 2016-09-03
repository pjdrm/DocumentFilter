'''
Created on Aug 29, 2016

@author: Pedro Mota
'''
import os
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np
import pandas as pd

def get_jacob_group_results(results_dir):
    def get_order(fileName):
        return int(fileName.split("_g")[1].replace(".txt", ""))
    
    results = []
    for dir in sorted(os.listdir(results_dir), key=get_order):
        with open(os.path.join(results_dir, dir)) as f:
            lins = f.readlines()
            for lin in lins:
                if lin.startswith("doc "):
                    results.append(float(lin.split("wd ")[1][:-1].replace(",", ".")))
    return results
    
def get_group_results(results_dir):
    results = []
    groupDirs = [x for x in os.listdir(results_dir) if x.startswith("group")]
    
    def get_order(dir):
        return int(dir.replace("group", ""))
    
    groupDirs = sorted(groupDirs, key=get_order)
    for dir in groupDirs:
        if dir.startswith("group"):
            res = process_dir(os.path.join(results_dir, dir))
            results.append(res)
    return results

def get_doc_type_results(results_dir, target_dirs):
    results = []
    dir_types = []
    for dir in os.listdir(results_dir):
        if dir in target_dirs:
            res = process_dir(os.path.join(results_dir, dir))
            results.append(res)
            dir_types.append(dir)
    return results

def process_dir(group_dir):
    for file_name in os.listdir(group_dir):
        if file_name.startswith("ind_scores"):
            with open(os.path.join(group_dir, file_name)) as f:
                lines = f.readlines()
                for lin in lines:
                    if "docid=0" in lin:
                        wd = lin.split("wd=")[1].split(" ")[0]
                        return float(wd)
                    
def get_doc_pure_type_results(results_dir, target_dirs):
    results = []
    dir_types = []
    for dir in target_dirs:
        res = process_dir_pure_type(os.path.join(results_dir, dir))
        results.append(res)
        dir_types.append(dir)
    return results

def process_dir_pure_type(group_dir):
    wd_total = 0.0
    n = 0.0
    for file_name in os.listdir(group_dir):
        if file_name.startswith("ind_scores"):
            with open(os.path.join(group_dir, file_name)) as f:
                lines = f.readlines()
                for lin in lines:
                    if lin.startswith("docName"):
                        wd_total += float(lin.split("wd=")[1].split(" ")[0])
                        n += 1.0
            return wd_total / n
        
def get_doc_type(docs_dir, file_path):
    with open(file_path, encoding="utf8", errors="ignore") as f:
            txt = f.read()
            txt = txt.replace("===== 0\n", "").replace("=====\n", "").replace("=====", "")
    
    for file in os.listdir(docs_dir):
        with open(os.path.join(docs_dir, file), encoding="utf8", errors="ignore") as f1:
            file_txt = f1.read()
            file_txt = file_txt.replace("==========\n", "").replace("==========", "")
            if txt == file_txt:
                if "_v" in file:
                    return "video"
                else:
                    with open(os.path.join(docs_dir.replace("_annoted", "_txt"), file[4:].replace("_processed_annotated", ""))) as f2:
                        f2.readline()
                        return f2.readline()[1:-1]
    #Assuming that ref doc was given
    return "video"
                    
def get_doc_type_dic(docs_txt, docs_dir):
    dic = {}
    dic["html"] = []
    dic["ppt"] = []
    dic["pdf"] = []
    dic["video"] = []
    for filePath in os.listdir(docs_dir):
        if filePath == "000.topicWord" or filePath == "ind_scores.txt.0":
            continue
        doc_type = get_doc_type(docs_txt, os.path.join(docs_dir, filePath))
        dic[doc_type].append(filePath)
    return dic

def get_by_type_results_alldocs(ind_score_file_path, doc_type_dic, type_order):
    doc_results_dic = {}
    with open(ind_score_file_path) as f:
        lins = f.readlines()[:-1]
        for lin in lins:
            split_lin = lin.split(" ")
            doc_id = split_lin[1].split("docid=")[1]
            wd = float(split_lin[8].split("wd=")[1])
            doc_results_dic["000."+doc_id] = wd
    
    grouped_results = []
    for type in type_order:
        wd_total = 0.0
        n = 0.0
        for doc_id in doc_type_dic[type]:
            wd_total += doc_results_dic[doc_id]
            n += 1.0
        wd_avg = wd_total / n
        grouped_results.append(wd_avg)
    return grouped_results
    
def get_by_type_results_jacob_baseline(resultsFilePath, docs_txt_dir, type_order):
    results_dic = {}
    with open(resultsFilePath) as f:
        lins = f.readlines()
        for lin in lins:
            if lin.startswith("doc "):
                str_split = lin.split(" ")
                doc_name = str_split[1][:-1]
                wd = float(str_split[-1].strip().replace(",", "."))
                results_dic[doc_name] = wd
                
    type_dic = {}
    type_dic["video"] = []
    type_dic["html"] = []
    type_dic["ppt"] = []
    type_dic["pdf"] = []
    for doc_name in results_dic:
        if "_v" in doc_name or doc_name.endswith(".ref"):
            type_dic["video"].append(doc_name)
        else:
            with open(os.path.join(docs_txt_dir, doc_name.replace("_processed_annotated", "")[4:])) as f:
                f.readline()
                type = f.readline()[1:-1]
                type_dic[type].append(doc_name)
    results_by_type = []
    for type in type_order:
        wd_avg = 0.0
        n = 0.0
        for doc_name in type_dic[type]:
            wd_avg += results_dic[doc_name]
            n += 1.0
        results_by_type.append(wd_avg/n)
    return results_by_type

def get_by_type_results_jacob_mine(resultsDir, type_order):
    results_dic = {}
    results_dic["video"] = []
    results_dic["html"] = []
    results_dic["pdf"] = []
    results_dic["ppt"] = []
    
    for file_path in os.listdir(resultsDir):
        if file_path.startswith("jacob_pure"):
            wd_total = 0.0
            n = 0.0
            type = file_path.replace("jacob_pure_", "").replace(".txt", "")
            with open(os.path.join(resultsDir, file_path)) as f:
                lins = f.readlines()
                for lin in lins:
                    if lin.startswith("doc "):
                        wd_total += float(lin.split(" ")[-1][:-1].replace(",", "."))
                        n += 1.0
            results_dic[type] = wd_total / n
            
    results = []
    for type in type_order:
        results.append(results_dic[type])
    return results  
           
def plot_group_results(results_list, labels, outFile, title):
    fig = plt.figure()
    for result, label in zip(results_list, labels):
        x = range(len(result))
        y = result
        plt.plot(x, y, label=label)
    plt.ylabel('WD')
    plt.xlabel('#Docs')
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.legend()
    fig.suptitle(title)
    plt.savefig(outFile)
    plt.show(outFile)
    
def plot_doc_types_results(y_results, y_labels, x_labels, title, outFile):
    pd_dic = {'celltype':x_labels}
    for y_vals, y_label in zip(y_results, y_labels):
        pd_dic[y_label] = y_vals
    df = pd.DataFrame(pd_dic)
    y_labels.append("celltype")
    df = df[y_labels]
    df.set_index(["celltype"],inplace=True)
    ax = df.plot(kind='bar',alpha=0.75, rot=0, title = title)
    ax.set_ylabel("AVG WD")
    plt.xlabel("Doc type")
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.savefig(outFile)
    plt.show()
                    
def run(results_dir_minwoo, results_dir_jacob, outGroup, base_line):
    results_minwoo = get_group_results(results_dir_minwoo)
    results_jacob = get_jacob_group_results(results_dir_jacob)
    labels = ["MinWoo", "MD-BayesSeg", "Baseline"]
    plot_group_results([results_minwoo, results_jacob, [base_line]*len(results_minwoo)], labels, outGroup, results_dir_minwoo.split("/")[-1])
    
def run_doc_types(results_dir, outDocTypes, base_line):
    target_dirs = ["html_docs", "video_docs", "ppt_docs", "pdf_docs"]
    results = get_doc_type_results(results_dir, target_dirs)
    plot_doc_types_results(results, target_dirs, base_line, results_dir.split("/")[-1], outDocTypes)
    
def run_doc_pure_types(results_dir, all_results_dir, docs_annotated_dir, outDocTypes, resultsFilePath, jacabo_mine_results, jacabo_mine_results_alldocs):
    target_dirs = ["pure_html_docs", "pure_video_docs", "pure_ppt_docs", "pure_pdf_docs"]
    results = get_doc_pure_type_results(results_dir, target_dirs)
    
    x_labels = ["html", "video", "ppt", "pdf"]
    doc_type_dic = get_doc_type_dic(docs_annotated_dir, all_results_dir)
    all_results = get_by_type_results_alldocs(os.path.join(all_results_dir, "ind_scores.txt.0"), doc_type_dic, x_labels)
    results_jacob_mine = get_by_type_results_jacob_mine(jacabo_mine_results, x_labels)
    results_jacob_mine_alldocs = get_by_type_results_jacob_baseline(jacabo_mine_results_alldocs, docs_annotated_dir.replace("annoted", "txt"), x_labels)
    base_line_results = get_by_type_results_jacob_baseline(resultsFilePath, docs_annotated_dir.replace("annoted", "txt"), x_labels)
    
    plot_doc_types_results([base_line_results, results, all_results, results_jacob_mine, results_jacob_mine_alldocs], ["Baseline", "MinWoo: Same Type", "MinWoo: All Docs", "MD-Bayes: Same Type", "MD-Bayes: All Docs"], x_labels, results_dir.split("/")[-1], outDocTypes)
    
l02_baseline = 0.41
#run("/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02", "/home/pjdrm/workspace/DocumentFilter/results_jacob/L02", "/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02/plot_group_L02.png", l02_baseline)
#run_doc_types("/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02", "/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02/plot_doc_types.png", l02_baseline)

run_doc_pure_types("/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02", "/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02/group21/", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "/home/pjdrm/workspace/MinWooTopicSeg/results/physics_L02/plot_doc_pure_types.png", "/home/pjdrm/workspace/DocumentFilter/results_jacob_baseline.txt", "/home/pjdrm/workspace/DocumentFilter/results_jacob/L02", "/home/pjdrm/workspace/DocumentFilter/results_jacob/L02/jacob_mine_alldocs.txt")