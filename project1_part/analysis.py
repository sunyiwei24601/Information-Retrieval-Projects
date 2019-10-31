from statistics import median, mean
import collections 
import csv
import math
from file_merger import write_triples
from matplotlib import pyplot as plt

class translator:
    def __init__(self, file_path):
        self.merge_file_path = file_path

    def single_term_translator(self, output_file):
        self.collection = collections.defaultdict(lambda : 0)
        reader = open(self.merge_file_path, encoding="utf-8")
        writer = open(output_file, "w", encoding="utf-8", newline="")
        csv_writer = csv.writer(writer, delimiter=",")
        csv_reader = csv.reader(reader, delimiter=",")
        self.term_list = []
        term_id = 0
        line = []
        for triple in csv_reader:
            if self.term_list:
                if triple[0] != self.term_list[-1]:
                    term_id += 1
                    self.term_list.append(triple[0])
                    csv_writer.writerow(line)
                    line = [term_id]
                    line += triple[1:]
                else:
                    line += triple[1:]
            else:
                self.term_list.append(triple[0])
                line.append(term_id)
                line += triple[1:]
            self.collector(triple[0])
        csv_writer.writerow(line)
        writer.close()
        reader.close()
                
    def position_term_translate(self, output_file):

        self.collection = collections.defaultdict(lambda : 0)
        reader = open(self.merge_file_path, encoding="utf-8")
        writer = open(output_file, "w", encoding="utf-8", newline="")
        csv_writer = csv.writer(writer, delimiter=",")
        csv_reader = csv.reader(reader, delimiter=",")
        self.term_list = []
        term_id = 0
        line = []
        for triple in csv_reader:
            if self.term_list:
                if triple[0] != self.term_list[-1]:
                    term_id += 1
                    self.term_list.append(triple[0])
            else:
                self.term_list.append(triple[0])

            csv_writer.writerow([term_id, *triple[1:] ])
            self.collector(triple[0])

        writer.close()
        reader.close()

    def phrase_term_translate(self, output_file, threshold):
        self.new_collection = collections.defaultdict(lambda : 0)
        self.plot_collections()
        reader = open(self.merge_file_path, encoding="utf-8")
        writer = open(output_file, "w", encoding="utf-8", newline="")
        csv_writer = csv.writer(writer, delimiter=",")
        csv_reader = csv.reader(reader, delimiter=",")
        self.term_list = []
        term_id = 0
        line = []
        self.collection = collections.defaultdict(lambda : 0)
        for triple in csv_reader:
            if self.new_collection[triple[0]] >= threshold:
                if self.term_list:
                    if triple[0] != self.term_list[-1]:
                        term_id += 1
                        self.term_list.append(triple[0])
                else:
                    self.term_list.append(triple[0])

                csv_writer.writerow([term_id, *triple[1:] ])
                self.collection[triple[0]] += 1
        writer.close()
        reader.close()

    def plot_collections(self, plot = False):
        reader = open(self.merge_file_path, encoding="utf-8")
        csv_reader = csv.reader(reader, delimiter=",")
        last_term = None
        for triple in csv_reader:
            if last_term:
                if triple[0] != last_term:
                    last_term = triple[0]
            else:
                last_term = triple[0]
            self.new_collection[triple[0]] += 1
        
        frequencies = list(self.new_collection.values())
        total_num = sum(frequencies)
        counts = collections.defaultdict(lambda: 0)
        for frequency in frequencies:
            counts[frequency] += 1

        log_counts = collections.defaultdict(lambda: 0)
        for frequency in frequencies:
            log_counts[int(math.log2(frequency))] += 1
        # x = sorted(list(counts.keys()))
        # y = [math.log2(counts[i]) for i in x]
        # plt.scatter(x, y, marker='.' , c='k')
        # plt.show()
        if plot:
            x = sorted(log_counts.keys())
            y = [math.log2(log_counts[i]) for i in x]
            plt.plot(x, y ,marker='o' , c='k')
            plt.show()
            print("max_frequency is ", max(frequencies) )
            print("mean_frequency is ", mean(frequencies))
            print("median_frequency is ", mean(frequencies))

    def collector(self, word):
        self.collection[word] += 1

    def analysis(self):
        self.triples = []
        for i in range(len(self.term_list)):
            term = self.term_list[i]
            self.triples.append([i, term, self.collection[term]])
        doc_frequencies = self.collection.values()
        print("Term Number is ", len(doc_frequencies))
        max_df = max(doc_frequencies)
        print("Max document frequency is " + str(max_df) )
        min_df = min(doc_frequencies)
        print("Min document frequency is ", min_df )
        mean_df = mean(doc_frequencies)
        print("Mean document frequency is ", mean_df )
        median_df = median(doc_frequencies)
        print("Median document frequency is ", median_df )

    def write_lexicon(self, outfile):
        write_triples(self.triples, outfile, "")