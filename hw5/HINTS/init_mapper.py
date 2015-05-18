#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

def main():

    for line in sys.stdin:
    	# remove last \n
        current_url, url_list = line[:-1].decode('utf-8').split('\t')

        print ('%s\tTO\t{%s}' % (current_url, url_list)).encode('utf-8')

        url_list = url_list.split(',')

        for url in url_list:
            print ('%s\tFROM\t%s' % (url, current_url)).encode('utf-8')

if __name__ == '__main__':
    main()
