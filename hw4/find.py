#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import argparse
import signal

import VarByte
import Simple9

import math

import base64
import zlib

from collections import Counter

__author__ = 'Nurzhan Saktaganov'

# dictionary
DIC_OFFSET = 0
DIC_SIZE = 1
DIC_DOCUMENT_FREQUENCY = 2

#docID_to
DOC_URL = 0
DOC_LENGTH = 1
DOC_OFFSET = 2
DOC_SIZE = 3

# documents_rank
BM25 = 0
PASSAGE = 1
FINAL = 2
TERMS = 3

TOP_N = 10

# BM25
b = 0.75
k1 = 2.0

# PASSAGE
# c_w - completeness weight
# dfb_w - distance from begining of the document weight
# d_w - density weight
# tfidf_w - tf-idf weight
# wo_w - word order weight
c_w = 1.0
dfb_w = 1.0
d_w = 1.0
tfidf_w = 1.0
wo_w = 1.0

# Final 
# W_bm25 - weight of BM25
# W_p - weight of best passage
W_bm25 = 1.0
W_p = 1.0

# df - document frequency, dc - document count
_idf = lambda df, dc:  math.log10(1.0 * dc / df)

_BM25 = lambda tf, idf, L, k1, b: \
    tf * idf / (tf + k1 * (b + L * (1.0 - b)))

_density = lambda _list: sum([1.0 / (_list[i + 1] - _list[i]) for i in range(len(_list) - 1)])

_inversions = lambda _list: sum([1 for i in range(len(_list)) for j in range(i + 1, len(_list)) if _list[j] < _list[i]])

def _passage_tfidf(doc_id, forward_index, dictionary, docID_to, positions, dc, text):
    begin = min(positions)
    end = max(positions)

    passage = text[begin: end + 1]
    terms_dictionary = Counter(passage)

    tfidf = 0.0
    for term in terms_dictionary.keys():
        df = dictionary[term][DIC_DOCUMENT_FREQUENCY]
        # tf is term frequency in passage
        tf = terms_dictionary[term]
        tfidf += tf * _idf(df=df,dc=dc)
    return tfidf

# -p / --prepared - <prepared data file, output of prepare_data.py>
# -i / --invert - <inverted index file>
# -e / --estimates - <output of evolution_trainer.py>
# -f / --forward - <forward index file>
# -c / --compress - <compressing algorithm, default='VarByte'>


def get_args():
    parser = argparse.ArgumentParser(\
        description='Blood Seeker searcher with ranks', epilog='by ' + __author__)
    parser.add_argument('-p','--prepared',help='prepared data file, output of prepare_data.py',\
        metavar='<prepared file path>', dest='prepared', required=True, type=str)
    parser.add_argument('-i','--invert', help='inverted index file, output of mapper.py',
        metavar='<inverted index file path>', dest='invert', required=True, type=str)
    parser.add_argument('-e','--estimates', help='estimates file, output of evolution_trainer.py',\
        metavar='<estimates file path>', dest='estimates', required=True, type=str)
    parser.add_argument('-f','--forward', help='forward index file, output of forward_mapper.py',\
        metavar='<forward index file path>', dest='forward', required=True, type=str)
    parser.add_argument('-c', '--compress',help='compressing algorithm: default=VarByte',\
        dest='compress', required=False, default='VarByte', type=str, choices=['VarByte', 'Simple9'])
    return parser.parse_args()

