#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

D = 0.85

def main():

    previous_url, adjacency_list, page_rank = None, '{}', 0.0

    for line in sys.stdin:
        # remove last \n
        splitted_line = line[:-1].decode('utf-8').split('\t')

        current_url = splitted_line[0]

        if current_url != previous_url and previous_url != None:
            print_result(previous_url, (1.0 - D) + D * page_rank, adjacency_list)
            adjacency_list = '{}'
            page_rank = 0.0

        # if structure
        if len(splitted_line) == 3:
            adjacency_list = splitted_line[2]
        # else
        elif len(splitted_line) == 2:
            page_rank += float(splitted_line[1])

        previous_url = current_url

    print_result(previous_url, (1.0 - D) + D * page_rank, adjacency_list)

def print_result(url, page_rank, adjacency_list):
    print ('%s\t%lf\t%s' % (url, page_rank, adjacency_list)).encode('utf-8')

if __name__ == '__main__':
    main()
