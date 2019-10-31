import math
from index_loader import *
import csv
from query_reader import *
import sys 
import collections
sys.path.append("project1_part")
from project1_part.Parser import *

class QueryModel:
    
    def __init__(self, loader, queries):
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

        self.parser = term_parser()
     
    def compute_idf(self):
        self.idf_list = []
        N = self.collection_lenth
        for df in self.document_frequency_list:
            idf = math.log10(N/df)
            self.idf_list.append(idf)

    def generate_query_posting_list(self, query):
        tokens = self.parser.get_single_term_tokens(query)
        query_posting_list = collections.defaultdict(lambda : 0)
        for token_list in tokens:
            for token in token_list:
                token_id = self.term_dict.get(token)
                if token_id:
                    query_posting_list[token_id] += 1
        
        return query_posting_list

    def output_result(self, score_lists, score_path):
        with open(score_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=" ")
            for score_list in score_lists:
                for score in score_list:
                    writer.writerow(score)


class VectorSpaceModel(QueryModel):
    def __init__(self, loader, queries):
        super(VectorSpaceModel,self).__init__(loader, queries)

    def get_COSINE_scores(self, size = 10):
    
        for query_num, query in self.queries:
            score = collections.defaultdict(lambda : 0)
            query_posting = self.generate_query_posting_list(query)
            query_tf_idf_vector, query_normalization = self.from_query_posting_into_weight_vector(query_posting)
            for term_id, weight in query_tf_idf_vector.items():
                term_posting_list = self.term_posting_list[term_id]
                for doc_id, tf in term_posting_list.items():
                    score[doc_id] += self.calculate_tf_idf(tf, self.idf_list[term_id]) * weight 
            for doc_id in score:
                score[doc_id] /= math.sqrt(query_normalization * self.document_normalization[doc_id])
            score_list = sorted(score.items(), key=lambda x: x[1], reverse=True)
            yield [[query_num, 0, self.document_list[score_list[n][0]], n, score_list[n][1], "COSINE"] for n in range(len(score_list[:size]))]
    
    def from_query_posting_into_weight_vector(self, query_posting):
        normalization = 0
        query_vector = {}
        for term_id, tf in query_posting.items():
            w = self.calculate_tf_idf(tf, self.idf_list[term_id])
            normalization += w ** 2
            query_vector[term_id] = w
        for term_id in query_vector:
            query_vector[term_id] /= normalization

        return query_vector, normalization
        
    def compute_document_normalization(self):
        """
        from document_posting_list read the term and tf in it
        calculate the tf-idf in it
        save the document sparse vector as following(sorted)
        """
        document_ids = sorted(self.document_posting_list.keys())

        self.document_normalization = []

        for document_id in document_ids:
            sum_normalization = 0
            posting_list = self.document_posting_list[document_id]
            term_ids = sorted(posting_list.keys())
            idf = self.idf_list[document_id]
            for term_id in term_ids:
                tf = posting_list[term_id]
                w = self.calculate_tf_idf(tf, idf)
                sum_normalization += w**2

            self.document_normalization.append(sum_normalization)

    def calculate_tf_idf(self, tf, idf):
        return (math.log10(tf) + 1.0) * idf

if __name__ == "__main__":   
    lexicon_path = "results\single.lexicon"
    index_path = "results\single.index"
    document_path = "results\document_list.csv"
    loader = IndexLoader(index_path, lexicon_path, document_path).load_all()

    query_file_path = "queryfile.txt"
    reader = QueryReader(query_file_path)

    VSM = VectorSpaceModel(loader,reader.get_query())
    VSM.compute_idf()
    VSM.compute_document_normalization()
    scores = VSM.get_COSINE_scores(100)
    cosine_score_path = os.path.join("query_results","COSINE_SCORE.txt")
    VSM.output_result(scores, cosine_score_path)
