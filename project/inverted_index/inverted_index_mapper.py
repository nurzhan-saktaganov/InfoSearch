#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import base64
import zlib

import lxml
import lxml.html.clean

import argparse

# stemmer
import snowballstemmer

__author__ = 'Nurzhan Saktaganov'

SPLIT_RGX = re.compile('\w+', re.U)

# term_to
TO_POSITIONS = 0
TO_ENDING_ID = 1

def get_args():
    # -x / --xpaths - <file with xpaths to delete>
    # -s / --stopwords - <file with stop words>
    # -b / --banned - <file with documents not to index>
    # -e / --endings - <file with endings>
    parser = argparse.ArgumentParser(\
        description='Inverted index mapper', epilog='by ' + __author__)
    parser.add_argument('-x', '--xpaths', help='file with xpaths to delete',\
        metavar='<xpaths file path>', dest='xpaths', required=False,type=str, default=None)
    parser.add_argument('-s', '--stopwords', help='file with stop words',\
        metavar='<stop words file path>', dest='stopwords', required=False, type=str, default=None)
    parser.add_argument('-b', '--banned', help='file with documents not to index',\
        metavar='<banned documents file path>', dest='banned', required=False,type=str,default=None)
    parser.add_argument('-e', '--endings', help='word endings (suffixes)',\
        metavar='<endings file path>', dest='endings', required=True, type=str)
    return parser.parse_args()

get_ending = lambda word, stemmed_word: word[len(stemmed_word):]

def main():
    args = get_args()

    # hadoop cluster doesn't support the "kill_tags" argument
    script_cleaner = lxml.html.clean.Cleaner(scripts=True,javascript=True,\
        comments=True,style=True,links=True,meta=False,remove_tags=['a', 'img']) #,kill_tags=['script','style'])

    stemmer = snowballstemmer.stemmer('russian')

    xpaths, stopwords, banned, endings = [], [], [], []

    # loading xpaths
    if args.xpaths != None:
        with open(args.xpaths, 'r') as f:
            xpaths = list(set([xpath.strip().decode('utf-8') for xpath in f.readlines()]))

    # loading stop words
    if args.stopwords != None:
        with open(args.stopwords, 'r') as f:
            stop_words = [word.strip().decode('utf-8') for word in f.readlines()]

    # loading banned documents list
    if args.banned != None:
        with open(args.banned, 'r') as f:
            banned = [int(doc_id.strip()) for doc_id in f.readlines()]

    with open(args.endings, 'r') as f:
        endings = sorted([ending.strip().decode('utf-8') for ending in f.readlines()])

    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')

        if int(doc_id) in banned:
            continue

        html_text = zlib.decompress(base64.b64decode(html_b64encoded)).decode('utf-8')
        html_structure = lxml.html.document_fromstring(html_text)

        # deleteing unnecessary info, including title
        for xpath in xpaths:
            delete_by_xpath(html_structure, xpath)

        # code from comment https://sfera-mail.ru/blog/Find/611.html#comment2000
        html_structure = script_cleaner.clean_html(html_structure)
        text = " ".join(lxml.etree.XPath("//text()")(html_structure)).lower()
        # print lxml.html.tostring(html_structure).encode('utf-8')

        #words = [word for word in re.findall(SPLIT_RGX, text) if word not in stop_words]
        words = re.findall(SPLIT_RGX, text)

        stemmed_words = stemmer.stemWords(words)
        words_endings = [get_ending(words[i],stemmed_words[i]) for i in range(len(words))]
        words_endings_id = [endings.index(word_ending) for word_ending in words_endings]

        # term_to {term: [[list-of-positions],[list-of-endings-id]]}
        term_to = {}

        for i in range(len(words)):
            word = stemmed_words[i]
            # words[i], cause word might not to be stop word
            if words[i] in stop_words:
                continue
            elif word not in term_to:
                term_to[word] = [None, None]
                term_to[word][TO_POSITIONS] = [i]
                term_to[word][TO_ENDING_ID] = [words_endings_id[i]]
            else:
                term_to[word][TO_POSITIONS].append(i)
                term_to[word][TO_ENDING_ID].append(words_endings_id[i])

        # output format: <term><\tab><doc id><\tab><input count><\tab><comma separated input positions><\tab><comma separated endings id>
        for term in term_to.keys():
            positions = map(str, term_to[term][TO_POSITIONS])
            ending_ids = map(str, term_to[term][TO_ENDING_ID])
            print ('%s\t%s\t%d\t%s\t%s' % \
                (term, doc_id, len(positions), ','.join(positions), ','.join(ending_ids))).encode('utf-8')


def delete_by_xpath(content, xpath):
    for elem in content.xpath(xpath):
        elem.getparent().remove(elem)

if __name__ == '__main__':
    main()
