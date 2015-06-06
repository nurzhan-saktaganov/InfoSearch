#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import argparse
import math
import base64

__author__ = 'Nurzhan Saktaganov'

# docID_to
DOC_URL = 0
DOC_LENGTH = 1
DOC_READ_OFFSET = 2
DOC_READ_SIZE = 3
DOC_PAGERANK = 4
DOC_IMGS_URL_LIST = 5

# dictionary
DIC_READ_OFFSET = 0
DIC_READ_SIZE = 1
DIC_IDF = 2


normalize_url = lambda url: url[:-1] if url.count('/') > 3 and url.count('?') == 0 and url[-1] == '/' else url


# df - document frequency of term
# dc - total documents count
idf = lambda df, dc: math.log10(1.0 * dc / df)


# <output is {'dictionary': <dictionary>, 'docID_to: <docID_to>}'
# where
#   <dictionary> is {<term>: [read_offset, read_size, idf]}
#   <docID_to is> is {<doc_id>: [url, length, read_offset, read_size, pagerank, list-of-imgs-url]}


def get_args():
    # -i / --invert - <inverted index file>
    # -f / --forward - <forward index file>
    # -u / --urls - <file with urls>
    # * for future -p / --pageranks - <file with pageranks>
    # -o / --output - <output file>
    parser = argparse.ArgumentParser(\
        description='Prepare data', epilog='by ' + __author__)
    parser.add_argument('-i', '--inverted', help='inverted index file',\
        metavar='<inverted index file path>', dest='inverted', required=True, type=str)
    parser.add_argument('-f', '--forward', help='forward index file',\
        metavar='<forward index file path>', dest='forward', required=True, type=str)
    parser.add_argument('-u', '--urls', help='file with urls',\
        metavar='<urls file path>', dest='urls', required=True, type=str)
    parser.add_argument('-b', '--banned', help='file with documents not to index',\
        metavar='<banned documents file path>', dest='banned', required=False,type=str,default=None)
    # * for future
    #parser.add_argument('-p', '--pageranks', help='pageranks file',\
    #    metavar='<pageranks file path>', dest='pageranks', required=True, type=str)
    parser.add_argument('-o', '--output', help='output file',\
        metavar='<output file path>', dest='output', required=False, type=str, default='prepared.data')
    return parser.parse_args()


def main():
    args = get_args()

    docID_to = build_docID_to(urls_path=args.urls, forward_path=args.forward, banned_path=args.banned)
    dictionary = build_dictionary(inverted_path=args.inverted, documents_count=len(docID_to))

    prepared = {'docID_to': docID_to, 'dictionary': dictionary}

    with open(args.output, 'w') as f:
        pickle.dump(prepared, f)


def build_docID_to(urls_path, forward_path, banned_path):
    docID_to, banned = {}, []

    if banned_path != None:
        with open(banned_path, 'r') as f:
            banned = [int(doc_id.strip()) for doc_id in f.readlines()]

    # adding urls info
    with open(urls_path, 'r') as f:
        for line in f:
            doc_id, url = line.strip().split('\t')
            doc_id = int(doc_id)
            
            if doc_id in banned:
                continue

            # URL, LENGTH, READ OFFSET, READ SIZE, PAGERANK, IMGS_URL_LIST
            docID_to[doc_id] = [None, None, None, None, None, None]
            docID_to[doc_id][DOC_URL] = normalize_url(url)

    # adding info from forward index, banned doc ids are not present here
    with open(forward_path, 'r') as f:
        read_offset, line = 0, f.readline()
        while line:
            splitted_line = line.strip().split('\t')

            doc_id = int(splitted_line[0])
            doc_length = int(splitted_line[1])
            b64_list_of_imgs_url = splitted_line[3].split(',')

            docID_to[doc_id][DOC_LENGTH] = doc_length
            if b64_list_of_imgs_url[0] == '0':
                docID_to[doc_id][DOC_IMGS_URL_LIST] = []
            else:
                docID_to[doc_id][DOC_IMGS_URL_LIST] = \
                    map(lambda b64url: base64.b64decode(b64url), b64_list_of_imgs_url)

            docID_to[doc_id][DOC_READ_OFFSET] = read_offset

            read_size = len(line)
            docID_to[doc_id][DOC_READ_SIZE] = read_size
            read_offset += read_size

            line = f.readline()

    return docID_to


def build_dictionary(inverted_path, documents_count):
    dictionary = {}
    with open(inverted_path, 'r') as f:
        read_offset, line = 0, f.readline()
        while line:
            splitted_line = line.strip().split('\t')
            read_size = len(line)

            term = splitted_line[0].decode('utf-8')
            # df - document frequency
            df = int(splitted_line[1])

            term_idf = idf(df=df,dc=documents_count)

            dictionary[term] = [None, None, None]
            dictionary[term][DIC_READ_OFFSET] = read_offset
            dictionary[term][DIC_READ_SIZE] = read_size
            dictionary[term][DIC_IDF] = term_idf

            read_offset += read_size
            line = f.readline()

    return dictionary


if __name__ == '__main__':
    main()
