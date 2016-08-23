'''
Created on Aug 18, 2016

@author: Pedro Mota
'''
from collections import Counter
from nltk.corpus import stopwords
import os
from sklearn.cluster.k_means_ import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics.classification import precision_score
from statistics import mean

import matplotlib.pyplot as plt


def get_files_to_filter(root_dir_path):
    files_list = []
    for path, dirs, files in os.walk(root_dir_path):
            for f in files:
                if f.startswith("cap_asr"):
                    continue
                if f.endswith("processed.txt"):
                    files_list.append(os.path.join(path, f))
    return files_list

def get_docs(docs_path):
    docs = []
    for doc_path in docs_path:
        docs.append(get_text(doc_path))
    return docs

def get_text(doc_path):
    with open(doc_path, encoding="utf8") as f:
        doc_txt = f.read()
        return doc_txt
    
def filter_docs_rank(docs_text, docs_path, urls_ranks_dir, cut_off):
    rank_dic = getRankDic(urls_ranks_dir)
    labels = []
    counter = 0
    for doc_path in docs_path:
        url = get_url(doc_path)[:-1]
        if url in rank_dic:
            if rank_dic[url] <= cut_off:
                labels.append(1)
            else:
                labels.append(0)
        else:
            counter += 1
            labels.append(0)
    print("Could not find url rank for %d / %d of the docs" % (counter, len(docs_text)))
    return labels
    
def getRankDic(urls_ranks_dir):
    rank_dic = {}
    with open(urls_ranks_dir) as urls_ranks_f:
        for lin in urls_ranks_f.readlines():
            lin = lin[:-1]
            spliLin = lin.split(" ")
            url = spliLin[0]
            rank = int(spliLin[2])
            if url in rank_dic:
                if rank_dic[url] < rank:
                    rank_dic[url] = rank
            else:
                rank_dic[url] = rank
    return rank_dic
    
def filter_docs(docs_text, docs_path):
    vectorizer = TfidfVectorizer(analyzer = "word", strip_accents = "unicode", stop_words = stopwords.words("english"), max_features = 5000)
    wd_matrix = vectorizer.fit_transform(docs_text)
    km = KMeans(n_clusters=2, init='k-means++',n_init=1, verbose=1)
    km.fit(wd_matrix)
    labels = km.labels_
    l0_files = []
    l1_files = []
    for i, l in enumerate(labels):
        url = get_url(docs_path[i])
        if l == 0:
            l0_files.append(url)
        else:
            l1_files.append(url)
    res = "L0 files\n"
    for f in l0_files:
        res += f
    
    res += "L1 files\n" 
    for f in l1_files:
        res += f
        
    with open("results.txt", "w+") as f:
        f.write(res)
    return km.labels_

def filter_k_clusters(docs_text, docs_path, oo_file_path, k_range, n_runs):
    vectorizer = TfidfVectorizer(analyzer = "word", strip_accents = "unicode", stop_words = stopwords.words("english"), max_features = 5000)
    wd_matrix = vectorizer.fit_transform(docs_text)
    true_labels = get_true_labels(docs_path, oo_file_path)
    precisions = []
    n_docs = []
    for k in range(2, k_range+1):
        current_pr = []
        curren_n_docs = []
        for i in range(n_runs):
            km = KMeans(n_clusters=k, init='k-means++',n_init=1, verbose=1)
            km.fit(wd_matrix)
            pred_labels = km.labels_
            cnt = Counter(pred_labels)
            l1 = cnt.most_common(1)[0][0]
            for i in range(len(pred_labels)):
                if pred_labels[i] == l1:
                    pred_labels[i] = 1
                else:
                    pred_labels[i] = 0
            precision = precision_score(true_labels, pred_labels)
            current_pr.append(precision)
            curren_n_docs.append(cnt.most_common(1)[0][1])
            
        precisions.append(mean(current_pr))
        n_docs.append(mean(curren_n_docs))
    f, axarr = plt.subplots(2, squeeze=False)
    x = range(2, k_range+1)
    axarr[0, 0].plot(x, precisions)
    axarr[0, 0].set_ylabel("Precision")
    axarr[1, 0].plot(x, n_docs)
    axarr[1, 0].set_ylabel("#Docs")
    plt.show()
            
    target_names = ['L0', 'L1']
    print(classification_report(true_labels, pred_labels, target_names=target_names))
    
