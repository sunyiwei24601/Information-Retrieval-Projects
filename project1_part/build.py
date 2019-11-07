from indexer import *
from Parser import *
from analysis import *
import os


class Tester:
    def __init__(self, directory_path, index_type, output_file):
        self.directory_path = directory_path
        self.index_type = index_type
        self.output_file = output_file

    def running_process(self):
        write_triples.num = 0
        directory_path = self.directory_path
        index_type = self.index_type
        output_file = self.output_file
        memory_limit = self.memory_limit
        start = time.time()
        if index_type == "single":
            skip_stop_words, stemmer, parser_type = True, None, "single"
        if index_type == "positional":
            skip_stop_words, stemmer, parser_type = False, None, "single"
        if index_type == "stem":
            skip_stop_words, stemmer, parser_type = True, PorterStemmer(), "single"
        if index_type == "phrase":
            skip_stop_words, stemmer, parser_type = True, None, "phrase"

        doc_reader = reader(directory_path)
        documents = doc_reader.read_doc()

        parser = term_parser(skip_stop_words=skip_stop_words, stemmer=stemmer)
        tokenized_documents = parser.generate_documents(documents, parser_type=parser_type)
        indexer = Indexer(tokenized_documents, memory_limit, output_file)
        
        # collect the num of different special words

        if index_type == "positional":
            merge_out_file = indexer.single_term_indexer(position=True)
            analyst = translator(merge_out_file)
            analyst.position_term_translate(output_file)
        else:
            merge_out_file = indexer.single_term_indexer()
            analyst = translator(merge_out_file)
            if index_type == "phrase":
                analyst.phrase_term_translate(output_file, 5)
            else:
                analyst.single_term_translator(output_file)

        analyst.analysis()
        analyst.write_lexicon(os.path.join(output_dir, index_type + ".lexicon"))
        end = time.time()
        total_time = end - start
        print("Memory limit {} Total Running time is {:.3f}".format(memory_limit, total_time))
        collection = dict(parser.collection)
        # json.dump(collection, open("special_symbol.json", "w"))
        doc_list = indexer.doc_list
        self.print_doc(doc_list)
        return indexer.triple_write_time, indexer.merge_time, total_time

    def mean_running_time(self, times, memory_limit, output=False):
        self.merge_time = []
        self.triple_wrtie_time = []
        self.total_time = []
        self.memory_limit = memory_limit
        for i in range(times):
            print("This is the {}th time running".format(i+1))
            t, m ,total = self.running_process()
            self.merge_time.append(m)
            self.triple_wrtie_time.append(t)
            self.total_time.append(total)

        if output:
            self.output()

    def output(self):
        self.analysis("{} with {} memory limit triple_time ".format(self.index_type, self.memory_limit), self.triple_wrtie_time)
        self.analysis("{} with {} memory limit merge_time ".format(self.index_type, self.memory_limit), self.merge_time)
        self.analysis("{} with {} memory limit total_time ".format(self.index_type, self.memory_limit), self.total_time)

    def analysis(self, name, frequence):
        max_time = max(frequence)
        min_time = min(frequence)
        mean_time = mean(frequence)
        print("{} max {:.3f} min {:.3f} mean {:.3f}".format(name, max_time, min_time, mean_time))

    def print_doc(self, doc_list):
        doc_output_dir = os.path.dirname(self.output_file)
        doc_output_path = os.path.join(doc_output_dir, "document_list.csv")
        writer = open(doc_output_path, "w", encoding="utf-8", newline="")
        csv_writer = csv.writer(writer, delimiter=",")
        n = 0
        for doc in doc_list:
            csv_writer.writerow([n, doc])
            n += 1
        writer.close()

if __name__ == "__main__":
    parameters = sys.argv
    directory_path = parameters[1] 
    index_type = parameters[2]
    output_dir = parameters[3]
    
    # directory_path = os.path.join(".","BigSample") 
    # index_type = "positional"
    # output_dir = os.path.join(".", "results")
    output_file = os.path.join(output_dir, index_type + ".index")
    # memory_limit = int(parameters[1])
    memory_limit = 10000
    Test = Tester(directory_path, index_type, output_file)
    Test.mean_running_time(1, memory_limit)