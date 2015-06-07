#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import argparse
import signal

import VarByte
import Simple9

# stemmer
import snowballstemmer

import heapq

import base64
import zlib

import CacheLRU

import re

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

# BM25
b = 0.75
k1 = 2.0

BM25 = lambda tf, idf, L: \
            tf * idf / (tf + k1 * (b + L * (1.0 - b)))

# PASSAGE
get_density = lambda _list: sum([1.0 / (_list[i + 1] - _list[i]) for i in range(len(_list) - 1)])

get_inversions = lambda _list: sum([1 for i in range(len(_list)) for j in range(i + 1, len(_list)) if _list[j] <= _list[i]])

# c_w - completeness weight
# dfb_w - distance from the beginning of the document weight
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

get_ending = lambda word, stemmed_word: word[len(stemmed_word):]


def get_args():
    # -p / --prepared - <prepared data file>
    # -i / --inverted - <inverted index file>
    # -f / --forward - <forward index file>
    # -c / --compress - <compressing algorithm, default='VarByte'>
    parser = argparse.ArgumentParser(\
        description='Blood Seeker SE', epilog='by ' + __author__)
    parser.add_argument('-p','--prepared',help='prepared data file',\
        metavar='<prepared file path>', dest='prepared', required=True, type=str)
    parser.add_argument('-i','--inverted', help='inverted index file',\
        metavar='<inverted index file path>', dest='inverted', required=True, type=str)
    parser.add_argument('-f', '--forward', help='forward index file',\
        metavar='<forward index file path>', dest='forward', required=True, type=str)
    parser.add_argument('-c', '--compress',help='compressing algorithm: default=VarByte',\
        dest='compress', required=False, default='VarByte', type=str, choices=['VarByte', 'Simple9'])
    return parser.parse_args()


def main():
    signal.signal(signal.SIGINT, good_bye)
    args = get_args()

    print 'Loading...'
    
    with open(args.prepared, 'r') as f:
        prepared = pickle.load(f)

    inverted = open(args.inverted, 'r')
    forward = open(args.forward, 'r')

    if args.compress == 'Simple9':
        decoder = Simple.Simple9
    else:
        decoder = VarByte.VarByte

    stemmer = snowballstemmer.stemmer('russian')

    cache = CacheLRU.CacheLRU(100)

    while True:
        sys.stdout.write('\nfind: ')
        try:
            request = raw_input().strip().decode('utf-8').lower()
            if request == '':
                continue
        except Exception, e:
            print e
            continue

        cache_key = request_to_cache_key(request, stemmer, prepared)

        if cache.has_key(cache_key):
            n_best = cache.get(cache_key)
        else:
            n_best = get_n_best(prepared, request, stemmer, inverted, decoder, n=100)

        if n_best == None:
            print 'No matches found!'
            continue

        cache.add(cache_key, n_best)
        
        # dpp - doc per page
        page = 0
        dpp = 10
        begin = page * dpp

        get_snippets(prepared, forward, decoder, documents=n_best[begin:begin + dpp], max_len=300)

        continue

# for get_snippets
SPLIT_RGX = re.compile('\w+', re.U)

def get_snippets(prepared, forward, decoder, documents, max_len):
    docID_to = prepared['docID_to']

    print documents

    for doc_id, passage_info in documents:
        forward.seek(docID_to[doc_id][DOC_READ_OFFSET])
        # cs - comma separated
        # b64 - base 64 encoded
        # gzip - gzipped
        # bp - begin positions
        _, _, b64_title, cs_b64_imgs_url, cs_b64_gzip_sentences, encoded_sentences_bp = \
            forward.read(docID_to[doc_id][DOC_READ_SIZE]).split('\t')

        title = base64.b64decode(b64_title).decode('utf-8')
        
        if cs_b64_imgs_url != '0':
            imgs_url = map(lambda b64url: base64.b64decode(b64url), cs_b64_imgs_url.split(','))
        else:
            imgs_url = []

        sentences = map(lambda s: zlib.decompress(base64.b64decode(s)).decode('utf-8'), cs_b64_gzip_sentences.split(','))
        sentences_bp = decoder.decode(encoded_sentences_bp, True)

        #print '\n'.join(sentences)
        #print sentences_bp
        #print title
        #print ' '.join(imgs_url)
        #print len(sentences)

        indices = []
        request_terms = {}
        max_idf = 0.0

        for term_position, term_idf in passage_info.iteritems():
            index = get_sentence_index(sentences_bp, term_position)
            if index not in indices:
                indices.append(index)
            term_position_in_sentence = term_position - sentences_bp[index]
            splitted_sentence = re.findall(SPLIT_RGX, sentences[index])
            current_term = splitted_sentence[term_position_in_sentence]
            request_terms[current_term] = term_idf
            if term_idf > max_idf:
                rarely_term = current_term

        raw_snippet = ' '.join([sentences[index] for index in indices])
        snippet_begin = max(0, raw_snippet.find(rarely_term) - max_len / 2)

        if snippet_begin > 0:
            while snippet_begin > 0 and raw_snippet[snippet_begin] != ' ':
                snippet_begin -= 1

        snippet = ''

        if snippet_begin > 0:
            snippet += '...'

        snippet += raw_snippet[snippet_begin: snippet_begin + max_len]

        if len(raw_snippet) > snippet_begin + max_len:
            snippet += '...'

        for request_term in request_terms.keys():
            snippet = snippet.replace(request_term, '<b>' + request_term + '</b>')

        print title
        print snippet.encode('utf-8')
            
        print '\n\n'

