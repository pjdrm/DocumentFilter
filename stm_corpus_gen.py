from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
import os
import shutil

def run(docs_annotated_dir, outDir, stmDir):
    created_dirs = prepare_dirs(docs_annotated_dir, outDir)
    script = ""
    for dir in created_dirs:
        out = dir.replace(outDir+"/", "")
        print("generating corpora for %s" % (dir))
        os.makedirs(os.path.join(outDir, "out", out))
        stmResults = os.path.join("results", out)
        os.makedirs(os.path.join(stmDir, stmResults))
        gen_corpora(dir, os.path.join(outDir, "out", out))
        script += "./run data/" + out + " " + stmResults + " 1 10 1\n"
        
    with open("run_physics_exp.sh", "w+") as f:
        f.write(script)
    
    
def prepare_dirs(docs_annotated_dir, outDir):
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)
    os.makedirs(outDir)
    created_dirs = []
    for annotated_dir in os.listdir(docs_annotated_dir):
        created_dirs += make_individual_test_dirs(os.path.join(docs_annotated_dir, annotated_dir), os.path.join(outDir, annotated_dir))
        created_dirs += make_alldocs_test_dirs(os.path.join(docs_annotated_dir, annotated_dir), os.path.join(outDir, annotated_dir))
        created_dirs += make_media_test_dirs("html", os.path.join(docs_annotated_dir, annotated_dir), os.path.join(outDir, annotated_dir, "docs_html"))
        created_dirs += make_media_test_dirs("pdf", os.path.join(docs_annotated_dir, annotated_dir), os.path.join(outDir, annotated_dir, "docs_pdf"))
        created_dirs += make_media_test_dirs("ppt", os.path.join(docs_annotated_dir, annotated_dir), os.path.join(outDir, annotated_dir, "docs_ppt"))
        created_dirs += make_media_test_dirs("_v", os.path.join(docs_annotated_dir, annotated_dir), os.path.join(outDir, annotated_dir, "docs_video"))
    return created_dirs
    
def make_individual_test_dirs(docs_annotated_dir, outDir):
    created_dirs = []
    for doc_i, file in enumerate(os.listdir(docs_annotated_dir)):
        dest = os.path.join(outDir, "doc" + str(doc_i))
        os.makedirs(dest)
        shutil.copyfile(os.path.join(docs_annotated_dir, file), os.path.join(dest, file))
        created_dirs.append(dest)
    return created_dirs

def make_alldocs_test_dirs(docs_annotated_dir, outDir):
    dest = os.path.join(outDir, "docs_all")
    os.makedirs(dest)
    for doc_i, file in enumerate(os.listdir(docs_annotated_dir)):
        shutil.copyfile(os.path.join(docs_annotated_dir, file), os.path.join(dest, file))
    return [dest]

def make_media_test_dirs(doc_type, docs_annotated_dir, outDir):
    os.makedirs(outDir)
    flag = False
    for file in os.listdir(docs_annotated_dir):
        if doc_type in file:
            flag = True
            shutil.copyfile(os.path.join(docs_annotated_dir, file), os.path.join(outDir, file))
    if flag:
        return [outDir]
    else:
        shutil.rmtree(outDir)
        return []
     
def gen_corpora(corporaDir, outDir):
    gs_final = ""
    meta_final = ""
    all_sents = []
    docsNames = ""
    for filePath in os.listdir(corporaDir):
        docsNames += filePath.replace(".txt", "") + "\n"
        gs_str, meta_str, sents = get_data(os.path.join(corporaDir, filePath))
        gs_final += gs_str + "\n"
        meta_final += meta_str  + "\n"
        all_sents += sents
    corpus_txt, vocab_str = get_corpus(all_sents)
    
    with open(os.path.join(outDir, "gs.seg"), "w+") as gsFile:
            gsFile.write(gs_final[:-1])
            
    with open(os.path.join(outDir, "metadata.meta"), "w+") as metadataFile:
            metadataFile.write(meta_final[:-1])
            
    with open(os.path.join(outDir, "vocab.vocab"), "w+") as vocabFile:
        vocabFile.write(vocab_str[:-1])
        
    with open(os.path.join(outDir, "corpus.data"), "w+") as corpusFile:
        corpusFile.write(corpus_txt[:-1])
        
    with open(os.path.join(outDir, "docsNames.txt"), "w+") as corpusFile:
        corpusFile.write(docsNames[:-1])
    
