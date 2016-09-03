'''
Created on Aug 23, 2016

@author: root
'''
from gensim.corpora.mmcorpus import MmCorpus
from gensim.models import ldamodel as ldamodel
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import pyLDAvis
import pyLDAvis.gensim
from scipy.sparse.coo import coo_matrix
from sklearn import lda
from sklearn.decomposition.online_lda import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import string
import pyLDAvis.sklearn


stemmer = PorterStemmer()
def tokenize_and_stem(text):
    tokens = nltk.tokenize.word_tokenize(text)
    # strip out punctuation and make lowercase
    tokens = [token.lower().strip(string.punctuation)
              for token in tokens]

    # now stem the tokens
    tokens = [stemmer.stem(token) for token in tokens]

    return tokens

class MyDictionary(object):

    def __init__(self, word2id_dic):
        self.token2id = word2id_dic
        
    def __len__(self):
        """
        Return the number of token->id mappings in the dictionary.
        """
        return len(self.token2id)

def lda_analysis(docsDir, n_topics):
    docs = getSegments(docsDir)
    vectorizer = CountVectorizer(analyzer = "word", strip_accents = "unicode", stop_words = stopwords.words("english"), max_features = 500)
    wd_matrix = vectorizer.fit_transform(docs)
    
    '''
    lda_tf = LatentDirichletAllocation(n_topics=n_topics, random_state=0)
    lda_tf.fit(wd_matrix)
    pyLDAvis.enable_notebook()
    return lda_tf, wd_matrix, vectorizer
    '''
    
    wd_matrix_dense = wd_matrix.toarray()
    docs_sparse_gensim = []
    for i in range(wd_matrix_dense.shape[0]):
        doc_sparse_gensim = []
        for j in range(wd_matrix_dense.shape[1]):
            val = wd_matrix_dense[i, j]
            if not val == 0:
                doc_sparse_gensim.append((j, val))
        doc_sparse_gensim = sorted(doc_sparse_gensim, key=lambda tup: tup[0])
        docs_sparse_gensim.append(doc_sparse_gensim)
                
    id2word =  {v: k for k, v in vectorizer.vocabulary_.items()}
    lda = ldamodel.LdaModel(corpus=docs_sparse_gensim, id2word=id2word, num_topics=n_topics, update_every=1, chunksize=2, passes=100)
    return lda, docs_sparse_gensim, MyDictionary(vectorizer.vocabulary_)
    
    topics_str = lda.print_topics(n_topics, 6)
    for topic_str in topics_str:
        print(topic_str)
    
def getDocs(docsDir):
    docs = []
    docs_txt_Dir = docsDir.replace("docs_annoted", "docs_txt")
    for path in os.listdir(docsDir):
        current_docs_dir = docs_txt_Dir
        path = path.replace("_annotated", "")
        if "_v" in path:
            current_docs_dir += "/" + path.split("_")[1][1:]
            path = "cap_man_processed.txt"
        else:
            path = path[4:]
        with open(os.path.join(current_docs_dir, path)) as f:
            docs.append(f.read())
    return docs

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
            doc = f.readlines()
            doc = doc[1:-1]
            docs.append(' '.join(doc))
    return docs

lda, corpus, dic = lda_analysis("/home/pjdrm/Desktop/GoogleScraper/Segment_relation_annotation/L02", 15)
pyLDAvis.enable_notebook()
vis_data = pyLDAvis.gensim.prepare(lda, corpus, dic)
pyLDAvis.display(vis_data)   
        
        
