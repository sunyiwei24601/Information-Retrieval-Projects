import math
from index_loader import *
import csv
import re
from query_reader import *
import sys, os
import collections
sys.path.append("project1_part")
from project1_part.Parser import *
from evaluate_tools import *

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

    def get_COSINE_scores(self, query_num, query, size = 10):
    
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
            return [[query_num, 0, self.document_list[score_list[n][0]], n, score_list[n][1], "COSINE"] for n in range(len(score_list[:size]))]
    
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
        calculate the tf-idf in it and sum up to get the normalization
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

    def run_query(self, cosine_score_path, size=10):
        self.compute_idf()
        self.compute_document_normalization()
        scores = []
        for query_num, query in self.queries:
            scores.append(self.get_COSINE_scores(query_num, query, size))
        self.output_result(scores, cosine_score_path)

class BM25(QueryModel):
    def __init__(self, loader, queries):
        super(BM25, self).__init__(loader, queries)
        self.avgdl = sum(self.document_frequency_list) / self.collection_lenth
        
    def compute_idf(self):
        self.idf_list = []
        N = self.collection_lenth
        for df in self.document_frequency_list:
            w = math.log10(((N - df) + 0.5) / (df + 0.5) )
            self.idf_list.append(w)

    def get_BM25_scores(self, query_num, query, size = 10):
        score = collections.defaultdict(lambda :0)
        query_posting = self.generate_query_posting_list(query)
        for term_id, qtf in query_posting.items():
            term_posting_list = self.term_posting_list[term_id]
            for doc_id, tf in term_posting_list.items():
                d_len = self.document_lenth[doc_id]
                w = self.idf_list[term_id]
                s = self.calculate_score(tf, w, d_len, qtf)
                score[doc_id] += s
        score_list = sorted(score.items(), key=lambda x: x[1], reverse=True)
        return [[query_num, 0, self.document_list[score_list[n][0]], n, score_list[n][1], "BM25"] for n in range(len(score_list[:size]))]

    def calculate_score(self, tf, w, d_len, qtf):
        avgdl = self.avgdl
        k1 = 1.2
        b = 0.75
        k2 = 1
        temp = (k1 + 1) * tf
        temp2 = tf + k1 * (1 - b + b * d_len / avgdl)
        temp3 = (k2 + 1) * qtf / (k2 + qtf)
        return w * temp / temp2 * temp3

    def run_query(self, bm25_score_path, size=10):
        self.compute_idf()
        scores = []
        for query_num, query in self.queries:

            scores.append(self.get_BM25_scores(query_num, query, size))
        self.output_result(scores, bm25_score_path)

class LanguageModel(QueryModel):
    def __init__(self, loader, queries, miu):
        super(LanguageModel, self).__init__(loader, queries)
        self.miu = sum(self.document_lenth)/ self.collection_lenth * miu

    def get_Dirichlet_scores(self, query_num, query, size=10):
        score = collections.defaultdict(lambda : 0)
        query_posting = self.generate_query_posting_list(query)
        for term_id, qtf in query_posting.items():
            term_posting_list = self.term_posting_list[term_id]
            for doc_id, tf in term_posting_list.items():
                d_len = self.document_lenth[doc_id]
                tfc = self.term_frequency_collection[term_id]
                s = self.calculate_Dirichlet(tf, tfc, d_len)
                score[doc_id] += s
        score_list = sorted(score.items(), key=lambda x: x[1], reverse=True)
        return [[query_num, 0, self.document_list[score_list[n][0]], n, score_list[n][1], "Dirichlet"] for n in range(len(score_list[:size]))]

    def calculate_Dirichlet(self, tf, tfc, d_len):
        miu = self.miu
        C = sum(self.document_lenth)
        temp1 = tf + miu * tfc / C
        temp2 = d_len + miu
        return math.log10(temp1/temp2)

    def run_query(self, dirichlet_score_path, size=10):
        scores = []
        for query_num, query in self.queries:
            scores.append(self.get_Dirichlet_scores(query_num, query, size))
        self.output_result(scores, dirichlet_score_path)

