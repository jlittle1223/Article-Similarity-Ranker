import argparse
import scholarly
import pickle
import numpy as np
import copy
import csv
from sklearn.feature_extraction.text import TfidfVectorizer

_PICKLE_FILE_PATH = "search_query.pk"
_OUTPUT_FILE_PATH = "result.csv"


def save_publication(publication, citations, pickle_file_path = _PICKLE_FILE_PATH):
    with open(pickle_file_path, "wb") as file:
        pickle.dump( (publication, citations) , file)

    print("Query Successfully Saved")


def load_publication(pickle_file_path = _PICKLE_FILE_PATH):
    with open(pickle_file_path, "rb") as file:
        query_tuple = pickle.load(file)
        publication = query_tuple[0]
        citations = query_tuple[1]
    return publication, citations



def save_output(publication, ranked_publications, fields):
    data_list = format_csv_data(publication, ranked_publications, fields)
    
    with open(_OUTPUT_FILE_PATH, "w", encoding = "utf8", newline = "") as file:
        writer = csv.DictWriter(file, fieldnames = fields)

        writer.writeheader()
        for row in data_list:
            writer.writerow(row)
        

def extract_fields(publication, fields):
    data = {}
    for field in fields:
        if field in publication.bib:
            data[field] = publication.bib[field]
        else:
            data[field] = None
    return data


def format_csv_data(publication, ranked_publications, fields):
    data_list = []
    data_list.append(extract_fields(publication, fields))
    for ranked_publication in ranked_publications:
        data_list.append(extract_fields(ranked_publication, fields))

    return data_list



def get_pairwise_similarity_masked(corpus):
    vect = TfidfVectorizer(min_df = 1, stop_words = "english")
    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = (tfidf * tfidf.T).toarray()

    #mask the ones in the diagonal so we can argmax
    pairwise_similarity_masked = copy.copy(pairwise_similarity)
    np.fill_diagonal(pairwise_similarity_masked, np.nan)

    return pairwise_similarity_masked



def rank_similarity(corpus: list, input_idx: int = 0) -> list:
    input_doc = corpus[input_idx]
    
    corpus_idx_ranked = []

    pairwise_similarity_masked = get_pairwise_similarity_masked(corpus)

    input_idx = corpus.index(input_doc)

    # argsort the row corresponding to the input_doc
    corpus_idx_ranked = np.argsort(pairwise_similarity_masked[input_idx]).tolist()

    # sort descending
    corpus_idx_ranked.reverse()

    # remove first entry which is always input_doc
    corpus_idx_ranked = corpus_idx_ranked[1:]

    return corpus_idx_ranked



def preprocess_abstract(abstract: str):
    # if abstract is cut off, remove ellipses
    if (abstract[-1] == "…"):
        abstract = abstract[:-2]
    return abstract
    


def create_corpus(publication, citations) -> list:
    publication_abstract = preprocess_abstract(publication.bib["abstract"])

    citation_abstract_dict = {}

    for citation in citations:
        if "abstract" in citation.bib:
            citation_abstract_dict[preprocess_abstract(citation.bib["abstract"])] = citations.index(citation)

    corpus = []

    corpus.append(publication_abstract)
    for citation_abstract in citation_abstract_dict.keys():
        corpus.append(citation_abstract)

    return corpus, citation_abstract_dict


    
def get_ranked_publications(citations, corpus, corpus_idx_ranked, citation_abstract_dict):
    ranked_publications = [citations[citation_idx] for citation_idx in [citation_abstract_dict[abstract] for abstract in [corpus[corpus_idx] for corpus_idx in corpus_idx_ranked]]]
    return ranked_publications



def display_ranked_corpus(corpus: list, corpus_idx_ranked: list, input_idx: int = 0):

    print("Input Document: '{}'".format(corpus[input_idx]))
    print()
    print("Ranked Similarity List:")

    
    for i, idx in enumerate(corpus_idx_ranked):
        print("{}: {}".format(i + 1, corpus[idx]))



def display_ranked_fields(publication, ranked_publications, fields = ["abstract"]):

    print("Input Document Title: '{}'".format(publication.bib["title"]))
    print()
    print("Ranked Similarity List:")

    
    for i, publication in enumerate(ranked_publications):
        print("{}:".format(i + 1))
        for field in fields:
            if field in publication.bib:
                print()
                print("{}: {}".format(field, publication.bib[field]))

        print()
        print()
                


def scholarly_search(query):
    print("Searching for publications...")
    
    search_query = list(scholarly.search_pubs_query(query))
    publication = search_query[0].fill()

    print("Searching for citations...")
    citations = [citation for citation in publication.get_citedby()]

    return publication, citations



def setup_argparser():
    parser = argparse.ArgumentParser(description = "This program will take as input a title of an article on google scholar and will output a ranked list of similar articles.")

    parser.add_argument("title", help = "Title of article to be searched for on google scholar")

    parser.add_argument("--load", help = "Loads a previously stored search query from search_query.pk",
                        action = "store_true")

    parser.add_argument("--save", help = "Saves the query locally to search_query.pk",
                        action = "store_true")

    parser.add_argument("--output", help = "If this flag is set, the data will be saved in {}".format(_OUTPUT_FILE_PATH),
                        action = "store_true")

    

    args = parser.parse_args()

    return args



def main():
    
    args = setup_argparser()

    query = args.title

    if args.load:
        publication, citations = load_publication()
    else:
        publication, citations = scholarly_search(query)
        if args.save:
            save_publication(publication, citations)

    corpus, citation_abstract_dict = create_corpus(publication, citations)

    corpus_idx_ranked = rank_similarity(corpus)

    #display_ranked_corpus(corpus, corpus_idx_ranked)

    ranked_publications = get_ranked_publications(citations, corpus, corpus_idx_ranked, citation_abstract_dict)

    fields = ["title", "abstract", "author", "eprint"]
    display_ranked_fields(publication, ranked_publications, fields)

    if args.output:
        save_output(publication, ranked_publications, fields)



if __name__ == "__main__":

    main()
    

    


