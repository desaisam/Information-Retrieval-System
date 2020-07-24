# coding: utf-8
import io
import os
import sys
import math
import string
import re
import traceback
import Indexer
import Parser


# GLOBAL CONSTANTS
output_directory = os.path.join(os.getcwd(), "Outputs")
retrievalModel = ""
tokenCountInDocument = {}
inverted_idx = {}
qid = 0


def setSelector(userInput):
    global retrievalModel
    if userInput == "1":
        retrievalModel = "TFIDF"
    elif userInput == "2":
        retrievalModel = "QLM"
    elif userInput == "3":
        retrievalModel = "BM25"

def extractQueriesFromCacmFile(query_file):
    queries = []
    queries_from_cacm_file = open(query_file,'r').read()
    while queries_from_cacm_file.find('<DOC>')!=-1:
        query, queries_from_cacm_file = extractQuery(queries_from_cacm_file)
        queries.append(query.lower())
    return queries

def extractQuery(queries_from_cacm_file):
    transformed_query = []
    query = queries_from_cacm_file[queries_from_cacm_file.find('</DOCNO>') + 8:queries_from_cacm_file.find('</DOC>')]
    query = str(query).strip()

    query_terms = query.split()

    for term in query_terms:
        transformed_term = term.strip(string.punctuation)
        transformed_term = re.sub(r'[^a-zA-Z0-9\-,\.–]', '', str(transformed_term))
        if transformed_term != '':
            transformed_query.append(transformed_term)

    query = " ".join(transformed_query)
    queries_from_cacm_file = queries_from_cacm_file[queries_from_cacm_file.find('</DOC>')+6:]
    return query, queries_from_cacm_file

def queryTermFrequency(query):
    qtf = {}
    termsInQuery = query.split()
    for term in termsInQuery:
        if term not in qtf:
            qtf[term] = 1
        else:
            qtf[term] += 1
    return qtf

def query_matching_index(qtf, idx=inverted_idx):
    index = {}
    for queryterm in qtf:
        if queryterm in idx:
            index[queryterm] = idx[queryterm]
        else:
            index[queryterm] = {}
    return index


def compute(indexForQueryTerms, qtf):
    global retrievalModel
    if retrievalModel == "BM25":
        return BM25_score(indexForQueryTerms, qtf)
    elif retrievalModel == "TFIDF":
        return tfidf(indexForQueryTerms, qtf)
    elif retrievalModel == "QLM":
        return QLM_score(indexForQueryTerms, qtf)


# BM25 FUNCTION
def BM25_score(indexForQueryTerms, qtf, tokenCountInDocument=tokenCountInDocument, rel_file="cacm.rel.txt"):
    # BM25 constants
    avdl = avgDocLength(tokenCountInDocument)
    N = len(tokenCountInDocument)
    b = 0.75
    k1 = 1.2
    k2 = 100
    dl = 0
    BM25_score = {}
    querydocs = calculateRValue(rel_file)
    R = len(querydocs)
    for eachqueryterm in qtf:
        # Calculating n_i value
        n_i = len(indexForQueryTerms[eachqueryterm])
        # Calculating qf value 
        qf = qtf[eachqueryterm]
        # Calculating r_i value
        if eachqueryterm in inverted_idx:
            r_i = documentCount(inverted_idx[eachqueryterm],querydocs)
        else:
            r_i = 0
        # Calculating document length 'dl' value
        for doc in indexForQueryTerms[eachqueryterm]:
            freq = indexForQueryTerms[eachqueryterm][doc]
            if doc in tokenCountInDocument:
                dl = tokenCountInDocument[doc]
            #Calculating K_value
            K_value = k1 * ((1-b) + ( b*(float(dl)/float(avdl))))
            # Calculating BM25 components
            p1 = math.log(((r_i + 0.5) / (R - r_i + 0.5)) / ((n_i - r_i + 0.5) / (N - n_i - R + r_i + 0.5)))
            p2 = ((k1 + 1) * freq) / (K_value + freq)
            p3 =  ((k2 + 1) * qf) / (k2 + qf)

            # Calculating BM25 score 
            if doc in BM25_score:
                BM25_score[doc] +=( p1 * p2 * p3)
            else:
                BM25_score[doc] =( p1 * p2 * p3)
    return BM25_score

# For BM25
def avgDocLength(tokenCountInDocument=tokenCountInDocument):
    length = 0
    for document in tokenCountInDocument:
        length = length + tokenCountInDocument[document]
    total_length = float(length)/float(len(tokenCountInDocument))
    return total_length