def main():
    signal.signal(signal.SIGINT, good_bye)
    args = get_args()
    
    print 'Loading...'
    with open(args.prepared) as f:
        prepared = pickle.load(f)

    dictionary = prepared['dictionary']
    docID_to = prepared['docID_to']

    inverted = open(args.invert, 'r')
    forward = open(args.forward, 'r')
    #estimates = open(args.estimates, 'r')

    if args.compress == 'Simple9':
        decoder = Simple9.Simple9
    else:
        decoder = VarByte.VarByte

    # documents count
    dc = len(docID_to.keys())

    while True:
        sys.stdout.write('\nfind: ')
        try:
            request = raw_input().decode('utf-8').strip().lower()
            if  request == '':
                continue
        except Exception, e:
            print e
            continue

        # list of terms from request
        terms = [term for term in request.split(' ') if term != '' ]

        # documents_rank {'doc_id': [BM25, PASSAGE, FINAL, {<term>: position-list}]}
        documents_rank = {}

        # BM25 ranking
        for term in terms:
            if term not in dictionary:
                continue
            inverted.seek(dictionary[term][DIC_OFFSET])
            t, df, encoded_doc_ids, encoded_tfs, encoded_positions_lists = \
                inverted.read(dictionary[term][DIC_SIZE]).split('\t')

            # document frequency of term
            # so, we can set df = dicitionary[term][DIC_DOCUMENT_FREQUENCY],
            # but i think, df = int(df) is faster
            df = int(df)
            idf = _idf(df=df, dc=dc)

            doc_ids = decoder.decode(encoded_doc_ids, from_diff=True)
            tfs = decoder.decode(encoded_tfs, from_diff=False)
            lists_of_positions = [decoder.decode(encoded_positions_list, from_diff=True)\
                            for encoded_positions_list in encoded_positions_lists.split(',')]

            for i in range(len(doc_ids)):
                L = docID_to[doc_ids[i]][DOC_LENGTH]
                rank_BM25 = _BM25(tf=tfs[i],idf=idf,L=L,k1=k1,b=b)
                if doc_ids[i] not in documents_rank:
                    documents_rank[doc_ids[i]] = [0.0, 0.0, 0.0, {term:lists_of_positions[i]}]
                    documents_rank[doc_ids[i]][BM25] = rank_BM25
                else:
                    documents_rank[doc_ids[i]][BM25] += rank_BM25
                    documents_rank[doc_ids[i]][TERMS][term] = lists_of_positions[i]

        if len(documents_rank) == 0:
            print 'No matches!'
            continue

        # here we can assess boolean retrieval sorting by doc_id

        # get TOP_N of BM25
        border = sorted(list(set([document_rank[BM25] for document_rank in documents_rank.values()])), reverse=True)[:TOP_N][-1]

        for doc_id in documents_rank.keys():
            if documents_rank[doc_id][BM25] < border:
                del documents_rank[doc_id]

        # here we can assess pure bm25 ranking sorting by BM25 value

        # passage algorithm
        # TODO
        # sliding_window : {term: pos | -1}
        for doc_id in documents_rank.keys():
            sliding_window = {}
            for term in terms:
                sliding_window[term] = -1
            # sliding_window {term: position}
            print sliding_window # delete

            position_to_term = {}
            for term, positions in documents_rank[doc_id][TERMS].iteritems():
                for position in positions:
                    position_to_term[position] = term

            max_passage = 0.0

            forward.seek(docID_to[doc_id][DOC_OFFSET])
            text = zlib.decompress(base64.b64decode(forward.read(docID_to[doc_id][DOC_SIZE]).strip().split('\t')[2])).decode('utf-8').split(' ')

            for position in sorted(position_to_term.keys()):
                term = position_to_term[position]
                sliding_window[term] = position
                sliding_window_positions = [pos for pos in sliding_window.values() if pos != -1]
                print sliding_window # delete
                print sliding_window_positions

                completeness = 1.0 * len(sliding_window_positions) / len(sliding_window)
                density = _density(_list=sorted(sliding_window_positions))
                inversions = _inversions(_list=sliding_window_positions)

                passage_tfidf = _passage_tfidf(doc_id=doc_id,forward_index=forward,dictionary=dictionary,\
                    docID_to=docID_to,positions=sliding_window_positions,dc=dc, text=text)

                print inversions
                print completeness
                print density

                current_passage = c_w * completeness + d_w * density + wo_w * 1.0 / (inversions + 1) + tfidf_w * passage_tfidf
                max_passage = max(max_passage, current_passage)

            documents_rank[doc_id][PASSAGE] = max_passage

            #print output

        # here we can assess final ranking sorting by final rank 

        #print documents_rank
        for doc_id in documents_rank.keys():
            documents_rank[doc_id][FINAL] = \
                    W_bm25 * documents_rank[doc_id][BM25] + W_p * documents_rank[doc_id][PASSAGE]

        final_ranking = sorted([(doc_id, documents_rank[doc_id][FINAL]) for doc_id in documents_rank.keys()],\
                                key=lambda value: value[1], reverse=True)
        print final_ranking


def good_bye(signal,frame):
    print '\nSee You!'
    exit()

if __name__ == '__main__':
    main()
