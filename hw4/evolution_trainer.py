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

import time
import Genetic

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

# term_to 
TO_IDF = 0
TO_COUNT = 1

# sliding_window 
SL_TERM = 0
SL_POSITION = 1

TOP_N = 100
# BM25
b = 0.75
k1 = 2.0

# PASSAGE
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

# df - document frequency, dc - document count
_idf = lambda df, dc:  math.log10(1.0 * dc / df)

_BM25 = lambda tf, idf, L, k1, b: \
    tf * idf / (tf + k1 * (b + L * (1.0 - b)))

_density = lambda _list: sum([1.0 / (_list[i + 1] - _list[i]) for i in range(len(_list) - 1)])

_inversions = lambda _list: sum([1 for i in range(len(_list)) for j in range(i + 1, len(_list)) if _list[j] <= _list[i]])

# -p / --prepared - <prepared data file, output of prepare_data.py>
# -i / --invert - <inverted index file>
# -o / --output - <output file>
# -f / --forward - <forward index file>
# -c / --compress - <compressing algorithm, default='VarByte'>
# -m / --marks - <assesors' marks>
# -s / --settings - <file with settings>


def get_args():
    parser = argparse.ArgumentParser(\
        description='Blood Seeker searcher with ranks', epilog='by ' + __author__)
    parser.add_argument('-p','--prepared',help='prepared data file, output of prepare_data.py',\
        metavar='<prepared file path>', dest='prepared', required=True, type=str)
    parser.add_argument('-i','--invert', help='inverted index file, output of mapper.py',
        metavar='<inverted index file path>', dest='invert', required=True, type=str)
    parser.add_argument('-m','--marks', help='assessors\' marks',\
        metavar='<file with marks>', dest='marks', required=True, type=str)
    parser.add_argument('-f','--forward', help='forward index file, output of forward_mapper.py',\
        metavar='<forward index file path>', dest='forward', required=True, type=str)
    parser.add_argument('-o','--output', help='best results of params evolution algorithm after each step',\
        metavar='<output path>', dest='output', required=False, default='output.evolution', type=str)
    parser.add_argument('-s', '--settings', help='file with settings',\
        metavar='<settings file path>', dest='settings',required=False,default=None,type=str)
    parser.add_argument('-c', '--compress',help='compressing algorithm: default=VarByte',\
        dest='compress', required=False, default='VarByte', type=str, choices=['VarByte', 'Simple9'])
    return parser.parse_args()

def get_settings(settings_file):
    integer_params = ['MAX_GENERATIONS', 'POPULATION_SIZE', 'CHILDREN_COUNT']
    float_params = ['MUTATION_POSSIBILITY']
    # default parameters
    settings = {'MAX_GENERATIONS': 1000, 'POPULATION_SIZE': 20, 'CHILDREN_COUNT': 20, 'MUTATION_POSSIBILITY': 0.03}

    if settings_file == None:
        return settings

    with open(settings_file, 'r') as f:
        for line in f:
            parameter, value = line.strip().split(' ')
            if parameter in integer_params:
                settings[parameter] = int(value)
            elif parameter in float_params:
                settings[parameter] = float(value)
    return settings

