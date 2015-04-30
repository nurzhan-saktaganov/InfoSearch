#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import argparse
import signal

import time
import Genetic

__author__ = 'Nurzhan Saktaganov'

# request_to
LIST_OF_DOC_ID = 0
LIST_OF_BM25 = 1
LIST_OF_TERMS = 2
BEST_URL = 3

# sliding_window 
SL_TERM = 0
SL_POSITION = 1

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

_density = lambda _list: sum([1.0 / (_list[i + 1] - _list[i]) for i in range(len(_list) - 1)])

_inversions = lambda _list: sum([1 for i in range(len(_list)) for j in range(i + 1, len(_list)) if _list[j] <= _list[i]])

# -t / --train - <trin data file, output of prepare_evolution_trainer.py>
# -o / --output - <output file>
# -s / --settings - <file with settings>


def get_args():
    parser = argparse.ArgumentParser(\
        description='Train params', epilog='by ' + __author__)
    parser.add_argument('-t','--train',help='train data file, output of prepare_evolution_trainer.py',\
        metavar='<train file path>', dest='train', required=True, type=str)
    parser.add_argument('-o','--output', help='best results of params evolution algorithm after each step',\
        metavar='<output path>', dest='output', required=False, default='output.evolution', type=str)
    parser.add_argument('-s', '--settings', help='file with settings',\
        metavar='<settings file path>', dest='settings',required=False,default=None,type=str)
    return parser.parse_args()

def get_settings(settings_file):
    integer_params = ['MAX_GENERATIONS', 'POPULATION_SIZE', 'CHILDREN_COUNT']
    float_params = ['MUTATION_POSSIBILITY']
    settings = {'MAX_GENERATIONS': 1000, 'POPULATION_SIZE': 20, 'CHILDREN_COUNT': 10, 'MUTATION_POSSIBILITY': 0.03}

    if settings_file != None:
        f = open(settings_file, 'r')
        for line in f:
            parameter, value = line.strip().split(' ')
            if parameter in integer_params:
                settings[parameter] = int(value)
            elif parameter in float_params:
                settings[parameter] = float(value)
        f.close()
    return settings


def main():
    signal.signal(signal.SIGINT, good_bye)
    args = get_args()
    settings = get_settings(args.settings)
    
    with open(args.train, 'r') as f:
        print 'Loading \"%s\"...' % (args.train, )
        train = pickle.load(f)

    request_to = train['request_to']
    term_to_idf = train['term_to_idf']
    doc_id_to_url = train['doc_id_to_url']
    doc_id_to_length = train['doc_id_to_length']
    doc_id_to_terms = train['doc_id_to_terms']

    genetic = Genetic.Genetic(settings, args.output)
    genetic.init_population()
    population = genetic.get_population()

    for generation in range(settings['MAX_GENERATIONS']):
        status = 1.0 * generation / settings['MAX_GENERATIONS']
        print 'Iteration %d of %d (%.2f%%)' % (generation, settings['MAX_GENERATIONS'], status)
        begin = time.clock()
        fitness = [0.0] * len(population)

        for request_id in request_to.keys():

            request_terms = request_to[request_id][LIST_OF_TERMS]
            list_of_doc_id = request_to[request_id][LIST_OF_DOC_ID]
            list_of_bm25 = request_to[request_id][LIST_OF_BM25]
            #list_of_passage = [[0.0] * len(list_of_bm25)][:] * len(population)
            list_of_passage = []
            for species_id in range(len(population)):
                tmp = [0.0] * len(list_of_doc_id)
                list_of_passage.append(tmp)
            # list_of_passage[species_id][nth_doc]

            # PASSAGE
            sliding_window = [[request_terms[i], None ] for i in range(len(request_terms))]
            for nth_doc in range(len(list_of_doc_id)):
                doc_id = list_of_doc_id[nth_doc]
                # reinit sliding window for this document
                for sw in range(len(sliding_window)):
                    sliding_window[sw][SL_POSITION] = -1

                position_to_term = {}
                for term, positions in doc_id_to_terms[doc_id].iteritems():
                    for position in positions:
                        position_to_term[position] = term

                max_passage = [0.0] * len(population)

                for position in sorted(position_to_term.keys()):
                    for i in list(reversed(range(len(sliding_window)))):
                        if sliding_window[i][SL_TERM] != position_to_term[position]:
                            continue
                        # else
                        sliding_window[i][SL_POSITION] = position
                        sliding_window_positions = [(lambda _list: _list[SL_POSITION])(elem) for elem in sliding_window \
                                                        if (lambda _list: _list[SL_POSITION])(elem) != -1]

                        completeness = 1.0 * len(sliding_window_positions) / len(sliding_window)
                        density = _density(_list=sorted(list(set(sliding_window_positions))))
                        inversions = _inversions(_list=sliding_window_positions)
                        distance_from_beginning = 1.0 - 1.0 * min(sliding_window_positions) / doc_id_to_length[doc_id]

                        # tf-idf of passage
                        passage_tfidf = 0.0
                        for current_position in sliding_window_positions:
                            current_term = position_to_term[current_position]
                            passage_tfidf += term_to_idf[current_term] * request_terms.count(current_term)

                        current_passage = [0.0] * len(population)

                        for species_id in range(len(population)):
                            c_w, dfb_w, d_w, tfidf_w, wo_w = population[species_id]

                            current_passage[species_id] = c_w * completeness + d_w * density + wo_w * 1.0 / (inversions + 1) \
                                        + tfidf_w * passage_tfidf + dfb_w * distance_from_beginning

                            max_passage[species_id] = max(max_passage[species_id], current_passage[species_id])

                for species_id in range(len(population)):
                    list_of_passage[species_id][nth_doc] = max_passage[species_id]


            for species_id in range(len(population)):
                for nth_doc in range(len(list_of_doc_id)):
                    list_of_passage[species_id][nth_doc] = W_bm25 * list_of_bm25[nth_doc] \
                                                                + W_p * list_of_passage[species_id][nth_doc]

            

            for species_id in range(len(population)):
                final_ranking = [_tuple[0] for _tuple in sorted([(doc_id_to_url[list_of_doc_id[nth]], list_of_passage[species_id][nth]) for nth in range(len(list_of_doc_id))],\
                                            key=lambda value: value[1], reverse=True)]

                document_position = final_ranking.index(request_to[request_id][BEST_URL]) + 1
                fitness[species_id] += 1.0 / document_position

        genetic.set_fitness(fitness)
        genetic.print_best()
        genetic.crossing()
        genetic.mutation()
        genetic.selection()
        population = genetic.get_population()
        print 'time: %f' % (time.clock() - begin, )


def good_bye(signal,frame):
    print '\nSee You!'
    exit()

if __name__ == '__main__':
    main()
