#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from DictionaryBuilder import DictionaryBuilder
import pickle
import argparse

__author__ = 'Nurzhan Saktaganov'

# -i / --index - <raw index file>
# -u / --urls - <file with urls>
# -l / --length - <file with length>
# -o / --output - <output file>

# <output is {'dictionary': {<dictionary>}, 'docID_to': {'url': <url>, 'length': <length>}} >
def get_args():
    parser = argparse.ArgumentParser(\
        description='Prepare data for searcher', epilog='by ' + __author__)
    parser.add_argument('-i','--index', help='raw index file',\
        dest='index', required=True, type=str)
    parser.add_argument('-u','--urls', help='file with urls',\
        dest='urls', required=True, type=str)
    parser.add_argument('-l','--length', help='file with length',\
        dest='length', required=True, type=str)
    parser.add_argument('-o','--output', help='output file',\
        dest='output', required=False, type=str, default='output.data')
    return parser.parse_args()
def main():
    args = get_args()

    dictionary = DictionaryBuilder.build(args.index)

    docID_to_url = {}
    with open(args.urls, 'r') as urls_file:
        for line in urls_file:
            doc_id, url = line.strip().split('\t')
            docID_to_url[int(doc_id)] = url

    docID_to_length = {}
    with open(args.length, 'r') as length_file:
        for line in length_file:
            doc_id, length = line.strip().split('\t')
            docID_to_length[int(doc_id)] = int(length)

    docID_to = {}
    for key in docID_to_url.keys():
        docID_to[key] = {'url': docID_to_url[key], 'length': docID_to_length[key]}

    result = {'dictionary': dictionary, 'docID_to': docID_to}

    with open(args.output, 'w') as output:
        pickle.dump(result, output)

if __name__ == '__main__':
    main()
