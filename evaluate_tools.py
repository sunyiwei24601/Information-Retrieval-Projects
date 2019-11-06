import re
import collections 
import sys
import os
import time
from QueryModel import *
from nltk.stem.porter import PorterStemmer
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
        LM.run_query(LM_score_path, size=self.size)
        
        os.system(".{}treceval {} {} > evaluation.txt".format(os.path.sep, self.qrel_path, LM_score_path))
    
    def run_VSM(self, loader, queries, COSINE_score_path=None):
        if COSINE_score_path == None:
            COSINE_score_path = os.path.join("query_results", "COSINE_SCORE.txt")
        VSM = VectorSpaceModel(loader, queries, stem=self.stem)
        VSM.run_query(COSINE_score_path, size=self.size)
        os.system(".{}treceval {} {} > evaluation.txt".format(os.path.sep, self.qrel_path, COSINE_score_path))

    def run_BM25(self, loader, queries, BM25_score_path=None):
        if BM25_score_path == None:
            BM25_score_path = os.path.join("query_results", "BM25_SCORE.txt")
        BM = BM25(loader, queries, stem=self.stem)
        BM.run_query(BM25_score_path, size=self.size)
        os.system(".{}treceval {} {} > evaluation.txt".format(os.path.sep, self.qrel_path, BM25_score_path))

    def run_Model(self, model_type, miu=1, times=1, output_path=None):
        running_time = []
        for i in range(times):
            start = time.time()
            query_file_path = "queryfile.txt"
            reader = QueryReader(query_file_path)
            queries = reader.get_query()
            if model_type == "LM":
                self.run_LM(self.loader, queries, miu=0.000001)
            if model_type == "BM25":
                self.run_BM25(self.loader, queries)
            if model_type == "COSINE":
                self.run_VSM(self.loader, queries)
            end = time.time()
            print("Running time is ", end - start)
            running_time.append(end - start)
        print("average time is ", sum(running_time) / len(running_time))






        

    

if __name__ == "__main__":
    eva = evaluator()
    lexicon_path = os.path.join("results","single.lexicon")
    index_path = os.path.join("results", "single.index")
    document_path = os.path.join("results", "document_list.csv")
    query_file_path = "queryfile.txt"

    # loader = IndexLoader(index_path, lexicon_path, document_path).load_all()

    test = Test(query_file_path, lexicon_path, index_path, document_path, stem=None)
    test.run_Model("LM", times=10)

