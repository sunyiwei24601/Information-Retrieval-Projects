import sys
import os
sys.path.append(os.getcwd())
from QueryModel import *
from index_loader import *

class QueryReducer():
    def __init__(self, loader, queries, stem=None):
        self.term_posting_list = loader.term_index
        self.term_frequency_collection = loader.term_frequency_collection
        self.term_list = loader.term_list
        self.term_dict = loader.term_dict
        self.document_list = loader.document_list
        self.document_dict = loader.document_dict
        self.document_posting_list = loader.document_posting_list
        self.document_lenth = loader.document_lenth
        self.collection_lenth = loader.collection_lenth
        self.document_frequency_list = loader.document_frequency_list
        self.queries = queries

        self.parser = term_parser(stemmer=stem) 


    def from_query_to_posting_list(self, query):
        tokens = self.parser.get_single_term_tokens(query.strip("\t"))
        query_posting_list = collections.defaultdict(lambda : 0)
        for token_list in tokens:
            for token in token_list:
                token_id = self.term_dict.get(token)
                if token_id:
                    query_posting_list[token_id] += 1
        
        return query_posting_list

    def compute_idf(self):
        self.idf_list = []
        N = self.collection_lenth
        for df in self.document_frequency_list:
            idf = math.log10(N/df)
            self.idf_list.append(idf)

    def get_reduced_query(self, threshold, filter):
        
        self.compute_idf()
        for query_num, query_title, narrative in self.queries:
            query = query_title + narrative 
            query_posting_list = self.from_query_to_posting_list(query)

            select_number = int(len(query_posting_list) * threshold)
            if filter == "qtf":
                sorted_term_list = sorted(query_posting_list.items(), key=lambda x:x[1], reverse=True)
                sorted_term_list = [i[0] for i in sorted_term_list]
            elif filter  == "idf":
                sorted_term_list = sorted([(term_id, self.idf_list[term_id]) for term_id in query_posting_list], key=lambda x:x[1], reverse=True)
                sorted_term_list = [i[0] for i in sorted_term_list]
            elif filter == "qtf*idf":
                l = [(term_id, self.idf_list[term_id] * frequency) for term_id, frequency in query_posting_list.items()]
                sorted_term_list = sorted(l, key= lambda x : x[1], reverse=True)
                sorted_term_list = [i[0] for i in sorted_term_list]
            new_query_posting_list = {key: query_posting_list[key] for key in sorted_term_list[:select_number]}


            new_query = ""
            for term, frequency in new_query_posting_list.items():
                if filter == "idf":
                    frequency = 1
                new_query += (self.term_list[term] + " ") * frequency
            yield query_num, new_query


if __name__ == "__main__":
    lexicon_path = "results\single.lexicon"
    index_path = "results\single.index"
    document_path = "results\document_list.csv"
    loader = IndexLoader(index_path, lexicon_path, document_path).load_all()


    query_file_path = "queryfile.txt"
    queries = QueryReader(query_file_path).get_query_with_narrative()

    reducer = QueryReducer(loader, queries)
    for i in reducer.get_reduced_query(0.4, "qtf*idf"):
        print(i)
