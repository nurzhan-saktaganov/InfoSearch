#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

URL_SEPARATOR = ' '

def main():

    for line in sys.stdin:
        # remove last \n
        current_url, url_list = line[:-1].decode('utf-8').split('\t')

        if url_list != ' ':
            print ('%s\tTO\t{%s}' % (current_url, url_list)).encode('utf-8')
        else:
            print ('%s\tTO\t{}' % (current_url)).encode('utf-8')
            continue

        url_list = url_list.split(URL_SEPARATOR)

        for url in url_list:
            print ('%s\tFROM\t%s' % (url, current_url)).encode('utf-8')

if __name__ == '__main__':
    main()
