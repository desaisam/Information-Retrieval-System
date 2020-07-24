import json
import operator
import random
import string

QUERIES_FILE = '../preprocessing/Clean_Query.txt'
INDEX_FILE = '../preprocessing/unigram_index.json'
OUTPUT_FILE = 'corrected_queries.txt'
COMMON_WORDS_FILE = '../preprocessing/common_words.txt'
MAX_LEV_DISTANCE = 2
MAX_RESULTS = 6

def lev(word1, word2, i, j, depth=0):
  if depth > MAX_LEV_DISTANCE or i < 0 or j < 0:
    return float('inf')

  if i == j and i == 0:
    return 0

  min1 = lev(word1, word2, i - 1, j, depth + 1) + 1
  min2 = lev(word1, word2, i , j - 1, depth + 1) + 1
  
  if word1[i-1] is not word2[j-1]:
    min3 = lev(word1, word2, i - 1, j - 1, depth + 1) + 1
  else:
    min3 = lev(word1, word2, i - 1, j - 1, depth)

  return min(min1, min2, min3)

def find_corrections(word, word_list):
  if word in word_list:
    return [word]

  first = word[0]
  word_list = [entry for entry in word_list if entry[0] == word[0]]

  results = []
  for entry in word_list:
    dist = lev(word, entry, len(word), len(entry), 0)
    if dist <= MAX_LEV_DISTANCE:
      results.append((entry, dist))

  results = sorted(results, key=operator.itemgetter(1)) # Rank by Levenshtein distance
  results = [result for (result, score) in results]
  return results[0:MAX_RESULTS]

if __name__ == '__main__':
  index = json.load(open(INDEX_FILE, 'r'))
  word_list = list(index.keys())
  output = open(OUTPUT_FILE, 'w+')
  common_words_file = open(COMMON_WORDS_FILE, 'r')

  common_words = common_words_file.readlines()
  common_words = [word[:-1] for word in common_words]

  for query in open(QUERIES_FILE, 'r'):
    new_query = ''
    for word in query.split(' '):
      if len(word) < 1:
        continue

      if word in common_words:
        new_query = new_query + word + ' '
        continue

      corrections = find_corrections(word, word_list)
      if len(corrections) == 0:
        new_query = new_query + '[?] '
      elif word == corrections[0]:
        new_query = new_query + word + ' '
      else:
        new_query = new_query + str(corrections) + ' '

    output.write(new_query[:-1] + '\n') # Remove trailing space