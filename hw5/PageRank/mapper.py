#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

D = 0.85

URL_SEPARATOR = ' '

def main():

    for line in sys.stdin:
        # remove last \n
        line = line[:-1]
        
        # send structure
        print line

        current_url, page_rank, adjacency_list = line.decode('utf-8').split('\t')

        if adjacency_list == '{}':
            continue

        adjacency_list = adjacency_list[1:-1].split(URL_SEPARATOR)

        p = float(page_rank) / len(adjacency_list)

        for url in adjacency_list:
            print ('%s\t%lf' % (url, p)).encode('utf-8')

if __name__ == '__main__':
    main()
