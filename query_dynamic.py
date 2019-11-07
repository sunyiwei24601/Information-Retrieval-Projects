from query import *

if __name__ == "__main__":
    



    parameters = sys.argv
    index_directory_path = parameters[1]
    query_file_path = parameters[2]

    results_file = parameters[3]

    lexicon_path = os.path.join(index_directory_path, "stem.lexicon")
    index_path = os.path.join(index_directory_path, "stem.index")
    document_path = os.path.join(index_directory_path, "document_list.csv")
    loader = IndexLoader(index_path, lexicon_path, document_path).load_all()

    phrase_lexicon_path = os.path.join(index_directory_path, "phrase.lexicon")
    phrase_index_path = os.path.join(index_directory_path, "phrase.index")
    document_path = os.path.join(index_directory_path, "document_list.csv")

    positional_index_path = os.path.join(index_directory_path, "positional.index")
    positional_lexicon_path = os.path.join(index_directory_path, "positional.lexicon")

    phrase_loader = IndexLoader(phrase_index_path, phrase_lexicon_path, document_path).load_all()
    phrase_loader.document_lenth = loader.document_lenth
    
    positional_loader = PositionalIndexLoader(positional_index_path, positional_lexicon_path, document_path).load_all()
    positional_loader.document_lenth = loader.document_lenth
    positional_loader.collection_lenth = loader.collection_lenth

    reader = QueryReader(query_file_path)

    Phrase = PhraseIndexModel(phrase_loader, reader.get_query())
    bm25_score_path = os.path.join("query_results", "Phrase_SCORE.txt")
    phrase_scores = Phrase.run_query(bm25_score_path, size= 100)

    # LM = LanguageModel(loader, reader.get_query())
    # LM_score_path = os.path.join("query_results", "DIRICHLET_SCORE.txt")
    # LM.run_query(LM_score_path)

    reader = QueryReader(query_file_path)
    PM = PositionalQueryModel(positional_loader, reader.get_query())
    positional_score_path = os.path.join("query_results", "positional_score.txt")
    positional_scores = PM.run_query(positional_score_path, size=10)

    reader = QueryReader(query_file_path)
    BM = BM25(loader, reader.get_query(), stem=PorterStemmer())
    bm25_score_path = os.path.join("query_results", "BM25_score.txt")
    bm25_scores = BM.run_query(bm25_score_path, size=100)

    merge_scores = combine_scores(phrase_scores, positional_scores, bm25_scores, alpha=50, mu=0, size=100)
    PM.output_result(merge_scores, results_file)

