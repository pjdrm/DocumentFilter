'''
Created on Aug 29, 2016

@author: Pedro Mota
'''
import os
import json
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np
import pandas as pd
import shutil

def run_mw_results(resultsDir):
    resDic = {}
    resDic["indv"] = spider_ind_results_mw(resultsDir)
    resDic["doc_type"] = spider_docType_results_mw(resultsDir)
    resDic["all"] = spider_allDocs_results_mw(resultsDir)
    return resDic

def run_jacob_results(resultsDir):
    resultsDic = {}
    for dir in os.listdir(resultsDir):
        resultsDic[dir] = {}
        res = get_jacob_result(os.path.join(resultsDir, dir, "results.txt"))
        resultsDic[dir] = {}
        for docName, wd in res:
            resultsDic[dir][docName] = wd
    return resultsDic

def get_jacob_result(filePath):
    results = []
    with open(filePath) as f:
        for lin in f.readlines():
            if not lin.startswith("docId"):
                continue
            strSplit = lin.split(" ")
            docName = strSplit[1]
            wd = float(strSplit[5])
            results.append((docName, wd))
    return results

def spider_ind_results_mw(resultsDir):
    resultsDic = {}
    for dir in os.listdir(resultsDir):
        resultsDic[dir] = {}
        for l_dir in os.listdir(os.path.join(resultsDir, dir)):
            #dir grouped by doc type have the _ char in the name
            if "_" in l_dir:
                continue
            res = get_mw_result(os.path.join(resultsDir, dir, l_dir, "ind_scores.txt.0"))[0]
            resultsDic[dir][res[0]] = res[1]
    return resultsDic

def spider_allDocs_results_mw(resultsDir):
    resultsDic = {}
    for dir in os.listdir(resultsDir):
        resultsDic[dir] = {}
        for l_dir in os.listdir(os.path.join(resultsDir, dir)):
            #dir grouped by doc type have the _ char in the name
            if "_all" in l_dir:
                results = get_mw_result(os.path.join(resultsDir, dir, l_dir, "ind_scores.txt.0"))
                for docName, wd in results:
                    resultsDic[dir][docName] = wd
                break
    return resultsDic

def spider_docType_results_mw(resultsDir):
    resultsDic = {}
    for dir in os.listdir(resultsDir):
        resultsDic[dir] = {}
        for l_dir in os.listdir(os.path.join(resultsDir, dir)):
            #dir grouped by doc type have the _ char in the name
            if not "_" in l_dir or "_all" in l_dir:
                continue
            resultsDic[dir][l_dir] = {}
            results = get_mw_result(os.path.join(resultsDir, dir, l_dir, "ind_scores.txt.0"))
            for docName, wd in results:
                resultsDic[dir][l_dir][docName] = wd
    return resultsDic
            
def get_mw_result(filePath):
    results = []
    with open(filePath) as f:
        for lin in f.readlines():
            if not lin.startswith("docName"):
                continue
            strSplit = lin.split(" ")
            docName = strSplit[0].replace("docName=", "")
            wd = float(strSplit[7].replace("wd=", ""))
            results.append((docName, wd))
    return results

def get_docType_wd_avg(resultsDic):
    total_wd = 0.0
    total_docs = 0.0
    for lect in resultsDic:
        for docType_results in resultsDic[lect]:
            for docName in resultsDic[lect][docType_results]:
                total_wd += resultsDic[lect][docType_results][docName]
                total_docs += 1.0
    return total_wd / total_docs

def get_specific_docType_wd_avg(resultsDic, docType):
    total_wd = 0.0
    total_docs = 0.0
    for lect in resultsDic:
        for docName in resultsDic[lect][docType]:
            wd = resultsDic[lect][docType][docName]
            total_wd += wd
            total_docs += 1.0
    return total_wd / total_docs

def get_allDocs_wd_avg(resultsDic):
    total_wd = 0.0
    total_docs = 0.0
    for lect in resultsDic:
        for docName in resultsDic[lect]:
            total_wd += resultsDic[lect][docName]
            total_docs += 1.0
    return total_wd / total_docs

def get_indv_wd_avg(resultsDic):
    return get_allDocs_wd_avg(resultsDic)

def get_lecture_wd_avg(resultsDic):
    wd_total = 0.0
    total = 0.0
    for doc in resultsDic:
        wd_total += resultsDic[doc]
        total += 1
    if total == 0.0:
        return 0.0
    return wd_total / total

def get_singleDocAlg_lecture_wd_avg(resultsDic, docType):
    wd_total = 0.0
    total = 0.0
    for doc in resultsDic:
        if docType in doc:
            wd_total += resultsDic[doc]
            total += 1
    if total == 0.0:
        return 0.0
    return wd_total / total

