import re
import collections 
import sys
import os
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

if __name__ == "__main__":
    eva = evaluator()
    
    eva.read_precision("evaluation.txt")
    print(eva.compute_MAP())
