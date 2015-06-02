#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

def main():
    previous_url, authority, hub, to_list, from_list = None, 0, 0, None, None

    for line in sys.stdin:
        # remove last \n and split
        splitted_line = line[:-1].decode('utf-8').split('\t')

        current_url = splitted_line[0]

        if current_url != previous_url and previous_url != None:
            print_result(previous_url, authority, hub, to_list, from_list)
            authority, hub, to_list, from_list = 0, 0, None, None

        # if structure
        if len(splitted_line) == 5:
            to_list = splitted_line[3]
            from_list = splitted_line[4]
        # if authority
        elif splitted_line[1] == 'A':
            authority += int(splitted_line[2])
        # if hub
        elif splitted_line[1] == 'H':
            hub += int(splitted_line[2])

        previous_url = current_url

    print_result(previous_url, authority, hub, to_list, from_list)

def print_result(url, authority, hub, to_list, from_list):
    print ('%s\t%d\t%d\t%s\t%s' % (url, authority, hub, to_list, from_list)).encode('utf-8')


if __name__ == '__main__':
    main()
