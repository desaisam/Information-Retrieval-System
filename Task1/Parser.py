# coding: utf-8
from bs4 import BeautifulSoup
import io
import re
import glob, os
import string


corpus_path = os.path.join(os.getcwd(), "cacm")
tokens_map = {}
text_map =  os.path.join(corpus_path,r"TextFiles")

def tokenCorpus(individualfile):
    with io.open(individualfile,"r", encoding="utf-8") as file:
        lines = file.read()
    body_content = parsehtml(lines)
    tokens = makeTokens(body_content)
    tokens = uniformize(tokens)
    tokens = puncuations(tokens)
    savefile(tokens,individualfile)


def parsehtml(html_file):
    parsefile = BeautifulSoup(html_file, 'html.parser')
    content = parsefile.find("pre").get_text()
    match = re.search(r'\sAM|\sPM',content)
    if match:
        content = content[:match.end()]
    return content

def makeTokens(text_content):
    tokens = text_content.split()
    regex = re.compile('\w')
    return list(filter(regex.search, tokens))

def uniformize(tokens):
    return [x.casefold() for x in tokens]

def puncuations(tokens):
    punctuation = []
    for token in tokens:
        punctuation.append(remove(token))
    regex = re.compile('\S')
    return list(filter(regex.search, punctuation))

def remove(s):
    s = re.sub(r'[^a-zA-Z0-9\-,\.–:]', '', str(s))
    s = s.strip(string.punctuation)
    number = re.compile(r'[0-9]+([\d[,.:]?]?\d)*[-\.%–]?([\d[,.:]?]?\d)*$')
    if number.match(s):
        return s
    else:
        str_form = re.sub(r'[^a-zA-Z0-9\-–]', '', s)
        str_form = str_form.strip(string.punctuation)
        return str_form

def savefile(tokens,file):
    global tokens_map
    filename = os.path.basename(file)
    doc_id = filename[:-5]
    output_file = os.path.join(text_map,doc_id+".txt")
    tokens_map[doc_id] = tokens
    with io.open(output_file, "w", encoding="utf-8") as tokenized_html:
        for token in tokens:
            tokenized_html.write(token+"\n")


def main():
    input_path = os.path.join(corpus_path, r"*.html")
    files = glob.glob(input_path)
    os.makedirs(text_map,exist_ok=True)

    for individualfile in files:
        tokenCorpus(individualfile)
    print("Tokenizing - Complete")
