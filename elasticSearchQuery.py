from index_loader import *
from query_reader import *
import requests
import json
import csv
class ElasticSeach:
    def __init__(self):
        pass 

    def get_queries(self, queries, output_path = "query_results\ElasticSearch.txt"):
        results = []
        for query in queries:
            query_id = query[0]
            query_text = query[1]
            result = self.request_search_query(query_text)
            results += list(self.result_extract(result, query_id))

        self.output(results, output_path)

    def request_search_query(self, query_text):
        query = self.create_query(query_text)
        headers = {
            "Content-Type":"application/json"
        }
        r = requests.get("http://localhost:9200/trec/_search", data = json.dumps(query), headers=headers)
        result = json.loads(r.text)
        return result

    def create_query(self, text, size=100):
        search_json = {
        "query": {
            "bool": {
            "must": [
                {
                "match": {
                    "text": text
                }
                }
            ],
            "must_not": [ ],
            "should": [ ]
            }
        },
        "from": 0,
        "size": size,
        "sort": [ ],
        "aggs": { }
        }
        return search_json
    
    def result_extract(self, result, query_id):
        hits = result['hits']['hits']
        n = 0
        results =[]
        for hit in hits:
            score = hit['_score']
            doc_name = hit['_source']['doc_name']
            doc_id = hit['_id']
            
            yield [query_id, 0, doc_name, n, score, "ElasticSearch"]
            n += 1
        
    def output(self, extract_result, output_path):
        with open(output_path, 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=' ')
            for line in extract_result:
                writer.writerow(line)
        
        


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

    query_reader = QueryReader("queryfile.txt")
    queries = query_reader.get_query()

    searcher = ElasticSeach()
    searcher.get_queries(queries)
    