# coding: utf-8
import io
from pprint import pprint
import Parser
import json

# GLOBAL CONSTANTS
token_count = {}
inverted_idx = {}

def unigram_index():
    for doc_name in Parser.tokens_map:
        allwords = Parser.tokens_map[doc_name]
        token_count[doc_name] = len(allwords)
        for word in allwords:
            create_index(word,doc_name)
    print("Indexing - Complete")


def create_index(word,doc_name):
    if word not in inverted_idx:
        inverted_idx[word] = {doc_name : 1}
    elif doc_name not in inverted_idx[word]:
        inverted_idx[word][doc_name] = 1
    else:
        inverted_idx[word][doc_name] += 1

def output_index_to_file(filename):
    print("Saving index to file . .")

    #json.dump(open('unigram_index.json', 'w+'))
    #json.dump(open('unigram_index_tokens.json', 'w+')) #Uncomment these to get fresh json
    with io.open(filename + ".txt", "w") as outfile:
        pprint(inverted_idx, stream=outfile)
