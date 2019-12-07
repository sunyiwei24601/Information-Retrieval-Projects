import sys
import os
sys.path.append(os.getcwd())
from query_reader import *
from query import *
class Expander:
    def __init__(self, queries, loader):
        self.queries = {}
        for num, query in queries:
            self.queries[num] = query
        self.model = ExpandVSM(loader, self.queries)
        self.model.compute_idf()
        self.model.compute_document_normalization()
        

        
        
    def get_original_documents(self, index_directory_path=None, query_file_path=None):
        index_directory_path = "results"
        query_file_path = "queryfile.txt"
        lexicon_path = os.path.join(index_directory_path, "single.lexicon")
        index_path = os.path.join(index_directory_path, "single.index")
        document_path = os.path.join(index_directory_path, "document_list.csv")
        test = Test(query_file_path, lexicon_path, index_path, document_path, size=None)
        self.scores = test.run_Model("cosine")


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
         
    def Rocchio_Vector_Generate(self, query_num, query, alpha=1, beta=10, gama=1):

        query_posting = self.model.generate_query_posting_list(query)
        origin_query_vector, norm = self.model.from_query_posting_into_weight_vector(query_posting)
        rel_documents = self.get_n_documents(query_num, 10)
        non_rel_documents = self.get_n_documents(query_num, 5, top=False)
        rel_vector = self.combine_document_vector(rel_documents)
        non_rel_vector = self.combine_document_vector(non_rel_documents)

        all_terms = list(origin_query_vector.keys()) + list(rel_vector.keys())
        new_query_vector = {}
        for term_id in all_terms:
            new_query_vector[term_id] = alpha * origin_query_vector.get(term_id, 0)
            new_query_vector[term_id] += beta * rel_vector.get(term_id, 0)
            # new_query_vector[term_id] -= gama * non_rel_vector.get(term_id, 0)
        
        if len(new_query_vector) > 0:
            threshold_value = sorted(list(new_query_vector.values()))[-10]
        query_vector = {}
        for key in new_query_vector:
            if new_query_vector[key] >= threshold_value:
                query_vector[key] = new_query_vector[key]
            
        return query_vector
        
 


    def combine_document_vector(self, rel_documents):
        combine_vector = collections.defaultdict(lambda:0)
        len_ = len(rel_documents)
        for docid in rel_documents:
            document_vector = self.document_vector_list[docid]
            for term_id, w in document_vector.items():
                combine_vector[term_id] += w/len_
        
        return combine_vector
            
    
    def get_Rocchio_Vector_Results(self):
        self.get_original_documents()
        vsm = self.model 
        vsm.compute_idf()
        self.document_normalization = vsm.document_normalization
        self.term_list = vsm.term_list
        self.term_dict = vsm.term_dict
        self.document_list = vsm.document_list
        self.document_dict = vsm.document_dict
        self.document_posting_list = vsm.document_posting_list
        self.document_lenth = vsm.document_lenth
        self.document_frequency_list = vsm.document_frequency_list
        self.document_vector_list = vsm.document_vector_list
        new_queries = {}
        for query_num, query in self.queries.items():
            new_queries[query_num] = self.Rocchio_Vector_Generate(query_num, query)
        vsm.queries = new_queries
        cosine_score_path = os.path.join("query_results", "cosine_qe.txt")
        return vsm.run_query(cosine_score_path, 100)


         
        

class ExpandVSM(VectorSpaceModel):
    def __init__(self, loader, queries, stem=None):
        super().__init__(loader, queries, stem=stem)

    def get_COSINE_scores(self, query_num, query, size = 10):
        score = collections.defaultdict(lambda : 0)
        query_tf_idf_vector = query
        query_normalization = self.from_query_vector_into_normalization(query)
        
        for term_id, weight in query_tf_idf_vector.items():
            term_posting_list = self.term_posting_list[term_id]
            for doc_id, tf in term_posting_list.items():
                score[doc_id] += self.calculate_tf_idf(tf, self.idf_list[term_id]) * weight
        
        for doc_id in score:
            score[doc_id] /= math.sqrt(query_normalization * self.document_normalization[doc_id])
        score_list = sorted(score.items(), key=lambda x: x[1], reverse=True)
        s  = [[query_num, 0, self.document_list[score_list[n][0]], n, score_list[n][1], "COSINE"] for n in range(len(score_list[:size]))]
        return s

    def from_query_vector_into_normalization(self, query):
        norm = 0
        for i in query:
            norm += i**2
        return norm

    def run_query(self, cosine_score_path, size=10):
        self.compute_document_normalization()
        scores = []
        for query_num, query in self.queries.items():
            scores.append(self.get_COSINE_scores(query_num, query, size))
        self.output_result(scores, cosine_score_path)
        return scores



if __name__ == "__main__":
    lexicon_path = "results\single.lexicon"
    index_path = "results\single.index"
    document_path = "results\document_list.csv"
    loader = IndexLoader(index_path, lexicon_path, document_path).load_all()

    query_file_path = "queryfile.txt"
    reader = QueryReader(query_file_path)
    expander = Expander(reader.get_query(), loader)
    s = expander.get_Rocchio_Vector_Results()
    pass 