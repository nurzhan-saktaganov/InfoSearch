#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from DictionaryBuilder import DictionaryBuilder
import pickle
import argparse

__author__ = 'Nurzhan Saktaganov'

#---------------------------------
# -i / --invert - <inverted index file>
# -u / --urls - <file with urls>
# -o / --output - <output file>
# -f / --forward - <forward index file>

# <output is {'dictionary': <dictionary>, 'docID_to: <docID_to>}'
# where:
#   <dictionary> is {<term>: [offset, size]}
#   <docID_to is> is {<doc_id>: [url, length, offset, size]}

URL = 0
LENGTH = 1
OFFSET = 2
SIZE = 3

normalize = lambda url: url[:-1] if url.count('/') > 3 and url.count('?') == 0 and url[-1] == '/' else url

def get_args():
    parser = argparse.ArgumentParser(\
        description='Prepare data for searcher', epilog='by ' + __author__)
    parser.add_argument('-i','--invert', help='inverted index file, output of reducer.py',\
        metavar='<inverted index file path>', dest='invert', required=True, type=str)
    parser.add_argument('-u','--urls', help='file with urls',metavar='<urls file path>',\
        dest='urls', required=True, type=str)
    parser.add_argument('-f','--forward', help='forward index file, output of forward_mapper.py',\
        metavar='<forward index file path>',dest='forward', required=True, type=str)
    parser.add_argument('-o','--output', help='output file',metavar='<output file path>',\
        dest='output', required=False, type=str, default='output.data')
    return parser.parse_args()

def main():
    args = get_args()

    dictionary = DictionaryBuilder.build(args.invert)
    docID_to = {}

    with open(args.urls, 'r') as f:
        for line in f:
            doc_id, url = line.strip().split('\t')
            # TODO normalize url
            docID_to[int(doc_id)] = [None, None, None, None]
            docID_to[int(doc_id)][URL] = normalize(url)

    with open(args.forward, 'r') as f:
        offset, line = 0, f.readline()
        while line:
            doc_id, length, encoded_text = line.strip().split('\t')

            doc_id = int(doc_id)
            docID_to[doc_id][LENGTH] = int(length)
            docID_to[doc_id][OFFSET] = offset

            size = len(line)
            docID_to[doc_id][SIZE] = size
            offset += size
            
            line = f.readline()

    result = {'dictionary': dictionary, 'docID_to': docID_to}

    with open(args.output, 'w') as output:
        pickle.dump(result, output)

if __name__ == '__main__':
    main()