def main():
    signal.signal(signal.SIGINT, good_bye)
    args = get_args()
    settings = get_settings(args.settings)
    
    print 'Loading...'
    with open(args.prepared) as f:
        prepared = pickle.load(f)

    with open(args.marks, 'r') as f:
        marks = {}
        for line in f:
            request, url = line.decode('utf-8').strip().split('\t')
            marks[request.lower()] = url

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

    genetic = Genetic.Genetic(settings, args.output)
    genetic.init_population()

    print 'all marks: ' + str(len(marks.keys()))

    for generation in range(settings['MAX_GENERATIONS']):
        if generation > 0:
            #print fitness
            genetic.set_fitness(fitness)
            genetic.print_best()
            genetic.crossing()
            genetic.mutation()
            genetic.selection()
            population = genetic.get_population()
            print 'previous iteration time: ' + str(time.clock() - begin)
            begin = time.clock()
            if generation == 1:
                print 'Marks after 1st iter: ' + str(len(marks.keys()))

        else:
            begin = time.clock()
            population = genetic.get_population()
            documents_rank = {}
            term_to = {}

        fitness = [0.0] * len(population)
        print 'Iteration %d/%d (%.2f%%)' % (generation + 1, settings['MAX_GENERATIONS'], 100.0 * generation / settings['MAX_GENERATIONS'])
        #for species in population:
        #    c_w, dfb_w, d_w, tfidf_w, wo_w = species

        #    species_fitness = 0.0

        for request in marks.keys():
            #print request

            # filtered list of terms from request
            request_terms = [term for term in request.split(' ') if term != '' and term in dictionary]

            if len(request_terms) == 0:
                #print 'No matches there!'
                # delete, because bad request
                del marks[request]
                continue

            if generation == 0:
                # documents_rank 'request': {'doc_id': [BM25, PASSAGE[1..POP_SIZE], FINAL[1..POP_SIZE], {<term>: position-list}]}
                documents_rank[request] = {}

                term_to[request] = {}
                for term in request_terms:
                    if term in term_to[request]:
                        term_to[request][term][TO_COUNT] += 1
                    else:
                        term_to[request][term] = [None, None]
                        term_to[request][term][TO_COUNT] = 1

            # BM25 ranking
            #begin = time.clock()
            if generation == 0:
                for term in request_terms:
                    inverted.seek(dictionary[term][DIC_OFFSET])
                    t, df, encoded_doc_ids, encoded_tfs, encoded_positions_lists = \
                        inverted.read(dictionary[term][DIC_SIZE]).split('\t')

                    # document frequency of term
                    # so, we can set df = dicitionary[term][DIC_DOCUMENT_FREQUENCY],
                    # but i think, df = int(df) is faster
                    df = int(df)
                    idf = _idf(df=df, dc=dc)
                    term_to[request][term][TO_IDF] = idf

                    doc_ids = decoder.decode(encoded_doc_ids, from_diff=True)
                    tfs = decoder.decode(encoded_tfs, from_diff=False)
                    #lists_of_positions = [decoder.decode(encoded_positions_list, from_diff=True)\
                    #                for encoded_positions_list in encoded_positions_lists.split(',')]
                    encoded_lists_of_positions = encoded_positions_lists.split(',')

                    for i in range(len(doc_ids)):
                        L = docID_to[doc_ids[i]][DOC_LENGTH]
                        rank_BM25 = _BM25(tf=tfs[i],idf=idf,L=L,k1=k1,b=b)
                        if doc_ids[i] not in documents_rank[request]:
                            documents_rank[request][doc_ids[i]] = [0.0, [0.0] * len(population), [0.0] * len(population), {term: encoded_lists_of_positions[i]}]
                            documents_rank[request][doc_ids[i]][BM25] = rank_BM25
                        else:
                            documents_rank[request][doc_ids[i]][BM25] += rank_BM25
                            documents_rank[request][doc_ids[i]][TERMS][term] = encoded_lists_of_positions[i]

                #print 'BM25: ' + str(time.clock() - begin)
                # here we can assess boolean retrieval sorting by doc_id

                # get TOP_N of BM25
                #begin = time.clock()
                #border = sorted(list(set([document_rank[BM25] for document_rank in documents_rank.values()])), reverse=True)[:TOP_N][-1]
                border = sorted(list(set([documents_rank[request][doc_id][BM25] for doc_id in documents_rank[request].keys()])), reverse=True)[:TOP_N][-1]

                for doc_id in documents_rank[request].keys():
                    if documents_rank[request][doc_id][BM25] < border:
                        del documents_rank[request][doc_id]

                #print 'del: ' + str(time.clock() - begin)
                # here we can assess pure bm25 ranking sorting by BM25 value
                # passage algorithm
                # TODO
                # sliding_window : {term: pos | -1}
                #begin = time.clock()

                # decode list of positions each term in each document
                for doc_id in documents_rank[request].keys():
                    for term in documents_rank[request][doc_id][TERMS].keys():
                        documents_rank[request][doc_id][TERMS][term] = decoder.decode(documents_rank[request][doc_id][TERMS][term], from_diff=True)
                #print 'decode: ' + str(time.clock() - begin)


            #begin = time.clock()

            sliding_window = [[request_terms[i], None ] for i in range(len(request_terms))]
            # PASSAGE REGION
            for doc_id in documents_rank[request].keys():
                # reinit sliding window for this document
                for i in range(len(sliding_window)):
                    sliding_window[i][SL_POSITION] = -1

                # just for current document
                position_to_term = {}
                for term, positions in documents_rank[request][doc_id][TERMS].iteritems():
                    for position in positions:
                        position_to_term[position] = term

                max_passage = [0.0] * len(population)

                for position in sorted(position_to_term.keys()):
                    for i in list(reversed(range(len(sliding_window)))):
                        if sliding_window[i][SL_TERM] != position_to_term[position]:
                            continue
                        else:
                            sliding_window[i][SL_POSITION] = position
                            sliding_window_positions = [(lambda _list: _list[SL_POSITION])(elem) for elem in sliding_window \
                                                            if (lambda _list: _list[SL_POSITION])(elem) != -1]

                            completeness = 1.0 * len(sliding_window_positions) / len(sliding_window)
                            density = _density(_list=sorted(list(set(sliding_window_positions))))
                            inversions = _inversions(_list=sliding_window_positions)
                            distance_from_beginning = 1.0 - 1.0 * min(sliding_window_positions) / docID_to[doc_id][DOC_LENGTH]

                            # tf-idf of passage
                            passage_tfidf = 0.0
                            for current_position in sliding_window_positions:
                                current_term = position_to_term[current_position]
                                passage_tfidf += term_to[request][current_term][TO_IDF] * term_to[request][current_term][TO_COUNT]

                            current_passage = [0.0] * len(population)

                            for k in range(len(population)):
                                c_w, dfb_w, d_w, tfidf_w, wo_w = population[k]

                                current_passage[k] = c_w * completeness + d_w * density + wo_w * 1.0 / (inversions + 1) \
                                            + tfidf_w * passage_tfidf + dfb_w * distance_from_beginning

                                max_passage[k] = max(max_passage[k], current_passage[k])

                documents_rank[request][doc_id][PASSAGE] = max_passage[:]

                #print output
            #print 'PASSGE: ' + str(time.clock() - begin)
            # here we can assess final ranking sorting by final rank 

            #print documents_rank
            #begin = time.clock()
            for doc_id in documents_rank[request].keys():
                for i in range(len(population)):
                    documents_rank[request][doc_id][FINAL][i] = \
                            W_bm25 * documents_rank[request][doc_id][BM25] + W_p * documents_rank[request][doc_id][PASSAGE][i]
            #print 'calculate final rank: ' + str(time.clock() - begin)

            #begin = time.clock()
            #final_ranking = sorted([(doc_id, documents_rank[doc_id][FINAL]) for doc_id in documents_rank.keys()],\
            #                        key=lambda value: value[1], reverse=True)
            #print 'sort: ' + str(time.clock() - begin)

            #begin = time.clock()
            #for doc_id, rank in final_ranking:
            #    print docID_to[doc_id][DOC_URL]
            #print 'print: ' + str(time.clock() - begin)
            exception_flag = False
            for i in range(len(population)):

                final_ranking = sorted([(doc_id, documents_rank[request][doc_id][FINAL][i]) for doc_id in documents_rank[request].keys()],\
                                    key=lambda value: value[1], reverse=True)

                final_result = [docID_to[doc_id][DOC_URL] for doc_id, rank in final_ranking]
                
                try:
                    document_position = final_result.index(marks[request]) + 1
                    fitness[i] += 1.0 / document_position
                except Exception, e:
                    exception_flag = True

            if exception_flag:
                del marks[request]
                del documents_rank[request]
                #print 'Request has removed'

        #fitness.append(species_fitness)

    #print 'Marks after training: ' + str(len(marks.keys()))


def good_bye(signal,frame):
    print '\nSee You!'
    exit()

if __name__ == '__main__':
    main()
