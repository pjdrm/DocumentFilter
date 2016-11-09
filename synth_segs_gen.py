'''
Created on Aug 23, 2016

@author: root
'''
import numpy as np
import os
import shutil

def gen_seg(lms, topic_props, doc_len, sent_len, vocab_dic):
    topic_prop_draws = np.random.multinomial(doc_len, topic_props)
    doc_txt = ""
    word_count = 0
    for i in range(len(topic_prop_draws)):
        for draw in range(topic_prop_draws[i]):
            word_draw = get_word_index(np.random.multinomial(1, lms[i]))
            doc_txt += vocab_dic[word_draw]
            word_count += 1
            if word_count % sent_len == 0:
                doc_txt += "\n"
            else:
                doc_txt += " "
    return doc_txt
            
def get_word_index(multinomial_draw):
    return np.nonzero(multinomial_draw)[0][0]

def save_doc(doc, outFP):
    doc = "==========\n" + doc + "=========="
    with open(outFP, "w+") as f:
        f.write(doc)
    

def run(outDir):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)
             
    vocab_dic = {0: "g1", 1: "g2", 2: "b1", 3: "b2",  4: "c1", 5: "c2"}
    topic_props_d1 = [0.445, 0.545, 0.01]
    topic_props_d2 = [0.445, 0.01, 0.545]
    n_docs_each = 500
    lms = [[0.45, 0.45, 0.025, 0.025, 0.025, 0.025], [0.025, 0.025, 0.45, 0.45, 0.025, 0.025], [0.025, 0.025, 0.025, 0.025, 0.45, 0.45]]
    doc_len = 1000
    sent_len = 20
    doc_i = 0
    for i in range(n_docs_each):
        doc = gen_seg(lms, topic_props_d1, doc_len, sent_len, vocab_dic)
        save_doc(doc, os.path.join(outDir, "d1_" + str(doc_i) + ".txt"))
        
        doc = gen_seg(lms, topic_props_d2, doc_len, sent_len, vocab_dic)
        save_doc(doc, os.path.join(outDir, "d2_" + str(doc_i) + ".txt"))
        doc_i += 1
    print(doc)
    
run("syn_segs")