def get_data(file_path):
    with open(file_path, encoding="utf8", errors='ignore') as f:
        lines = f.readlines()[1:]
        sents = []
        seg_gs = ""
        flag = True
        for lin in lines:
            if lin.startswith("=========="):
                seg_gs += "1,"
                flag = True
            else:
                sents.append(lin)
                if not flag:
                    seg_gs += "0,"
                else:
                    flag = False
                
        seg_gs = seg_gs[:-3]
        seg_gs += ",1"
        print("nSentsDocs %d nSentsGS %d" % (len(sents), len(seg_gs.split(","))))
        return seg_gs, str(len(sents)), sents
    
def get_corpus(sents):
    tf_vectorizer = CountVectorizer(analyzer = "word", strip_accents = "unicode", stop_words = stopwords.words("english"))
    dtm_tf = tf_vectorizer.fit_transform(sents)
    vocab = tf_vectorizer.vocabulary_
    inv_vocab = {v: k for k, v in vocab.items()}
    vocab_str = ""
    for id in inv_vocab:
        vocab_str += str(id) + "," + inv_vocab[id] + "\n"
            
    corpusTxt = ""
    for i in range(dtm_tf.shape[0]):
        for j in range(dtm_tf.shape[1]):
            corpusTxt += str(j) + ":" + str(dtm_tf[i, j])+","
        corpusTxt = corpusTxt[:-1]
        corpusTxt += "\n"
        
    return corpusTxt, vocab_str
    
def gen_corpus_files(file_path, outDir):
    with open(file_path) as f:
        lines = f.readlines()[1:]
        sents = []
        seg_gs = ""
        flag = True
        for lin in lines:
            if lin.startswith("=========="):
                seg_gs += "1,"
                flag = True
            else:
                sents.append(lin)
                if not flag:
                    seg_gs += "0,"
                else:
                    flag = False
                
        seg_gs = seg_gs[:-3]
        seg_gs += ",1"
        print("nSentsDocs %d nSentsGS %d" % (len(sents), len(seg_gs.split(","))))
        with open("gs.seg", "w+") as gsFile:
            gsFile.write(seg_gs)
            
        with open(join(outDir, "metadata.meta"), "w+") as metadataFile:
            metadataFile.write(str(len(sents)))
        tf_vectorizer = CountVectorizer(analyzer = "word", strip_accents = "unicode", stop_words = stopwords.words("english"))
        dtm_tf = tf_vectorizer.fit_transform(sents)
        vocab = tf_vectorizer.vocabulary_
        inv_vocab = {v: k for k, v in vocab.items()}
        with open(join(outDir, "vocab.vocab"), "w+") as vocabFile:
            for id in inv_vocab:
                vocabFile.write(str(id) + "," + inv_vocab[id] + "\n")
                
        corpusTxt = ""
        for i in range(dtm_tf.shape[0]):
            for j in range(dtm_tf.shape[1]):
                corpusTxt += str(j) + ":" + str(dtm_tf[i, j])+","
            corpusTxt = corpusTxt[:-1]
            corpusTxt += "\n"
        with open(join(outDir, "corpus.data"), "w+") as corpusFile:
            corpusFile.write(corpusTxt)
            
#gen_corpus("L02.txt")
'''
gen_corpora("landu_corpora/doc1", "landu_corpora/out/doc1")
gen_corpora("landu_corpora/doc2", "landu_corpora/out/doc2")
gen_corpora("landu_corpora/doc3", "landu_corpora/out/doc3")
gen_corpora("landu_corpora/doc4", "landu_corpora/out/doc4")
gen_corpora("landu_corpora/doc5", "landu_corpora/out/doc5")
gen_corpora("landu_corpora/doc6", "landu_corpora/out/doc6")
gen_corpora("landu_corpora/doc7", "landu_corpora/out/doc7")
gen_corpora("landu_corpora/doc8", "landu_corpora/out/doc8")
gen_corpora("landu_corpora/docs_all", "landu_corpora/out/docs_all")
'''
            
run("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted", "landu_corpora", "/home/pjdrm/workspace/LanDuSegmentation")
