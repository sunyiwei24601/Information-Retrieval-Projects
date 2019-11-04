import re
import csv
import collections
class IndexLoader:
    def __init__(self, index_path, lexicon_path, document_path):
        self.index_path = index_path
        self.lexicon_path = lexicon_path
        self.document_path = document_path
        pass 
    
    def load_all(self):
        self.load_document()
        self.load_index()
        self.load_lexicon()
        self.generate_document_index()
        return self 

    def load_lexicon(self, lexicon_path=None):
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
        if lexicon_path == None:
            lexicon_path = self.lexicon_path
        term_list = []
        document_frequency_list = []
        with open(lexicon_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                term_list.append(line[1])
                document_frequency_list.append(int(line[2]))
        self.document_frequency_list = document_frequency_list
        self.term_list = term_list
        self.term_dict = {}

        n = 0 
        for i in term_list:
            self.term_dict[i] = n
            n += 1

    def load_index(self, index_path=None):
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
        if index_path == None:
            index_path = self.index_path

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

    def load_document(self, document_path=None):
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
        if document_path == None:
            document_path = self.document_path
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
        self.document_posting_list = document_index
        self.document_lenth = []
        len_ = len(document_index.keys())
        for doc_id in range(len_):
            self.document_lenth.append(sum(document_index[doc_id].values()))
        self.collection_lenth = len_


class PositionalIndexLoader(IndexLoader):
    def __init__(self, positional_index_path, positional_lexicon_path, document_path, phrase_index_path, phrase_lexicon_path):
        super(PositionalIndexLoader, self).__init__(phrase_index_path, phrase_lexicon_path, document_path)
        self.positional_lexicon_path = positional_lexicon_path
        self.positional_index_path = positional_index_path

    def load_positional_index(self):
        index_path = self.positional_index_path
        term_posting_list = []
        with open(index_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            term_frequency = {}
            last_term_id = -1
            for line in reader:
                term_id = int(line[0])
                doc_id = int(line[1])
                positions = line[2:]
                if term_id != last_term_id:
                    if term_id != 0:
                        term_posting_list.append(term_frequency)
                    term_frequency = {}
                term_frequency[doc_id] = [int(i) for i in positions]
                last_term_id = term_id
            term_posting_list.append(term_frequency)

        self.positional_term_posting_list = term_posting_list

    def load_positional_lexicon(self):
        lexicon_path = self.positional_lexicon_path
        term_list = []
        document_frequency_list = []
        with open(lexicon_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                term_list.append(line[1])
                document_frequency_list.append(int(line[2]))
        self.positional_document_frequency_list = document_frequency_list
        self.positional_term_list = term_list
        self.positional_term_dict = {}

        n = 0 
        for i in term_list:
            self.positional_term_dict[i] = n
            n += 1 
        
if __name__ == "__main__":
    lexicon_path = "results\phrase.lexicon"
    index_path = "results\phrase.index"
    document_path = "results\document_list.csv"
    
    positional_index_path = "results\positional.index"
    positional_lexicon_path = "results\positional.lexicon"
    
    loader = PositionalIndexLoader(positional_index_path, positional_lexicon_path, document_path, index_path, lexicon_path)
    loader.load_all()
    loader.load_positional_index()
    loader.load_positional_lexicon()
    pass