class PhraseQueryModel(QueryModel):
    def __init__(self, loader, queries, phrase_loader, single_model):
        super(PhraseQueryModel, self).__init__(loader, queries)
        self.phrase_term_posting_list = phrase_loader.term_index
        self.phrase_term_frequency_collection = phrase_loader.term_frequency_collection
        self.phrase_term_list = phrase_loader.term_list
        self.phrase_term_dict = phrase_loader.term_dict
        self.phrase_document_list = phrase_loader.document_list
        self.phrase_document_dict = phrase_loader.document_dict
        self.phrase_document_posting_list = phrase_loader.document_posting_list
        self.phrase_document_lenth = phrase_loader.document_lenth
        self.phrase_collection_lenth = phrase_loader.collection_lenth
        self.phrase_document_frequency_list = phrase_loader.document_frequency_list

        self.positional_term_dict = phrase_loader.positional_term_dict
        self.positional_term_list = phrase_loader.positional_term_list
        self.positional_term_posting_list = phrase_loader.positional_term_posting_list
        self.positional_document_frequency_list = phrase_loader.positional_document_frequency_list
        
        self.single_model = single_model
    
    def run_query(self, phrase_score_path, size=10):
        for query_num, query in self.queries:
            self.get_phrase_score(query_num, query, size)
    
    def compute_phrase_idf(self):
        self.phrase_idf_list = []
        N = self.collection_lenth
        for df in self.phrase_document_list:
            w = math.log10(((N - df) + 0.5) / (df + 0.5) )
            self.phrase_idf_list.append(w)

    def get_phrase_score(self, query_num, query, size=10):
        score = collections.defaultdict(lambda: 0)
        posting_list = self.generate_query_posting_list(query)
        for phrase, qtf in posting_list.items():
            if self.phrase_term_dict.get(phrase):
                phrase_term_id = self.phrase_term_dict[phrase]
                phrase_posting_list = self.phrase_term_posting_list[phrase_term_id]
                for doc_id, tf in phrase_posting_list.items():
                    d_len = self.document_lenth[doc_id]
                    w = self.phrase_idf_list[phrase_term_id]
                    s = self.calculate_score(tf, w, d_len, qtf)
                    score[doc_id] += s 
            else:
                phrase_posting_list = self.get_positional_posting_list(phrase.split(" "))
                df = len(phrase_posting_list)
                N = self.collection_lenth
                for doc_id, tf in phrase_posting_list.items():
                    d_len = self.document_lenth[doc_id]
                    w = math.log10(((N - df) + 0.5) / (df + 0.5))
                    s = self.calculate(tf,w, d_len. qtf)
                    score[doc_id] += s
        score_list = sorted(score.items(), key=lambda x:x[1], reverse=True)
        return [[query_num, 0, self.document_list[score_list[n][0]], n, score_list[n][1], "phrase_index"] for n in range(len(score_list[:size]))]

    def calculate_idf(self, posting_list):
        pass
    
    def calculate_score(self, tf, w, d_len, qtf):
        avgdl = self.avgdl
        k1 = 1.2
        b = 0.75
        k2 = 1
        temp = (k1 + 1) * tf
        temp2 = tf + k1 * (1 - b + b * d_len / avgdl)
        temp3 = (k2 + 1) * qtf / (k2 + qtf)
        return w * temp / temp2 * temp3

    def generate_query_posting_list(self, query):
        posting_list = collections.defaultdict(lambda: 0)
        terms = re.split(" |-|/|,", query)
        terms = [term.lower() for term in terms if len(term) >= 1]
        len_ = len(terms)
        
        for i in range(len_ - 1):
            phrase = terms[i] + " " + terms[i + 1]
            posting_list[phrase] += 1
        
        return posting_list

    def get_positional_posting_list(self, phrase, k=5):
        
        term1, term2 = phrase
        if self.positional_term_dict.get(term1) and self.positional_term_dict.get(term2):
            term_id1 = self.positional_term_dict[term1]
            term_id2 = self.positional_term_dict[term2]
        else:
            return {}


        positional_posting_list = {}
        p1 = self.positional_term_posting_list[term_id1]
        p2 = self.positional_term_posting_list[term_id2]
        p1 = sorted(p1.items(), key=lambda x :x[0])
        p2 = sorted(p2.items(), key=lambda x :x[0])
        pointer1 = 0
        pointer2 = 0
        p1_len, p2_len = len(p1), len(p2)
        while(pointer1 < p1_len and pointer2 < p2_len):
            doc_id1 = p1[pointer1][0]
            doc_id2 = p2[pointer2][0]
            if doc_id1 < doc_id2:
                pointer1 += 1
            if doc_id2 < doc_id1:
                pointer2 += 1
            if doc_id1 == doc_id2:
                answer = []
                l = []
                pp1, pp2 = 0, 0
                positions1 = p1[pointer1][1]
                positions2 = p2[pointer2][1]
                while(pp1 < len(positions1)):
                    position1 = positions1[pp1]
                    while(pp2 < len(positions2)):
                        position2 = positions2[pp2]
                        if abs(position1 - position2) <= k:
                            l.append(position2)
                        elif position2 > position1:
                            break
                        pp2 += 1
                    l = [i for i in l if abs(i - position1) < k]
                    for i in l:
                        answer.append((position1, i))
                    pp1 += 1
                positional_posting_list[doc_id1] = answer
                pointer1 += 1
                pointer2 += 1
        return positional_posting_list

                    

if __name__ == "__main__":   
    lexicon_path = "results\single.lexicon"
    index_path = "results\single.index"
    document_path = "results\document_list.csv"
    loader = IndexLoader(index_path, lexicon_path, document_path).load_all()

    phrase_lexicon_path = "results\phrase.lexicon"
    phrase_index_path = "results\phrase.index"
    document_path = "results\document_list.csv"
    
    positional_index_path = "results\positional.index"
    positional_lexicon_path = "results\positional.lexicon"
    
    phraseloader = PositionalIndexLoader(positional_index_path, positional_lexicon_path, document_path, phrase_index_path, phrase_lexicon_path)
    phraseloader.load_all()
    phraseloader.load_positional_index()
    phraseloader.load_positional_lexicon()
    
    query_file_path = "queryfile.txt"
    reader = QueryReader(query_file_path)

    VSM = VectorSpaceModel(loader,reader.get_query())
    cosine_score_path = os.path.join("query_results", "COSINE_SCORE.txt")
    # VSM.run_query(cosine_score_path)



    # BM = BM25(loader, reader.get_query())
    # bm25_score_path = os.path.join("query_results", "BM25_SCORE.txt")
    # BM.run_query(bm25_score_path, size= 100)
    

    PositionalIndexModel = PhraseQueryModel(loader, reader.get_query(), phraseloader, VSM)
    s = PositionalIndexModel.get_positional_posting_list(["domestic", "violence"])
    pass
