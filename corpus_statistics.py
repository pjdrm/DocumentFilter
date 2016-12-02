import nltk
import numpy as np
import os

def get_doc_type(file_path):
    file_name = file_path.split("/")[-1]
    if "_v" in file_name:
        return "video"
    
    return file_name.split("_")[-1][:-4]    

def get_doc_stats(file_path, stats_dic):
    doc_type = get_doc_type(file_path)
    with open(file_path, encoding="utf8", errors='ignore') as f:
        doc_str = f.read()
    doc_segs = doc_str.split("==========\n")[1:]
    doc_segs[-1] = doc_segs[-1].replace("\n==========", "")
    n_segs = len(doc_segs)
    stats_dic[doc_type]["n_segs"].append(n_segs)
    for seg in doc_segs:
        seg = seg
        n_sents = seg.count("\n") + 1
        words = nltk.word_tokenize(seg)
        n_words = len(words)
        stats_dic[doc_type]["n_sents"].append(n_sents)
        stats_dic[doc_type]["n_words"].append(n_words)
        stats_dic[doc_type]["vocab"] += words
        
def process_corpus_stats(stats_dic):
    str_stats = ""
    for doc_type in stats_dic:
        str_stats += doc_type + "\n"
        str_stats += "#Docs " + str(len(stats_dic[doc_type]["n_segs"])) + "\n"
        avg_segs = np.mean(stats_dic[doc_type]["n_segs"])
        std_segs = np.std(stats_dic[doc_type]["n_segs"])
        str_stats += "AVG Segments " + str(avg_segs) + " +- " + str(std_segs) + "\n"
        avg_sents = np.mean(stats_dic[doc_type]["n_sents"])
        std_sents = np.std(stats_dic[doc_type]["n_sents"])
        str_stats += "AVG Sents " + str(avg_sents) + " +- " + str(std_sents) + "\n"
        avg_words = np.mean(stats_dic[doc_type]["n_words"])
        std_words = np.std(stats_dic[doc_type]["n_words"])
        str_stats += "AVG Words " + str(avg_words) + " +- " + str(std_words) + "\n"
        str_stats += "|Vocab| " + str(len(set(stats_dic[doc_type]["vocab"]))) + "\n\n"
    print(str_stats)
    
def run(dirPath):
    stats_dic = {"video": {"n_segs": [], "n_sents": [], "n_words": [], "vocab": []},
                 "html": {"n_segs": [], "n_sents": [], "n_words": [], "vocab": []},
                 "pdf": {"n_segs": [], "n_sents": [], "n_words": [], "vocab": []},
                 "ppt": {"n_segs": [], "n_sents": [], "n_words": [], "vocab": []}}
    
    for dir in os.listdir(dirPath):
        for file_path in os.listdir(os.path.join(dirPath, dir)):
            get_doc_stats(os.path.join(dirPath, dir, file_path), stats_dic)
    process_corpus_stats(stats_dic)
    
run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted")
        
        
        
        
    
        
    
        
    