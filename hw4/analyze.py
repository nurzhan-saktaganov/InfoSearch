#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

__author__ = 'Nurzhan Saktaganov'

def get_args():
    parser = argparse.ArgumentParser(\
        description='Analyze', epilog='by ' + __author__)
    parser.add_argument('-b','--boolean',help='boolean search results',\
        metavar='<boolean result file>', dest='boolean', required=True, type=str)
    parser.add_argument('-n','--notboolean', help='bm25 and passage search resutls',
        metavar='<bm25 and passage result file>', dest='notb', required=True, type=str)
    return parser.parse_args()

def main():
    args = get_args()
    with open(args.boolean, 'r') as f:
        boolean = {}
        for line in f:
            request, position = line.strip().split('\t')
            position = int(position)
            boolean[request.decode('utf-8')] = position

    with open(args.notb, 'r') as f:
        bm25, passage = {}, {}
        for line in f:
            request, bm25_position, passage_position = line.strip().split('\t')
            request = request.decode('utf-8')
            bm25_position = int(bm25_position)
            passage_position = int(passage_position)
            bm25[request] = bm25_position
            passage[request] = passage_position

    boolean_found = sorted([position for position in boolean.values() if position != 0])
    bm25_found = sorted([position for position in bm25.values() if position != 0])
    passage_found = sorted([position for position in passage.values() if position != 0])

    total = len(boolean.keys())

    print '---------------------------------------------------------------------------'
    print 'METHOD | TOTAL | FOUND | MEDIANA | MEAN | MIN | MAX  | SCORE | MEAN SCORE |' 
    print '---------------------------------------------------------------------------'
    print_statistics('BOOL', total, boolean_found)
    print_statistics('BM25', total, bm25_found)
    print_statistics('PASSAGE', total, passage_found)
    print '---------------------------------------------------------------------------'
    
def print_statistics(name, total, _list):
    #print 'METHOD  | TOTAL | FOUND | MEDIANA | MEAN | MIN | MAX |SCORE | MEAN SCORE|' 
    print '{0:7}|{1:7}|{2:7}|{3:9}|{4:6}|{5:5}|{6:6}|{7:7.3f}|{8:12.8f}|'.format(name, total,\
            len(_list), _list[len(_list) / 2], sum(_list) / len(_list), min(_list), max(_list), \
            sum([1.0 / position for position in _list]), sum([1.0 / position for position in _list]) / len(_list))


if __name__ == '__main__':
    main()
