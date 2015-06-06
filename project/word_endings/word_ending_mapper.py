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

def get_args():
    # -x / --xpaths - <file with xpaths to delete>
    # -s / --stopwords - <file with stop words>
    # -b / --banned - <file with documents not to index>
    parser = argparse.ArgumentParser(\
        description='Word endings mapper', epilog='by ' + __author__)
    parser.add_argument('-x', '--xpaths', help='file with xpaths to delete',\
        metavar='<xpaths file path>', dest='xpaths', required=False,type=str, default=None)
    parser.add_argument('-s', '--stopwords', help='file with stop words',\
        metavar='<stop words file path>', dest='stopwords', required=False, type=str, default=None)
    parser.add_argument('-b', '--banned', help='file with documents not to index',\
        metavar='<banned documents file path>', dest='banned', required=False,type=str,default=None)
    return parser.parse_args()

get_ending = lambda word, stemmed_word: word[len(stemmed_word):]

def main():
    args = get_args()

    # hadoop cluster doesn't support the "kill_tags" argument
    script_cleaner = lxml.html.clean.Cleaner(scripts=True,javascript=True\
        ,comments=True,style=True,links=True,meta=False,remove_tags=['a', 'img']) #,kill_tags=['script','style'])

    stemmer = snowballstemmer.stemmer('russian')

    xpaths, stopwords, banned = [], [], []

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

    uniq_endings = {}

    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')

        if int(doc_id) in banned:
            continue

        html_text = zlib.decompress(base64.b64decode(html_b64encoded)).decode('utf-8')
        html_structure = lxml.html.document_fromstring(html_text)

        # deleteing unnecessary info, including title
        for xpath in xpaths:
            delete_by_xpath(html_structure, xpath)

        html_structure = script_cleaner.clean_html(html_structure)

        #print lxml.html.tostring(html_structure).encode('utf-8')
        #print ' '.join(stemmer.stemWords(lxml.html.tostring(html_structure).split())).encode('utf-8')
        text = " ".join(lxml.etree.XPath("//text()")(html_structure)).lower()
        #words = [word for word in re.findall(SPLIT_RGX, text) if word not in stop_words]
        words = re.findall(SPLIT_RGX, text)

        stemmed_words = stemmer.stemWords(words)

        for i in range(len(words)):
            ending = get_ending(words[i], stemmed_words[i])
            if ending not in uniq_endings:
                uniq_endings[ending] = 1

    print '\n'.join(uniq_endings.keys()).encode('utf-8')


def delete_by_xpath(content, xpath):
    for elem in content.xpath(xpath):
        elem.getparent().remove(elem)

if __name__ == '__main__':
    main()
