import time
import json
import os
import sys
import math
from file_merger import *
import collections 
from reader import *
from Parser import *
from test_time import *
from position_indexer import position_term_indexer
from analysis import *
from statistics import median, mean
import math

class Indexer:
    def __init__(self, documents, memory_limit, output_file):
        self.documents = documents
        self.memory_limit = memory_limit
        self.output_file = output_file
        self.doc_dict = {}
        self.doc_list = []
        
    def single_term_indexer(self, position=False):
        start = time.time()
        count = 0
        triples_store = []
        file_path = os.path.join("single_term_index", "single_indexer")
        doc_id = 0
        for docno, document in self.documents:
            self.doc_dict[docno] = doc_id
            self.doc_list.append(docno)
            if position:
                collections = self.count_position_token(document)
                #transform term,doc into  id
                triples = self.create_triple(collections, doc_id) # standard output termid, docid, frequence/positions
                triples = [[triple[0], triple[1], *triple[2] ] for triple in triples]
            else:
                collections = self.count_token(document)
                #transform term,doc into  id
                triples = self.create_triple(collections, doc_id) # standard output termid, docid, frequence/positions

            # if new triples exceed the limit, write the file
            count = len(triples_store) + len(triples)
            if count > self.memory_limit:
                triples_store = sorted(triples_store, key=lambda x: (x[0], x[1]) )
                write_triples(triples_store, file_path)
                triples_store = triples
                count = len(triples)
                doc_id += 1
                continue 
            else:
                triples_store += triples
            doc_id += 1
        triples_store = sorted(triples_store, key=lambda x: (x[0], x[1]) )
        write_triples(triples_store, file_path)
        end = time.time()
        self.triple_write_time = end - start
        print("triples write down cost ", self.triple_write_time)
        merge_start = time.time()
        merge_result_file = merge_triple_files(file_path, write_triples.num)
        self.merge_time = time.time() - merge_start

        return merge_result_file

    def count_token(self, document):
        collections = {}
        for tokens in document:
            for token in tokens:
                if token in collections:
                    collections[token] += 1
                else:
                    collections[token] = 1
        return collections 

    def create_triple(self, collections, docid):
        triples = []
        for key,value in collections.items():
            triples.append((key, docid, value))
        return triples 

    def count_position_token(self, document):
        cltns = collections.defaultdict(list)
        for i in range(len(document)):
            tokens = document[i]
            for token in tokens:
                cltns[token].append(i)
        return cltns 
    
if __name__ == "__main__":
    parameters = sys.argv
    # directory_path = parameters[1] 
    # index_type = parameters[2]
    # output_dir = parameters[3]
    
    directory_path = os.path.join(".","BigSample") 
    index_type = "positional"
    output_dir = os.path.join(".", "results")
    output_file = os.path.join(output_dir, index_type + ".index")
    memory_limit = int(parameters[1])
    



    




    