def filter_2lvl_docs(docs_text, docs_path):
    lvl1_labels = list(filter_docs(docs_text, docs_path))
    lvl2_filter_text = []
    lvl2_filter_path = []
    filtered_docs = []
    target_label = 0 if lvl1_labels.count(0) > lvl1_labels.count(1) else 1
    for doc, doc_path, lvl1_label in zip(docs_text, docs_path, lvl1_labels):
        if lvl1_label == target_label:
            lvl2_filter_text.append(doc)
            lvl2_filter_path.append(doc_path)
        else:
            filtered_docs.append(doc_path)
    #filter_docs(lvl2_filter_text, lvl2_filter_path)
    return lvl2_filter_text, lvl2_filter_path, filtered_docs

def filter_lvl_n_docs(docs_text, docs_path, n_lvls, oo_file_path):
    in_docs_urls = []
    all_docs_path = list(docs_path)
    for i in range(n_lvls):
        if len(docs_text) < 2:
            break
        docs_text, docs_path, filtered_docs = filter_2lvl_docs(docs_text, docs_path)
        for d in filtered_docs:
            in_docs_urls.append(get_url(d))
        
    pred_labels = []
    all_urls = []
    for doc_path in all_docs_path:
        url = get_url(doc_path)
        all_urls.append(url)
        if url in in_docs_urls:
            pred_labels.append(1)
        else:
            pred_labels.append(0)
            
    true_labels = get_true_labels(all_docs_path, oo_file_path)
    target_names = ['L0', 'L1']
    #print(classification_report(true_labels, pred_labels, target_names=target_names))
    
    precision = precision_score(true_labels, pred_labels)
    return precision, len(in_docs_urls)
    
def test_filter_lvls(docs_text, docs_path, n_lvls, oo_file_path, n_runs):
    precisions = []
    n_docs = []
    for lvls in range(1, n_lvls + 1):
        current_run_pr = []
        current_run_n_in = []
        for i in range(n_runs):
            pr, n_in_domains = filter_lvl_n_docs(docs_text, docs_path, lvls, oo_file_path)
            current_run_pr.append(pr)
            current_run_n_in.append(n_in_domains)
        precisions.append(mean(current_run_pr))
        n_docs.append(mean(current_run_n_in))
    f, axarr = plt.subplots(2, squeeze=False)
    x = range(n_lvls)
    axarr[0, 0].plot(x, precisions)
    axarr[0, 0].set_ylabel("Precision")
    axarr[1, 0].plot(x, n_docs)
    axarr[1, 0].set_ylabel("#Docs")
    #plt.ylabel('Precision')
    #plt.xlabel('Level')
    plt.show()
        
def get_url(doc_path):
    doc_path = doc_path.replace("_processed", "")
    with open(doc_path) as f:
        return f.readline()
    
def get_true_labels(docs_path, oo_file_path):
    true_labels = []
    with open(oo_file_path) as f:
        oo_urls = f.readlines()
    for doc_path in docs_path:
        url = get_url(doc_path)
        if url in oo_urls:
            true_labels.append(0)
        else:
            true_labels.append(1)
    return true_labels
        
docs_path = get_files_to_filter("/home/pjdrm/Desktop/GoogleScraper/docs_txt/L02")
docs_text = get_docs(docs_path)

#test_filter_lvls(docs_text, docs_path, 8, "out_of_domain_urls.txt", 100)
#filter_k_clusters(docs_text, docs_path, "out_of_domain_urls.txt", 6, 100)
filter_docs_rank(docs_text, docs_path, "/home/pjdrm/workspace/GoogleScraper/docs_urls_ranks/L02.urls.ranks.txt", 100)
print("done")
    
