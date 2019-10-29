import re
import csv
import collections
class IndexLoader:
    def __init__(self):
        pass 
    
    def load_lexicon(self, lexicon_path):
        """
        read document frequency list and term list
        document frequency list like
        [term0_df, term1_df]
        term_list like
        [term0, term1]
        term_dict like
        {
            "term0" : 0,
            "term1" : 1
        }
        """
        term_list = []
        document_frequency_list = []
        with open(lexicon_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                term_list.append(line[1])
                document_frequency_list.append(line[2])
        self.document_frequency_list = document_frequency_list
        self.term_list = term_list
        self.term_dict = {}
        n = 0 
        for i in term_list:
            self.term_dict[i] = n
            n += 1

    def load_index(self, index_path):
        """
        read term posting and generate the term frequency of collection
        term posting list like
        [
            {term0_doc0: term0_doc0_frequency,
             term0_doc1: term0_doc1_frequency}
        ]
        term frequency in collection like
        [term0_frequency_collection, term1_frequency_collection]
        """
        term_index = []
        with open(index_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                term_frequency = {}
                len_ = len(line)
                for i in range(1, len_, 2):
                    term_frequency[int(line[i])] = int(line[i+1])
                term_index.append(term_frequency)
        self.term_index = term_index

        self.term_frequency_collection = []
        for posting in term_index:
            total_frequency = sum(posting.values())
            self.term_frequency_collection.append(total_frequency)

    def load_document(self, document_path):
        """
        read document list and generate document dict
        document list like
        [doc_name0, doc_name1]
        document dict like 
        {
            "doc_name0":0,
            "doc_name1":1
        }
        """
        document_list = []
        document_dict = {}
        with open(document_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            n = 0
            for line in reader:
                document_list.append(line[1].strip(" "))
                document_dict[line[1].strip(" ")] = n
                n += 1
        self.document_list = document_list 
        self.document_dict = document_dict

    def generate_document_index(self):
        """
        generate document posting list like
        {
            doc_id：{"term_id": term_frequency}
        }
        generate document lenth list like
        [document0 lenth, document1 lenth]
        [10, 100 ]
        """
        document_index = collections.defaultdict(dict)
        n = 0 
        for posting_list in self.term_index:
            for doc_id, term_frequency in posting_list.items():
                document_index[doc_id][n] = term_frequency
            n += 1
        self.document_index = document_index
        self.document_lenth = []
        len_ = len(document_index.keys())
        for doc_id in range(len_):
            self.document_lenth.append(sum(document_index[doc_id].values()))
        self.collection_lenth = len_

if __name__ == "__main__":
    loader = IndexLoader()
    lexicon_path = "results\single.lexicon"
    loader.load_lexicon(lexicon_path)
    index_path = "results\single.index"
    loader.load_index(index_path)
    # print(loader.term_index[:100])
    document_path = "results\document_list.csv"
    loader.load_document(document_path)
    # print(loader.document_list[:100], loader.document_dict)
    loader.generate_document_index()
    print(loader.document_lenth)
