#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import argparse
import signal

import VarByte
import Simple9

import math

__author__ = 'Nurzhan Saktaganov'

# dictionary
OFFSET = 0
SIZE = 1

#docID_to
DOC_URL = 0
DOC_LENGTH = 1

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
tfifd_w = 1.0
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

# -p / --prepared - <prepared data file, output of prepare_data.py>
# -i / --index - <raw index file>
# -e / --estimates - <output of evolution trainer>
# -d / --direct - <direct index file>
# -c / --compress - <compressing algorithm, default='VarByte'>

def get_args():
    parser = argparse.ArgumentParser(\
        description='Blood Seeker searcher with ranks', epilog='by ' + __author__)
    parser.add_argument('-p','--prepared',\
        help='prepared data file, output of prepare_data.py',metavar='<prepared file path>',\
        dest='prepared', required=True, type=str)
    parser.add_argument('-i','--index', help='raw index file',metavar='<index file path>',\
        dest='index', required=True, type=str)
    parser.add_argument('-e','--estimates', help='output of evolution_trainer.py',\
        dest='estimates', required=True, type=str,metavar='<estimates file path>')
    #parser.add_argument('-d','--direct', help='direct index, output of doc_len_and_direct_index.py',\
    #    dest='direct', required=True, type=str, metavar='<direct index file path>')
    parser.add_argument('-c', '--compress',\
        help='compressing algorithm: default=VarByte',\
        dest='compress', required=False, default='VarByte', type=str,\
        choices=['VarByte', 'Simple9'])
    return parser.parse_args()

def main():
    signal.signal(signal.SIGINT, good_bye)
    args = get_args()
    
    with open(args.prepared) as f:
        prepared = pickle.load(f)

    dictionary = prepared['dictionary']
    docID_to = prepared['docID_to']

    index = open(args.index, 'r')
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

        terms = [term for term in request.split(' ') if term != '' ]

        # documents_rank {'doc_id':[BM25, PASSAGE, {<term>: positions}}}
        # upd 1. documents_rank {'doc_id': [BM25, PASSAGE, FINAL, {<term>: position-list}]}
        documents_rank = {}

        # BM25 ranking
        for term in terms:
            if term not in dictionary:
                continue
            index.seek(dictionary[term][OFFSET])
            t, df, encoded_doc_ids, encoded_tfs, encoded_positions_lists = \
                index.read(dictionary[term][SIZE]).split('\t')

            # document frequency of term
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
                    documents_rank[doc_ids[i]] = [rank_BM25, 0.0, 0.0, {term:lists_of_positions[i]}]
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

            for position in sorted(position_to_term.keys()):
                term = position_to_term[position]
                sliding_window[term] = position
                sliding_window_positions = [pos for pos in sliding_window.values() if pos != -1]
                print sliding_window # delete
                print sliding_window_positions

                completeness = 1.0 * len(sliding_window_positions) / len(sliding_window)
                density = _density(_list=sorted(sliding_window_positions))
                inversions = _inversions(_list=sliding_window_positions)

                print inversions
                print completeness
                print density

                current_passage = c_w * completeness + d_w * density + wo_w * 1.0 / (inversions + 1)
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