# For BM25 
def calculateRValue(rel_file="cacm.rel.txt"):
    try:
        docs = []
        R_docs = []
        with io.open(rel_file,'r', encoding="utf-8") as file:
            for line in file.readlines():
                values = line.split()
                if values and (values[0] == str(qid)):
                    docs.append(values[2])
            for doc_id in tokenCountInDocument:
                if doc_id in docs:
                    R_docs.append(doc_id)
        return R_docs
    except Exception as e:
        print(traceback.format_exc())

# For BM25
def documentCount(docs_with_term,relevant_docs):
    count = 0
    for doc_id in docs_with_term:
        if doc_id in relevant_docs:
            count+=1
    return count


# TFIDF FUNCTION
def tfidf(indexForQueryTerms, qtf, tokenCountInDocument=tokenCountInDocument):
    TFIDF_score = {}
    dictionary = {}
    for term in indexForQueryTerms:
        idf = 1.0 + math.log(float(len(tokenCountInDocument)) / float(len(indexForQueryTerms[term].keys()) + 1))
        for doc_id in indexForQueryTerms[term]:
            tf = float(indexForQueryTerms[term][doc_id])/float(tokenCountInDocument[doc_id])
            if term not in dictionary:
                dictionary[term] = {}
            dictionary[term][doc_id] = tf * idf

    for term in indexForQueryTerms:
        for doc in indexForQueryTerms[term]:
            documentWeight = 0
            documentWeight = documentWeight + dictionary[term][doc]
            if doc in TFIDF_score:
                documentWeight = documentWeight + TFIDF_score[doc]
            TFIDF_score.update({doc:documentWeight})
    return TFIDF_score


# QLM with JM smoothing
def QLM_score(indexForQueryTerms, query_term_freq):
    C = 0
    lambdaValue = 0.35
    QLM_score = {}
    for doc in tokenCountInDocument:
        C = C + tokenCountInDocument[doc]
    for query_term in query_term_freq:
        countOfQueryTermsInCollection = 0
        for doc in indexForQueryTerms[query_term]:
            countOfQueryTermsInCollection += indexForQueryTerms[query_term][doc]
        for doc in indexForQueryTerms[query_term]:
            D = tokenCountInDocument[doc]
            frequencyOfQueryTerms = indexForQueryTerms[query_term][doc]
            p1 = float(1-lambdaValue) * (frequencyOfQueryTerms / D)
            p2 = float(lambdaValue) * (countOfQueryTermsInCollection / C)
            if doc in QLM_score:
                QLM_score[doc] = QLM_score[doc] + math.log(p1 + p2)
            else:
                QLM_score[doc] = math.log(p1 + p2)
    return QLM_score

def outputFile(scores, qid):
    output_file = os.path.join(output_directory,retrievalModel+".txt")
    rank = 0
    with io.open(output_file ,"a+") as file:
        sorted_scores = [(k, scores[k]) for k in sorted(scores, key=scores.get, reverse = True)]
        for i in range(min(len(sorted_scores),100)):
            k,v = sorted_scores[i]
            rank += 1
            file.write(str(qid) + " " + "Q0 "+ k + " " + str(rank) + " " + str(v) +" "+retrievalModel+"\n")

def ask_user():
    print("Press 1 for TF-IDF")
    print("Press 2 for QLM with JM smoothing")
    print("Press 3 for BM25")
    print("Press q to quit")
    userInput = input("Enter your choice: ")
    return userInput

def index_creation():
    Parser.main()
    Indexer.unigram_index()
    Indexer.output_index_to_file("unigram_index")


def main():
    global qid
    global inverted_idx
    global retrievalModel
    global tokenCountInDocument

    index_creation()

    inverted_idx = Indexer.inverted_idx
    tokenCountInDocument = Indexer.token_count

    userInput = ask_user()
    if userInput == 'q':
        sys.exit()
    elif userInput not in ["1", "2", "3"]:
        print("\nInput incorrect. Exiting program.")
        sys.exit()
    else:
        setSelector(userInput)

        os.makedirs(output_directory,exist_ok=True)
        output_file = os.path.join(output_directory,retrievalModel+".txt")
        if os.path.exists(output_file):
            os.remove(output_file)

        queries = extractQueriesFromCacmFile("cacm.query.txt")
        for individualquery in queries:
            qid +=1
            qtf = queryTermFrequency(individualquery)
            indexForQueryTerms = query_matching_index(qtf)
            scores = compute(indexForQueryTerms, qtf)
            outputFile(scores,qid)
        print("Process Complete. Please wait for results in Outputs folder. ")

if __name__ == '__main__':
  main()
