import json
import sys
import operator
from nltk.stem.porter import *

sys.path.append('../Task1')
from task1 import *

QUERY_FILE = '../preprocessing/cacm.query.txt'
OUTPUT_FILE = 'query_time_stemming.txt'
MAX_RESULTS = 100
ps = PorterStemmer()

def tfidf_search(query, max_results):
  qtf = queryTermFrequency(query)
  indexToUse = query_matching_index(qtf, inverted_idx)

  results = tfidf(indexToUse, queryTermFrequency(query), tokenCountInDocument)
  results = [(result, results[result]) for result in results]
  highestScoring = sorted(results, key=operator.itemgetter(1), reverse=True)[0:max_results]
  highestScoring = [(docid, score) for (docid, score) in highestScoring]
  return highestScoring

def get_stems(word):
  return ps.stem(word)

def search(query):
  words = query.split(' ')
  stemmed_words = []

  for word in words:
    stemmed = get_stems(word)
    if stemmed != word:
      stemmed_words.append(stemmed)

  words.extend(stemmed_words)
  expanded_query = ' '.join(words)
  return tfidf_search(expanded_query, MAX_RESULTS)

def compute_and_write(query, queryid):
  results = search(query)

  for (rank, (docid, score)) in enumerate(results):
    output.write(str(queryid) + ' Q0 ' + docid + ' ' + str(rank + 1) + ' ' + str(score) + ' QUERYTIMESTEM\n')


if __name__ == '__main__':
  global tokenCountInDocument
  global inverted_idx

  tokenCountInDocument = json.load(open('../Task1/unigram_index_tokens.json'))
  inverted_idx = json.load(open('../Task1/unigram_index.json'))

  queries = extractQueriesFromCacmFile(QUERY_FILE)
  output = open(OUTPUT_FILE, 'w+')

  [compute_and_write(q, queryid + 1) for (queryid, q) in enumerate(queries)]