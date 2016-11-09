import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
plt.style.use('ggplot')

def getWordCountsDic(filePath, words_to_display):
    with open(filePath) as f:
        sents = f.readlines()
    tf_vectorizer = CountVectorizer(analyzer = "word", strip_accents = "unicode", stop_words = stopwords.words("english"), max_features = 500)
    dtm_tf = tf_vectorizer.fit_transform(sents)
    array_tf = dtm_tf.toarray()
    word_c_dic = {}
    for word in words_to_display:
        word_c_dic[word] = array_tf[:, tf_vectorizer.vocabulary_[word]]
    return word_c_dic

def getWordBar(word_counts):
    bar_len = 0
    flag = True
    word_bar = []
    for sent_count in word_counts:
        if sent_count == 0 and flag:
            word_bar.append(bar_len)
            flag = False
            bar_len = 0
            
        if sent_count > 0 and not flag:
            word_bar.append(bar_len)
            flag = True
            bar_len = 0
        bar_len += 1
    #if word_counts[0] == 0:
     #   word_bar = word_bar[:-1]
    word_bar.append(bar_len)
    return word_bar

def plot_word_repetions(word_counts_dic, words_to_disp):
    word_bars = []
    max_bar = 0
    for word in words_to_disp:
        word_bar = getWordBar(word_counts_dic[word])
        word_bars.append(word_bar)
        bar_len = len(word_bar)
        if bar_len > max_bar:
            max_bar = bar_len

    df = pd.DataFrame(word_bars)
    color_list = []
    color = '#348ABD'
    n_cols = len(word_bars[0])    
    for i in range(n_cols):
        color_list.append(color)
        if color == '#FFFFFF':
            color = '#348ABD'
        else:
            color = '#FFFFFF'
    
    ax = df.plot.barh(stacked=True, color=color_list, legend=False, width=0.4, xlim=[0, sum(word_bars[0])+1], edgecolor='#348ABD', linewidth='1')
    ax.set_yticklabels(map(str.title, words_to_disp))
    ax.yaxis.set_ticks_position('none')
    ax.grid(False)
    ax.patch.set_facecolor('#FFFFFF')
    ax.set_xlabel('Sentences', fontsize=20)
    ax.spines['bottom'].set_color('black')
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontweight('bold')
        tick.label1.set_fontsize(20)
        
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontweight('bold')
        tick.label1.set_fontsize(12)
    plt.show()
    
#word_counts_dic = {"Velocity": [1, 1, 1, 3, 0, 0, 0, 4, 6, 0, 1, 0], "Accelaration": [0, 0, 1, 3, 0, 0, 0, 4, 5, 3, 3, 3], "Direction": [1, 1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0], "Instant": [0, 0, 1, 3, 0, 0, 0, 4, 5, 3, 3, 3], "Average": [0, 0, 1, 3, 0, 0, 0, 4, 5, 3, 3, 3]}
#words_disp = ["Velocity", "Accelaration", "Instant", "Average", "Direction"]
#plot_word_repetions(word_counts_dic, words_disp)
words_disp = ["velocity", "acceleration", "instantaneous", "average"]
word_counts_dic = getWordCountsDic("word_repetition_plot/L02_vref.txt", words_disp)
plot_word_repetions(word_counts_dic, words_disp)