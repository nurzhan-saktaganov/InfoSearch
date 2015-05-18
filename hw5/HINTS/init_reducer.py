#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

def main():
    previous_url, to_list, from_list = None, '{}', []

    for line in sys.stdin:
        # remove last \n
        current_url, direction, list_or_url = line[:-1].decode('utf-8').split('\t')

        if current_url != previous_url and previous_url != None:
            print_result(previous_url, to_list, from_list)
            to_list = '{}'
            from_list = []

        if direction == 'TO':
            # list_or_url is list
            to_list = list_or_url
        elif direction == 'FROM':
            # list_or_url is url
            from_list.append(list_or_url)

        previous_url = current_url

    print_result(previous_url, to_list, from_list)

def print_result(url, to_list, from_list):
    # url authority hub to-list from-list
    print ('%s\t1\t1\t%s\t{%s}' % (url, to_list, ','.join(from_list))).encode('utf-8')

if __name__ == '__main__':
    main()
