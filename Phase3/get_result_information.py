# Utility file to get result information

NUM_QUERIES = 64

# Format of filename, number of queries, if there is a query line
SCORE_FILES = [('../Task1/Outputs/BM25.txt', NUM_QUERIES, False),
  ('../Task1/Outputs/Lucene_scores.txt', NUM_QUERIES, False),
  ('../Task1/Outputs/QLM.txt', NUM_QUERIES, False),
  ('../Task1/Outputs/TFIDF.txt', NUM_QUERIES, False),
  ('../Task2/pseudo_relevance_feedback.txt', NUM_QUERIES, False),
  ('../Task2/query_time_stemming.txt', NUM_QUERIES, False),
  ('../Task3/RUN1/BM25_Scores.txt', NUM_QUERIES, True),
  ('../Task3/RUN1/LUCENE_results.txt', 7, False),
  ('pseudo_relevance_feedback_with_bm25.txt', NUM_QUERIES, False)]
REL_FILE = '../preprocessing/cacm.rel.txt'
NUM_RESULTS = 100

# Note that the queryids are offset by 1
def get_rel_docs_by_id(file):
  rel_docs_by_id = [[] for i in range(0, NUM_QUERIES + 1)]
  
  for line in file:
    entry = line.split(' ')
    queryId = int(entry[0]) - 1
    rel_docs_by_id[queryId].append(entry[2]) # Get the actual docID from the entry

  return rel_docs_by_id

def get_results(file, num_queries, queryline):
  results_by_id = []

  for _ in range(0, num_queries):
    if queryline:
      file.readline() # Ignore query line
    results = []

    for _ in range(0, NUM_RESULTS - 1):
      line = file.readline().strip()
      results.append(line.split(' ')[2])

    results_by_id.append(results)

  return results_by_id