#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import argparse

import VarByte
import Simple9

import math

import base64

import time

__author__ = 'Nurzhan Saktaganov'

# Global constants
TOP_N = 100

#docID_to
DOC_URL = 0
DOC_LENGTH = 1

# documents_rank
BM25 = 0
PASSAGE = 1
FINAL = 2
TERMS = 3

# dictionary
DIC_OFFSET = 0
DIC_SIZE = 1

# BM25
b = 0.75
k1 = 2.0


# df - document frequency, dc - document count
_idf = lambda df, dc:  math.log10(1.0 * dc / df)


_BM25 = lambda tf, idf, L, k1, b: \
    tf * idf / (tf + k1 * (b + L * (1.0 - b)))

def get_args():
    parser = argparse.ArgumentParser(\
        description='Prepare evolution trainer', epilog='by ' + __author__)
    parser.add_argument('-p','--prepared',help='prepared data file, output of prepare_data.py',\
        metavar='<prepared file path>', dest='prepared', required=True, type=str)
    parser.add_argument('-i','--invert', help='inverted index file, output of mapper.py',
        metavar='<inverted index file path>', dest='invert', required=True, type=str)
    parser.add_argument('-m','--marks', help='assessors\' marks',\
        metavar='<file with marks>', dest='marks', required=True, type=str)
    parser.add_argument('-o','--output', help='best results of params evolution algorithm after each step',\
        metavar='<output path>', dest='output', required=False, default='output.evolution', type=str)
    parser.add_argument('-c', '--compress',help='compressing algorithm: default=VarByte',\
        dest='compress', required=False, default='VarByte', type=str, choices=['VarByte', 'Simple9'])
    return parser.parse_args()



def main():
    args = get_args()

    with open(args.prepared, 'r') as f:
        print 'Loading \"%s\"...'  % (args.prepared, )
        prepared = pickle.load(f)

    with open(args.marks, 'r') as f:
        # marks is list of [request, url]
        marks = [line.decode('utf-8').strip().split('\t') for line in f]
        print 'Total marks count: %d' % (len(marks), )

    dictionary = prepared['dictionary']
    docID_to = prepared['docID_to']

    inverted = open(args.invert, 'r')

    if args.compress == 'Simple9':
        decoder = Simple9.Simple9
    else:
        decoder = VarByte.VarByte

    dc = len(docID_to.keys())

    # request_to[request_id] = [list-of-doc-id, list-of-bm25, list-of-terms, best-url-from-marks]
    LIST_OF_DOC_ID = 0
    LIST_OF_BM25 = 1
    LIST_OF_TERMS = 2
    BEST_URL = 3
    request_to = {}
    term_to_idf = {}
    doc_id_to_url = {}
    doc_id_to_length = {}
    doc_id_to_terms = {}

    begin = time.clock()
    for i in range(len(marks)):
        sys.stdout.write(str(i + 1) + '/' + str(len(marks)) + '\r')
        request, url = marks[i]

        request_to[i] = [None, None, None, None]
        request_to[i][BEST_URL] = url
        request_to[i][LIST_OF_TERMS] = [term for term in request.split(' ') if term != '' and term in dictionary]

        if len(request_to[i][LIST_OF_TERMS]) == 0:
            del request_to[i]
            continue

        # bm25 calculate
        documents_rank = {}

        for term in request_to[i][LIST_OF_TERMS]:
            inverted.seek(dictionary[term][DIC_OFFSET])
            t, df, encoded_doc_ids, encoded_tfs, encoded_positions_lists = \
                inverted.read(dictionary[term][DIC_SIZE]).split('\t')

            df = int(df)
            idf = _idf(df=df, dc=dc)
            term_to_idf[term] = idf

            doc_ids = decoder.decode(encoded_doc_ids, from_diff=True)
            tfs = decoder.decode(encoded_tfs, from_diff=False)
            #lists_of_positions = [decoder.decode(encoded_positions_list, from_diff=True)\
            #                for encoded_positions_list in encoded_positions_lists.split(',')]
            encoded_lists_of_positions = encoded_positions_lists.split(',')

            for j in range(len(doc_ids)):
                L = docID_to[doc_ids[j]][DOC_LENGTH]
                rank_BM25 = _BM25(tf=tfs[j],idf=idf,L=L,k1=k1,b=b)
                if doc_ids[j] not in documents_rank:
                    documents_rank[doc_ids[j]] = [0.0, 0.0, 0.0, {term: encoded_lists_of_positions[j]}]
                    documents_rank[doc_ids[j]][BM25] = rank_BM25
                else:
                    documents_rank[doc_ids[j]][BM25] += rank_BM25
                    documents_rank[doc_ids[j]][TERMS][term] = encoded_lists_of_positions[j]

        border = sorted(list(set([document_rank[BM25] for document_rank in documents_rank.values()])), reverse=True)[:TOP_N][-1]

        for doc_id in documents_rank.keys():
            if documents_rank[doc_id][BM25] < border:
                del documents_rank[doc_id]

        urls = [(lambda doc_id: docID_to[doc_id][DOC_URL])(doc_id) for doc_id in documents_rank.keys()]

        if request_to[i][BEST_URL] not in urls:
            del request_to[i]
            continue


        request_to[i][LIST_OF_DOC_ID] = documents_rank.keys()
        request_to[i][LIST_OF_BM25] = [documents_rank[doc_id][BM25] for doc_id in request_to[i][LIST_OF_DOC_ID]]

        for doc_id in documents_rank.keys():
            if doc_id in doc_id_to_url:
                continue
            doc_id_to_url[doc_id] = docID_to[doc_id][DOC_URL]
            doc_id_to_length[doc_id] = docID_to[doc_id][DOC_LENGTH]
            doc_id_to_terms[doc_id] = {}
            for term in documents_rank[doc_id][TERMS].keys():
                doc_id_to_terms[doc_id][term] = decoder.decode(documents_rank[doc_id][TERMS][term], from_diff=True)


    print 'Total requests count: %d, time: %f' % (len(request_to.keys()), time.clock() - begin)

    output = {'request_to': request_to, 'term_to_idf': term_to_idf, 'doc_id_to_url': doc_id_to_url, \
            'doc_id_to_length': doc_id_to_length, 'doc_id_to_terms': doc_id_to_terms}

    with open(args.output, 'w') as f:
        pickle.dump(output, f)


if __name__ == '__main__':
    main()