# for get_snippets()
def get_sentence_index(_list, elem):
    low, high = 0, len(_list)
    while low != high:
        mid = (low + high) / 2
        if _list[mid] <= elem:
            low = mid + 1
        else:
            high = mid

    return low - 1

request_to_cache_key = lambda request, stemmer, prepared : \
    ' '.join(\
        [stemmer.stemWord(term) \
        for term in request.split() \
            if term not in prepared['stop_words'] \
                and stemmer.stemWord(term) in prepared['dictionary']])


# for function get_best
### request_stemmed_term_to
RST_COUNT = 0
RST_IDF = 1

### documents_rank
DR_BM25 = 0
DR_PASSAGE = 1
DR_FINAL = 2
DR_TERMS = 3
DR_PASSAGE_INFO = 4
DR_TERM_POSITIONS = 0
DR_TERM_ENDINGS = 1

### sliding_window
SL_STEMMED_TERM = 0
SL_STEMMED_TERM_POSITION = 1

# returns {<doc id>: <best passage info>}
# where
# <best passage info> - {<term position>: <term idf>}
def get_n_best(prepared, request, stemmer, inverted, decoder, n):
    dictionary = prepared['dictionary']
    docID_to = prepared['docID_to']
    stop_words = prepared['stop_words']

    # filter request terms by deleting stop words
    request_terms = [term for term in request.split() \
                        if term not in stop_words \
                            and stemmer.stemWord(term) in dictionary]

    if len(request_terms) == 0:
        return None

    documents_rank, request_stemmed_term_to = {}, {}
    stemmed_request_terms = stemmer.stemWords(request_terms)
    request_terms_endings = [get_ending(request_terms[i], stemmed_request_terms[i]) \
                                    for i in range(len(request_terms))]

    for stemmed_term in stemmed_request_terms:
        if stemmed_term in request_stemmed_term_to:
            request_stemmed_term_to[stemmed_term][RST_COUNT] += 1
        else:
            request_stemmed_term_to[stemmed_term] = [None, None]
            request_stemmed_term_to[stemmed_term][RST_COUNT] = 1
            request_stemmed_term_to[stemmed_term][RST_IDF] = dictionary[stemmed_term][DIC_IDF]

    # BM25 ranking
    for stemmed_term in stemmed_request_terms:
        inverted.seek(dictionary[stemmed_term][DIC_READ_OFFSET])
        _, _, encoded_doc_ids, encoded_tfs, encoded_poisitions_list, encoded_endings_list = \
            inverted.read(dictionary[stemmed_term][DIC_READ_SIZE]).split('\t')

        idf = dictionary[stemmed_term][DIC_IDF]

        doc_ids = decoder.decode(encoded_doc_ids, from_diff=True)
        tfs = decoder.decode(encoded_tfs, from_diff=False)

        encoded_lists_of_positions = encoded_poisitions_list.split(',')
        encoded_lists_of_endings = encoded_endings_list.split(',')

        for i in range(len(doc_ids)):
            L = docID_to[doc_ids[i]][DOC_LENGTH]
            BM25_rank = BM25(tf=tfs[i], idf=idf, L=L)
            if doc_ids[i] not in documents_rank:
                # documents_rank {'doc_id': [BM25, PASSAGE, FINAL, {<term>: position-list}]}
                documents_rank[doc_ids[i]] = [0.0, 0.0, 0.0, \
                    {stemmed_term: [encoded_lists_of_positions[i], encoded_lists_of_endings[i]]}, None]
                documents_rank[doc_ids[i]][DR_BM25] = BM25_rank
            else:
                documents_rank[doc_ids[i]][DR_BM25] += BM25_rank
                documents_rank[doc_ids[i]][DR_TERMS][stemmed_term] = \
                    [encoded_lists_of_positions[i],encoded_lists_of_endings[i]]

    # get top n of BM25 
    #   by heapq.nlargest, cause O(k * log(n))
    #   where k - total elements count 
    nlargest = heapq.nlargest(n, documents_rank.iteritems(), key=lambda item: item[1][DR_BM25])
    
    # instead of deleteing, i think it's faster 
    #   create new documents_rank 
    documents_rank = {}
    for key, value in nlargest:
        documents_rank[key] = value

    # decode list of positions of each stemmed term in each document
    #   and decode list of endings of each stemmed term in each document
    for doc_id in documents_rank.keys():
        for stemmed_term in documents_rank[doc_id][DR_TERMS].keys():
            documents_rank[doc_id][DR_TERMS][stemmed_term][DR_TERM_POSITIONS] = \
                decoder.decode(documents_rank[doc_id][DR_TERMS][stemmed_term][DR_TERM_POSITIONS], True)
            documents_rank[doc_id][DR_TERMS][stemmed_term][DR_TERM_ENDINGS] = \
                decoder.decode(documents_rank[doc_id][DR_TERMS][stemmed_term][DR_TERM_ENDINGS], False)

    #print documents_rank
    sliding_window = [[stemmed_request_terms[i], None] for i in range(len(stemmed_request_terms))]

    # PASSAGE ranking
    for doc_id in documents_rank.keys():
        # reinit sliding window for this document
        for i in range(len(sliding_window)):
            sliding_window[i][SL_STEMMED_TERM_POSITION] = -1

        # just for the current document
        position_to_stemmed_term = {}
        position_to_ending = {}

        for stemmed_term in documents_rank[doc_id][DR_TERMS].keys():
            positions = documents_rank[doc_id][DR_TERMS][stemmed_term][DR_TERM_POSITIONS]
            endings = documents_rank[doc_id][DR_TERMS][stemmed_term][DR_TERM_ENDINGS]

            for i in range(len(positions)):
                position_to_stemmed_term[positions[i]] = stemmed_term
                position_to_ending[positions[i]] = endings[i]

        max_passage = 0.0

        # best passage info is dictionary
        # where key is position
        # value is idf of stemmed term in this position
        best_passage_info = {}

        for position in sorted(position_to_stemmed_term.keys()):
            # from last to first position
            for i in list(reversed(range(len(sliding_window)))):
                if sliding_window[i][SL_STEMMED_TERM] != position_to_stemmed_term[position]:
                    continue
                else:
                    sliding_window[i][SL_STEMMED_TERM_POSITION] = position
                    sliding_window_positions = \
                        [(lambda _list: _list[SL_STEMMED_TERM_POSITION])(elem) \
                                    for elem in sliding_window \
                                        if (lambda _list: _list[SL_STEMMED_TERM_POSITION])(elem) != -1]

                    completeness = 1.0 * len(sliding_window_positions) / len(sliding_window)
                    density = get_density(sorted(list(set(sliding_window_positions))))
                    inversions = get_inversions(sliding_window_positions)
                    distance_from_beginning = 1.0 - 1.0 * min(sliding_window_positions) / docID_to[doc_id][DOC_LENGTH]

                    # tf-idf of passage
                    passage_tfidf = 0.0
                    for current_position in sliding_window_positions:
                        current_stemmed_term = position_to_stemmed_term[current_position]
                        passage_tfidf += request_stemmed_term_to[current_stemmed_term][RST_IDF] \
                                            * request_stemmed_term_to[current_stemmed_term][RST_COUNT]

                    current_passage = c_w * completeness + d_w * density + wo_w * 1.0 / (inversions + 1) \
                            + tfidf_w * passage_tfidf + dfb_w * distance_from_beginning

                    if current_passage > max_passage:
                        max_passage = current_passage
                        best_passage_info = {}
                        for current_position in sliding_window_positions:
                            current_stemmed_term = position_to_stemmed_term[current_position]
                            current_stemmed_term_idf = dictionary[current_stemmed_term][DIC_IDF]
                            best_passage_info[current_position] = current_stemmed_term_idf                            

                    

        documents_rank[doc_id][DR_PASSAGE] = max_passage
        documents_rank[doc_id][DR_PASSAGE_INFO] = best_passage_info

    # PASSAGE ranking end

    for doc_id in documents_rank.keys():
        documents_rank[doc_id][DR_FINAL] = \
            W_bm25 * documents_rank[doc_id][DR_BM25] + W_p * documents_rank[doc_id][DR_PASSAGE]

    final_ranking = sorted([(doc_id, documents_rank[doc_id][DR_FINAL]) for doc_id in documents_rank.keys()], \
                    key=lambda value: value[1], reverse=True)

    n_best = [[doc_id, documents_rank[doc_id][DR_PASSAGE_INFO]] for doc_id, rank in final_ranking]

    for doc_id, rank in final_ranking:
        print docID_to[doc_id][DOC_URL]

    return n_best


def good_bye(signal,frame):
    print '\nSee You!'
    exit()

if __name__ == '__main__':
    main()