def get_ref_wd(resultsDic_lect):
    for docName in resultsDic_lect:
        if docName.endswith("ref.txt"):
            return resultsDic_lect[docName]
                
def run_general_resView(resultsDic, outDir):
    y_vals = []
    y_labels = []
    x_labels = ["indv", "doc_type", "all"]
    for segmentor in resultsDic:
        y_labels.append(segmentor)
        if "indv" in resultsDic[segmentor]:
            indv_wd_avg = get_indv_wd_avg(resultsDic[segmentor]["indv"])
            docType_wd_avg = get_docType_wd_avg(resultsDic[segmentor]["doc_type"])
            all_wd_avg = get_allDocs_wd_avg(resultsDic[segmentor]["all"])
            y_vals.append([indv_wd_avg, docType_wd_avg, all_wd_avg])
        else:
            wd_avg = get_indv_wd_avg(resultsDic[segmentor])
            y_vals.append([wd_avg, wd_avg, wd_avg])
            
    plot_doc_types_results(y_vals, y_labels, "AVG WindowDiff", x_labels, "", "", os.path.join(outDir, "results_exp1.png"))
    
def run_general_docType_resView(resultsDic, outDir):
    y_vals = []
    y_labels = []
    x_labels = ["indv", "video", "ppt", "html", "pdf", "all"]
    for segmentor in resultsDic:
        y_labels.append(segmentor)
        if "indv" in resultsDic[segmentor]:
            indv_wd_avg = get_indv_wd_avg(resultsDic[segmentor]["indv"])
            video_wd_avg = get_specific_docType_wd_avg(resultsDic[segmentor]["doc_type"], "docs_video")
            ppt_wd_avg = get_specific_docType_wd_avg(resultsDic[segmentor]["doc_type"], "docs_ppt")
            html_wd_avg = get_specific_docType_wd_avg(resultsDic[segmentor]["doc_type"], "docs_html")
            pdf_wd_avg = get_specific_docType_wd_avg(resultsDic[segmentor]["doc_type"], "docs_pdf")
            all_wd_avg = get_allDocs_wd_avg(resultsDic[segmentor]["all"])
            y_vals.append([indv_wd_avg, video_wd_avg, ppt_wd_avg, html_wd_avg, pdf_wd_avg, all_wd_avg])
        else:
            wd_avg = get_indv_wd_avg(resultsDic[segmentor])
            y_vals.append([wd_avg]*6)
            
    plot_doc_types_results(y_vals, y_labels, "AVG WindowDiff", x_labels, "", "", os.path.join(outDir, "results_exp1.png"))
    
def run_ref_lectures_resView(resultsDic, refDocType, outDir):
    segmentor = list(resultsDic.keys())[0]
    if "indv" in resultsDic[segmentor]:
        lectures = resultsDic[segmentor]["indv"].keys()
    else:
        lectures = resultsDic[segmentor].keys()
    
    for lect in lectures:
        y_vals = []
        y_labels = []
        x_labels = ["indv", "video", "all"]
        for segmentor in resultsDic:
            y_labels.append(segmentor)
            if "indv" in resultsDic[segmentor]:
                indv_wd_avg = get_ref_wd(resultsDic[segmentor]["indv"][lect])
                docType_wd_avg = get_ref_wd(resultsDic[segmentor]["doc_type"][lect][refDocType])
                all_wd_avg = get_ref_wd(resultsDic[segmentor]["all"][lect])
                y_vals.append([indv_wd_avg, docType_wd_avg, all_wd_avg])
            else:
                indv_wd_avg = get_ref_wd(resultsDic[segmentor][lect])
                y_vals.append([indv_wd_avg]*3)
        plot_doc_types_results(y_vals, y_labels, "WindowDiff", "", x_labels, lect + "Results", os.path.join(outDir, "results_exp_" + lect + ".png"))
        
