import sys
import os
sys.path.append(os.getcwd())
from query_reader import *
from query import *

class General_Expander:
    def __init__(self, queries, loader, scores, stem=None):
        self.queries = queries
        self.loader = loader
        self.scores = scores

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
        self.parser = term_parser(stemmer=stem)
    
    def compute_idf(self):
        self.idf_list = []
        N = self.collection_lenth
        for df in self.document_frequency_list:
            idf = math.log10(N/df)
            self.idf_list.append(idf)
    
    def get_n_documents(self, query_num, n, top=True):
        scores = []
        for score_list in self.scores:
            if len(score_list) == 0 :
                continue
            if score_list[0][0] == query_num:
                if top:
                    scores = score_list[:n]
                else:
                    scores = score_list[-n:]
        document_name_list = [i[2] for i in scores]
        document_id_list = [self.document_dict[i] for i in document_name_list]
        return document_id_list

    def generate_query_posting_list(self, query):
        tokens = self.parser.get_single_term_tokens(query.strip("\t"))
        query_posting_list = collections.defaultdict(lambda : 0)
        for token_list in tokens:
            for token in token_list:
                token_id = self.term_dict.get(token)
                if token_id:
                    query_posting_list[token_id] += 1
        
        return query_posting_list

    def generate_expanded_queries(self, criteria, document_nums, term_nums):
        self.compute_idf()
        for query_num, query in self.queries:
            rel_documents = self.get_n_documents(query_num, document_nums)
        
            
            # original_query = self.generate_query_posting_list(query)
            if criteria == "dfidf": count_df = True 
            else: count_df = False
            combine_posting_list = self.combine_document_posting_list(rel_documents, count_df)
            # for term_id in original_query:
                # combine_posting_list[term_id] += original_query[term_id]
            term_scores = collections.defaultdict(lambda:0)
            for term_id, frequency in combine_posting_list.items():
                term_scores[term_id] += frequency * self.idf_list[term_id]

            sorted_term_list = sorted(term_scores.items(), key=lambda x:x[1], reverse=True)
            query = ""
            for i, j in sorted_term_list[:term_nums]:
                query += self.term_list[i] + " "
            yield query_num, query

    def combine_document_posting_list(self, document_list, count_df=True):
        combine_posting_list = collections.defaultdict(lambda :0)
        len_ = len(document_list)
        for doc_id in document_list:
            document_posting_list = self.document_posting_list[doc_id]
            for term_id, tf in document_posting_list.items():
                if count_df == True:
                    tf = 1
                combine_posting_list[term_id] += tf 
            
        return combine_posting_list

if __name__ == "__main__":
    index_directory_path = "results"
    query_file_path = "queryfile.txt"
    retrieval_model = "cosine"
    index_type = "single"
    results_file = "query_results" + os.path.sep + "cosine_single_reduce_qf_idf.txt"

    if index_type == "stem":
        lexicon_path = os.path.join(index_directory_path,"stem.lexicon")
        index_path = os.path.join(index_directory_path, "stem.index")
        document_path = os.path.join(index_directory_path, "document_list.csv")
    elif index_type == "single":
        lexicon_path = os.path.join(index_directory_path,"single.lexicon")
        index_path = os.path.join(index_directory_path, "single.index")
        document_path = os.path.join(index_directory_path, "document_list.csv")

    query_file_path = query_file_path
    reader = QueryReader(query_file_path)
    

    loader = IndexLoader(index_path, lexicon_path, document_path).load_all()
    test = Test(query_file_path, lexicon_path, index_path, document_path, size=100)
    # reduced_queries  = test.reduce_query(1, "qtf*idf")
    # test.run_Model(retrieval_model, times=1, output_path=results_file)

    scores = test.run_Model(retrieval_model, times=1, output_path=results_file)

    expander = General_Expander(queries, loader, scores)
    expanded_queries = list(expander.generate_expanded_queries("tfidf", 10, 10))

    scores = test.run_Model(retrieval_model, times=1, output_path=results_file, queries=expanded_queries)
    pass
    
