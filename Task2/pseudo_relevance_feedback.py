import json
import nltk
import operator
import os
import string
import sys
from nltk import ngrams


sys.path.append('../preprocessing')
sys.path.append('../Task1')

from task1 import *
from Indexer import *
from generate_index import *

INDEX_FILE = '../preprocessing/unigram_index.json'
OUTPUT_FILE = 'pseudo_relevance_feedback.txt'
index = json.load(open(INDEX_FILE, 'r'))
QUERY_FILE = '../preprocessing/cacm.query.txt'
CORPUS_PATH = '../preprocessing/CLEAN_CORPUS'

k = 10
n = 7
MAX_RESULTS = 100

def tfidf_search(query, max_results):
  qtf = queryTermFrequency(query)
  indexToUse = query_matching_index(qtf, inverted_idx)
  
  results = tfidf(indexToUse, queryTermFrequency(query), tokenCountInDocument)
  results = [(result, results[result]) for result in results]
  highestScoring = sorted(results, key=operator.itemgetter(1), reverse=True)[0:max_results]
  highestScoring = [(docid + '.txt', score) for (docid, score) in highestScoring]
  return highestScoring

def search(query):
  original_search = tfidf_search(query, k)
  original_search = [docid for (docid, score) in original_search]

  dict_content = create_dictionary_files(original_search, CORPUS_PATH)
  exclude = set(string.punctuation)
  dict_unigram = {}

  for docId, str_doc_content in dict_content.items():
    list_unigram = list(unigram(nltk.word_tokenize(str_doc_content)))
    # Remove punctutation
    list_unigram = [''.join(each_unigram) for each_unigram in list_unigram if each_unigram not in exclude]
    create_invIndex_unigram(docId, list_unigram, dict_unigram, dict_content)

  tf_idf_dict = {}
  for term in dict_unigram:
    entries = dict_unigram[term]
    tf = 0
    df = len(entries)
    for entry in entries:
      tf += entry['freq']

    tf_idf_dict[term] = 1.0 * tf / df

  highestScoring = sorted(tf_idf_dict.items(), key=operator.itemgetter(1), reverse=True)
  highestScoring = [term for (term, tf_idf) in highestScoring[0:n]]
  
  expanded_query = query + ' ' + ' '.join(highestScoring)

  return tfidf_search(expanded_query, MAX_RESULTS)

# TODO need results from magic_search
def compute_and_write(query, output, queryid):
  results = search(query)

  for (rank, (docid, score)) in enumerate(results):
    docid = docid[:-4] # Remove the .txt
    output.write(str(queryid) + ' Q0 ' + docid + ' ' + str(rank + 1) + ' ' + str(score) + ' PSEUDORELEVANCE\n')

if __name__ == '__main__':
  global tokenCountInDocument
  global inverted_idx

  tokenCountInDocument = json.load(open('../Task1/unigram_index_tokens.json'))
  inverted_idx = json.load(open('../Task1/unigram_index.json'))

  queries = extractQueriesFromCacmFile(QUERY_FILE)
  output = open(OUTPUT_FILE, 'w+')

  [compute_and_write(q, output, queryid + 1) for (queryid, q) in enumerate(queries)]

