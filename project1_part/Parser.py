import json
import re
import string
import collections
from filter import *
from nltk.stem.porter import PorterStemmer
import time
import math
import matplotlib.pyplot  as plt
from reader import *
from tokenizer import *
from test_time import *
import os

# split the text by space and eliminate the punctuation
def split_text(text):
    lists = text.split(" ")
    l = [i for i in lists if len(i)>0]
    punc = list(string.punctuation)
    punc = list(""" !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ """)
    for i in ("$", "@", ".", "%", "-", "(", ")", "#", ",", "\\", '/'):
        punc.remove(i)
    punc_translate = str.maketrans({key: None for key in punc})
    # eliminate punctuation
    l = [i.translate(punc_translate) for i in l]
    return [i for i in l if len(i)>0]

# get stop words list
def get_stop_words(filepath):
    f = open(filepath)
    stop_words_lists = []
    l = f.readline()
    while(l):
        stop_words_lists.append(l.strip('\n'))
        l = f.readline()
    f.close()
    return stop_words_lists

    frequencies = list(collectors.values())
    total_num = sum(frequencies)
    counts = collections.defaultdict(lambda: 0)
    for frequency in frequencies:
        counts[frequency] += 1

    log_counts = collections.defaultdict(lambda: 0)
    for frequency in frequencies:
        log_counts[math.log2(frequency)] += 1
    # x = sorted(list(counts.keys()))
    # y = [counts[i] for i in x]
    # plt.scatter(x, y, marker='.' , c='k')
    # plt.show()

    x = log_counts.keys()
    y = [math.log2(i) for i in log_counts.values()]
    plt.scatter(x, y ,marker='.' , c='k')
    plt.show()

# convert single document into a list of phrases
def document_phrase_parser(document):
    res = []
    stop_words = get_stop_words("stops.txt")
    for i in range(len(document)):
        word = document[i].lower()
        
        word_match = re.match(r'^[a-zA-Z]+$', word)
        if word_match and word not in stop_words:
            res.append(word)
        else:
            res.append(None) 
    res = generate_phrase(res)
    return res

def generate_phrase(token_list):
    len_ = len(token_list)
    res = []
    if len_ < 2:
        return []
    for i in range(len_ - 2):
        word_1 = token_list[i]
        word_2 = token_list[i + 1]
        word_3 = token_list[i + 2]
        if not word_1:
            continue
        if word_1 and word_2:
            res.append([word_1 + ' ' + word_2])
        if word_1 and word_2 and word_3:
            res.append([' '.join([word_1, word_2, word_3])])
    if token_list[-2] and token_list[-1]:
        res.append([token_list[-2] + ' ' + token_list[-1]])
    return res

class term_parser:
    def __init__(self, skip_stop_words=True, stemmer=None):
        stop_words_path = os.path.join("project1_part","stops.txt")
        self.stop_words = get_stop_words(stop_words_path)
        self.skip_stop_words = skip_stop_words
        self.stemmer = stemmer
        self.counter = collections.defaultdict(lambda:0)
        self.collection = collections.defaultdict(list)

    def get_single_term_tokens(self, document):
        res = []
        text = split_text(document)
        for i in range( len(text)):
            token = None 
            filter_type = None
            word = text[i].lower()
            #double_word parser
            if i < len(text) - 1:
                word2 = text[i+1].lower()
                filter_type, token = double_filter(word, word2)
            months = ["january", "february", "march", "april", "may", "june",
                      "july", "august", "september", "october", "november", "december"]
            mons = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            if (word in (mons + months)) and (i < (len(text) - 3)): 
                word3 = text[i+2]
                token = date_tokenier(word, word2, word3)
                if token:
                    filter_type= "filter_date5"

            if filter_type == None:
                w = strip_word(word)
                # use regex to get token
                filter_type, token = regex_filtering(w) #output like filter, [token1, token2]

            # stop words skip
            if self.skip_stop_words:
                temp = []
                if token:
                    if self.stemmer:
                        temp = [self.stemmer.stem(t) for t in token if t not in self.stop_words]
                    else:
                        temp = [t for t in token if t not in self.stop_words]
                    if len(temp) > 0 :
                        res.append(temp)   
            elif token:
                res.append(token) 
            # collector
            if filter:
                self.collect(word+"  "+ str(token), filter)
            elif len(w) > 1:
                self.collect(word)
        return res
        
    def collect(self, word, filter="others"):
        self.collection[filter].append(word)

    def count(self, word):
        self.counter[word] += 1

    def get_phrase_term_tokens(self, document):
        document = split_text(document)
        phrase_list = document_phrase_parser(document)
        for phrase in phrase_list:
            self.count(phrase[0])
        return phrase_list

    def generate_documents(self, documents, parser_type="single"):
        for docno, document in documents:
            if parser_type == "single":
                yield docno, self.get_single_term_tokens(document)
            if parser_type == "phrase":
                yield docno, self.get_phrase_term_tokens(document)

if __name__ == "__main__":
    parser = term_parser(skip_stop_words=False)
    pass
    
    