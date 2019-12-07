import re
import collections 
import sys
import os
import time
from QueryModel import *
from nltk.stem.porter import PorterStemmer
from QueryReduction.ReduceQuery import *
class evaluator:
    def __init__(self):
        pass 

    def read_precision(self, evaluation_report_path):
        with open (evaluation_report_path) as f:
            results = collections.defaultdict(dict)
            line = f.readline()
            while(line):
                num = self.identify_num(line)
                if num:
                    query_num = num 
                    line = f.readline()
                    continue
                if self.identify("AP", line):
                    results[query_num]["AP"] = eval(f.readline())
                    line = f.readline()
                    continue
                if self.identify("RP", line):
                    results[query_num]["RP"] = eval(f.readline()[-6:])
                    line = f.readline()
                    continue
                line = f.readline()
        self.results = results

    def identify(self, type, line):
        if type == "AP":
            if re.match(".*Average precision \(non-interpolated\) over all rel docs", line):
                return True
            else:
                return False
        if type == "RP":
            if re.match("R-Precision (precision after R (= num_rel for a query) docs retrieved):", line):
                return True
            else:
                return False

    def identify_num(self, line):
        r = re.match("Queryid \(Num\):      ([0-9]+)", line)
        if r:
            return r.group()
        else:
            return False
        
    def compute_MAP(self):

        APs = [i["AP"] for i in self.results.values()]
        return sum(APs) / len(APs)

class Test:

    def __init__(self, query_file_path=None, lexicon_path=None, index_path=None, document_path=None, size=100, stem=None, qrel_path="qrel.txt"):
        self.loader = IndexLoader(index_path, lexicon_path, document_path).load_all()
        self.size = size 
        self.stem = stem 
        self.qrel_path = qrel_path
        self.query_file_path = query_file_path

    def run_LM(self, loader, queries, miu=1, LM_score_path=None):
        LM = LanguageModel(loader, queries, miu=miu, stem=self.stem)
        if LM_score_path == None:
            LM_score_path = os.path.join("query_results", "DIRICHLET_SCORE.txt")
        scores = LM.run_query(LM_score_path, size=self.size)
        
        # os.system(".{}treceval {} {}".format(os.path.sep, self.qrel_path, LM_score_path))
        os.system(".{}treceval.exe {} {} > evaluation.txt".format(os.path.sep, self.qrel_path, LM_score_path))
        return scores

    def run_VSM(self, loader, queries, COSINE_score_path=None):
        if COSINE_score_path == None:
            COSINE_score_path = os.path.join("query_results", "COSINE_SCORE.txt")
        VSM = VectorSpaceModel(loader, queries, stem=self.stem)
        scores =  VSM.run_query(COSINE_score_path, size=self.size)
        os.system(".{}treceval.exe {} {} > evaluation.txt".format(os.path.sep, self.qrel_path, COSINE_score_path))
        return scores

    def run_BM25(self, loader, queries, BM25_score_path=None):
        if BM25_score_path == None:
            BM25_score_path = os.path.join("query_results", "BM25_SCORE.txt")
        BM = BM25(loader, queries, stem=self.stem)
        scores =  BM.run_query(BM25_score_path, size=self.size)
        os.system(".{}treceval.exe {} {} > evaluation.txt".format(os.path.sep, self.qrel_path, BM25_score_path))
        return scores 

    def run_Model(self, model_type, miu=1, times=1, output_path=None):
        running_time = []
        for i in range(times):
            start = time.time()
            query_file_path = "queryfile.txt"
            reader = QueryReader(query_file_path)
            queries = reader.get_query()


            if model_type == "lm":
                scores = self.run_LM(self.loader, queries, miu=400, LM_score_path=output_path)
            if model_type == "bm25":
                scores = self.run_BM25(self.loader, queries, BM25_score_path=output_path)
            if model_type == "cosine":
                scores = self.run_VSM(self.loader, queries, COSINE_score_path=output_path)
            end = time.time()
            print("Running time is ", end - start)
            # eva.read_precision("evaluation.txt")
            # print("human calculated MAP is " , eva.compute_MAP())
            running_time.append(end - start)
        print("average time is ", sum(running_time) / len(running_time))
        return scores

    def run_Model_query_processed(self, model_type, miu=1, times=1, output_path=None):
        running_time = []
        for i in range(times):
            start = time.time()
            queries = self.queries
            if model_type == "lm":
                scores = self.run_LM(self.loader, queries, miu=0.0000001, LM_score_path=output_path)
            if model_type == "bm25":
                scores = self.run_BM25(self.loader, queries, BM25_score_path=output_path)
            if model_type == "cosine":
                scores = self.run_VSM(self.loader, queries, COSINE_score_path=output_path)
            end = time.time()
            print("Running time is ", end - start)
            # eva.read_precision("evaluation.txt")
            # print("human calculated MAP is " , eva.compute_MAP())
            running_time.append(end - start)
        print("average time is ", sum(running_time) / len(running_time))
        return scores

    def reduce_query(self, threshold, reduce_type):
        query_file_path = self.query_file_path
        reader = QueryReader(query_file_path)
        old_queries = list(reader.get_query())
        queries = reader.get_query_with_narrative()
        reducer = QueryReducer(self.loader, queries)
        self.queries = reducer.get_reduced_query(threshold, reduce_type)
        pass



        

    

if __name__ == "__main__":
    parameters = sys.argv
    # index_directory_path = parameters[1]
    # query_file_path = parameters[2]
    # retrieval_model = parameters[3]
    # index_type = parameters[4]
    # results_file = parameters[5]


    index_directory_path = "results"
    query_file_path = "queryfile.txt"
    retrieval_model = "cosine"
    index_type = "single"
    results_file = "query_results\\cosine_single_reduce_qf_idf.txt"
    

    if index_type == "stem":
        lexicon_path = os.path.join(index_directory_path,"stem.lexicon")
        index_path = os.path.join(index_directory_path, "stem.index")
        document_path = os.path.join(index_directory_path, "document_list.csv")
    elif index_type == "single":
        lexicon_path = os.path.join(index_directory_path,"single.lexicon")
        index_path = os.path.join(index_directory_path, "single.index")
        document_path = os.path.join(index_directory_path, "document_list.csv")

    query_file_path = query_file_path
    # loader = IndexLoader(index_path, lexicon_path, document_path).load_all()
    test = Test(query_file_path, lexicon_path, index_path, document_path, size=100)
    test.reduce_query(1, "qtf*idf")
    # test.run_Model(retrieval_model, times=1, output_path=results_file)

    test.run_Model_query_processed(retrieval_model, times=1, output_path=results_file)

    