def run_avg_lectures_resView(resultsDic, outDir):
    segmentor = list(resultsDic.keys())[0]
    if "indv" in resultsDic[segmentor]:
        lectures = resultsDic[segmentor]["indv"].keys()
    else:
        lectures = resultsDic[segmentor].keys()
    
    for lect in lectures:
        y_vals = []
        y_labels = []
        x_labels = ["html", "video", "ppt", "pdf"]
        for segmentor in resultsDic:
            if "indv" in resultsDic[segmentor]:
                baseResDic = resultsDic[segmentor]["doc_type"][lect]
                y_labels.append(segmentor + ": Same Type")
                video_wd_avg = get_lecture_wd_avg(baseResDic["docs_video"])
                ppt_wd_avg = get_lecture_wd_avg(baseResDic["docs_ppt"])
                html_wd_avg = get_lecture_wd_avg(baseResDic["docs_html"])
                pdf_wd_avg = get_lecture_wd_avg(baseResDic["docs_pdf"])
                y_vals.append([html_wd_avg, video_wd_avg, ppt_wd_avg, pdf_wd_avg])
                
                baseResDic = resultsDic[segmentor]["all"][lect]
                y_labels.append(segmentor + ": All Docs")
                video_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_v")
                ppt_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_ppt")
                html_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_html")
                pdf_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_pdf")
                y_vals.append([html_wd_avg, video_wd_avg, ppt_wd_avg, pdf_wd_avg])
            else:
                y_labels.append(segmentor)
                baseResDic = resultsDic[segmentor][lect]
                video_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_v")
                ppt_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_ppt")
                html_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_html")
                pdf_wd_avg = get_singleDocAlg_lecture_wd_avg(baseResDic, "_pdf")
                y_vals.append([html_wd_avg, video_wd_avg, ppt_wd_avg, pdf_wd_avg])
            
        plot_doc_types_results(y_vals, y_labels, "WindowDiff", x_labels, "", "All " + lect + " Docs Results", os.path.join(outDir, "results_exp_allDocs_" + lect + ".png"))
        
def run_ref_lectures_avg_resView(resultsDic, refDocType, outDir):
    segmentor = list(resultsDic.keys())[0]
    if "indv" in resultsDic[segmentor]:
        lectures = resultsDic[segmentor]["indv"].keys()
    else:
        lectures = resultsDic[segmentor].keys()
    
    y_vals = []
    y_labels = []
    x_labels = ["indv", "video", "all"]

    for segmentor in resultsDic:
        y_labels.append(segmentor)
        total = 0.0
        indv_wd_total = 0.0
        docType_wd_total = 0.0
        all_wd_total = 0.0
        for lect in lectures:
            total += 1.0
            if "indv" in resultsDic[segmentor]:
                indv_wd_total += get_ref_wd(resultsDic[segmentor]["indv"][lect])
                docType_wd_total += get_ref_wd(resultsDic[segmentor]["doc_type"][lect][refDocType])
                all_wd_total += get_ref_wd(resultsDic[segmentor]["all"][lect])
            else:
                indv_wd_total += get_ref_wd(resultsDic[segmentor][lect])
        if all_wd_total == 0:
            y_vals.append([indv_wd_total/total]*3)
        else:
            y_vals.append([indv_wd_total/total, docType_wd_total/total, all_wd_total/total])
    plot_doc_types_results(y_vals, y_labels, "AVG WindowDiff", x_labels, "", "All Reference Lectures Results", os.path.join(outDir, "results_exp_ref_avg.png"))
                
                    
def plot_doc_types_results(y_results, y_labels, y_axis_label, x_labels, x_axis_label, title, outFile):
    pd_dic = {'celltype':x_labels}
    for y_vals, y_label in zip(y_results, y_labels):
        pd_dic[y_label] = y_vals
    df = pd.DataFrame(pd_dic)
    y_labels.append("celltype")
    df = df[y_labels]
    df.set_index(["celltype"],inplace=True)
    ax = df.plot(kind='bar',alpha=0.75, rot=0, title = title)
    ax.set_ylabel(y_axis_label)
    plt.xlabel(x_axis_label)
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.savefig(outFile)
    #plt.show()
            
def run(mw_results, bayeseg_results, mincut_results):
    all_corpora_dir = "all_corpora_results"
    if os.path.isdir(all_corpora_dir):
        shutil.rmtree(all_corpora_dir)
    os.makedirs(all_corpora_dir)
    
    indv_lec_dir = "indv_lectures_results"
    if os.path.isdir(indv_lec_dir):
        shutil.rmtree(indv_lec_dir)
    os.makedirs(indv_lec_dir)
    
    resDic = {}
    resDic["Minwoo"] = run_mw_results(mw_results)
    resDic["Bayeseg"] = run_jacob_results(bayeseg_results)
    resDic["Mincut"] = run_jacob_results(mincut_results)
    #print(json.dumps(resDic["Jacob"], indent=4, sort_keys=True))
    run_general_resView(resDic, all_corpora_dir)
    run_general_docType_resView(resDic, all_corpora_dir)
    run_ref_lectures_avg_resView(resDic, "docs_video", all_corpora_dir)
    run_ref_lectures_resView(resDic, "docs_video", indv_lec_dir)
    run_avg_lectures_resView(resDic, indv_lec_dir)
    
def run2(mw_results):
    resDic = spider_allDocs_results_mw(mw_results)
    total_wd = 0.0
    n_docs = 0.0
    for domain in resDic:
        for doc in resDic[domain]:
            n_docs += 1.0
            total_wd += resDic[domain][doc]
            
    print("AVG WD: %f" % (total_wd /n_docs))
        
run("experiments/minwoo_results", "experiments/jacob_results/bayeseg", "experiments/jacob_results/mincut")
#run2("experiments/mw_news_results")