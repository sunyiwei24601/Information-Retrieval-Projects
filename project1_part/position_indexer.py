import json
import os
from file_merger import *
import collections 
import time
from test_time import *
def define_docs(documents):
    docs = list(documents.keys())
    doc_dict = {}
    n = 0
    for i in docs:
        doc_dict[i] = n 
        n += 1
    return doc_dict, docs 

def define_term(documents):
    terms = set()
    for document in documents:
        temp = []
        for i in document:
            if type(i) == list:
                temp += i
            elif i:
                temp.append(i)
        terms = terms.union(set(temp))
    term_list = sorted(list(terms))
    n = 0
    term_dict = {}
    for term in term_list:
        term_dict[term] = n
        n += 1
    return term_dict, term_list

def count_position_token(documents):
    cltns = collections.defaultdict(list)
    for i in range(len(documents)):
        tokens = documents[i]
        for token in tokens:
            cltns[token].append(i)
    return cltns 

def create_triple(collections, docid):
    triples = []
    for key,value in collections.items():
        if type(value) != list:
            value = [value]
        triples.append((key, docid, *value))
    return triples 

@test_time(show_time=True)
def position_term_indexer(documents, memory_limit, output_file):
    start = time.time()
    doc_dict, doc_list = define_docs(documents)
    term_dict, term_list = define_term(documents.values())
    count = 0
    triples_store = []
    file_path = os.path.join("position_term_index", "position_indexer")
    for docid, tokens in documents.items():
        collections = count_position_token(tokens)
        #transform term,doc into  id
        triples = create_triple(collections, doc_dict[docid]) # standard output termid, docid, frequence/positions
        triples = [(term_dict[triple[0]], *triple[1:])  for triple in triples]

        # if new triples exceed the limit, write the file
        count = len(triples_store) + len(triples)
        if count > memory_limit:
            triples_store = sorted(triples_store, key=lambda x: (int(x[0]), int(x[1])) )
            write_triples(triples_store, file_path)
            triples_store = triples
            count = len(triples)
            continue 
        else:
            triples_store += triples
        pass
    end = time.time()
    print("triples write down cost: ", end - start)
    final_file = merge_triple_files(file_path, write_triples.num)
    return translate_file(term_list, final_file, output_file, positions=True )

if __name__ == "__main__":
    documents = json.load(open("doc_tokenized.json"))
    position_term_indexer(documents, 10000)
    print(2333)
