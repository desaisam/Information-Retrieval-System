import math
import time
import operator
import json
import nltk
import os
import re
import string
import unicodedata
import shutil
from nltk import ngrams

# Create Inverted Index :

pwd = os.getcwd()
dir_path = pwd + '/STOP_CORPUS'
unigram_index_file = pwd + '/unigram_index.json'
# Lists to store the unigram, bigram and trigram generated
list_unigram = []

dict_freq = {}
dict_no_terms = {}

# Create unigrams
def unigram(tokens):
    return list(ngrams(tokens, 1))

def create_dictionary_files(files, path):
    dict_file_content = {}
    for each_tokenised_file in files:
        fh = open(path + '\\' + each_tokenised_file, 'r', encoding='utf-8')
        docId_dupl = each_tokenised_file[:-4]
        docId_dupl = docId_dupl.replace("(", "")
        docId_dupl = docId_dupl.replace(")", "")
        if "," in docId_dupl:
            docId_dupl = docId_dupl.replace(",", "")
        # Remove punctuation other than hypen and use lowercase terms
        str_doc_content_dupl = str(fh.read().lower())
        remove = string.punctuation
        remove = remove.replace("-", "")
        pattern = r"[{}]".format(remove)
        str_doc_content_dupl = re.sub(pattern, "", str_doc_content_dupl)
        dict_file_content[docId_dupl] = str_doc_content_dupl
    return dict_file_content

def create_invIndex_unigram(docId_uni, list_unigram_func, dict_unigram, dict_content):
    start_bi = time.time()
    # docId_uni = unicodedata.normalize('NFKD', docId_uni)
    # dict_no_terms[docId_uni] = len(list_unigram_func)
    dict_temp = {}
    counter = 1
    str_doc_content = dict_content[docId_uni]
    dict_no_terms[docId_uni] = len(list_unigram_func)
    for index, each_unigram in enumerate(list_unigram_func):
        pos = index + 1
        if each_unigram not in dict_unigram.keys():
            dict_unigram[each_unigram] = [{'docId': docId_uni, 'freq': 1, 'pos': [pos]}]
        else:
            for index, each_dict in enumerate(dict_unigram[each_unigram]):
                if docId_uni == each_dict['docId']:
                    temp = index
                    break
                temp = -1
            if temp != -1:
                dict_unigram[each_unigram][temp]['freq'] += 1
                list_pos = dict_unigram[each_unigram][temp]['pos']
                list_pos.append(pos)
                dict_unigram[each_unigram][temp]['pos'] = list_pos
            else:
                dict_unigram[each_unigram].append({'docId': docId_uni, 'freq': 1, 'pos': [pos]})
    end_bi = time.time()

if __name__ == '__main__':
  # Read all the files one by one
  all_files = os.listdir(dir_path)

  dict_unigram = {}

  dict_content = create_dictionary_files(all_files, dir_path)
  exclude = set(string.punctuation)

  print("Creating unigram index\n")

  for docId, str_doc_content in dict_content.items():
      list_unigram = list(unigram(nltk.word_tokenize(str_doc_content)))
      # Remove punctutation
      list_unigram = [''.join(each_unigram) for each_unigram in list_unigram if each_unigram not in exclude]
      create_invIndex_unigram(docId, list_unigram, dict_unigram, dict_content)

  print("Writing unigram index to file\n")

  output_file = open(unigram_index_file, 'w+')
  json.dump(dict_unigram, output_file)