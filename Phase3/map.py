from get_result_information import *

RESULT_FILE = 'map_scores.txt'

def compute(rel_docs, results):
  if rel_docs == []:
    return None
    
  precision_values = []
  num_correct = 0
  num_seen = 0

  for result in results:
    num_seen = num_seen + 1

    if result in rel_docs:
      num_correct = num_correct + 1
      precision_values.append(num_correct / num_seen)

  if num_correct == 0:
    return 0

  return sum(precision_values) / len(precision_values)

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
