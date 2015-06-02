#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

URL_SEPARATOR = ' '

def main():

    for line in sys.stdin:
        # remove last \n
        line = line[:-1]

        # send structure
        print line

        current_url, authority, hub, to_list, from_list = line.decode('utf-8').split('\t')

        authority = int(authority)
        hub = int(hub)

        if to_list != '{}':
            for url in to_list[1:-1].split(URL_SEPARATOR):
                # our hub is other's authority
                print ('%s\tA\t%d' % (url, hub)).encode('utf-8')

        if from_list != '{}':
            for url in from_list[1:-1].split(URL_SEPARATOR):
                # out authority is other's hub
                print ('%s\tH\t%d' % (url, authority)).encode('utf-8')

if __name__ == '__main__':
    main()
