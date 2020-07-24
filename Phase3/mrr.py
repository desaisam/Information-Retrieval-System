from get_result_information import *

RESULT_FILE = 'mrr_scores.txt'

def compute(rel_docs, results):
  if rel_docs == []:
    return None
    
  rank_values = []
  current_rank = 0

  for result in results:
    current_rank = current_rank + 1

    if result in rel_docs:
      rank_values.append(1 / current_rank)

  return sum(rank_values)

if __name__ == '__main__':
  rel_docs_by_id = get_rel_docs_by_id(open(REL_FILE))
  result_file = open(RESULT_FILE, 'w+')

  for (score_file, num_queries, queryline) in SCORE_FILES:
    result_docs = get_results(open(score_file), num_queries, queryline)
    result_file.write(score_file + '\n')

    scores = [compute(rel_docs_by_id[qid], result_docs[qid]) for qid in range(0, len(result_docs))]
    scores = [score for score in scores if score is not None]
    average = sum(scores) / len(scores)
    result_file.write(str(average) + '\n')
