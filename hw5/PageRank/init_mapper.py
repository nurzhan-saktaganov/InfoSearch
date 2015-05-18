#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

D = 0.85

def main():

    for line in sys.stdin:
    	# remove last \n
        current_url, url_list = line[:-1].decode('utf-8').split('\t')

        # send structure
        print ('%s\t%lf\t{%s}' % (current_url, 1.0 - D, url_list)).encode('utf-8') 

        url_list = url_list.split(',')

        p = (1 - D) / len(url_list)

        for url in url_list:
            print ('%s\t%lf' % (url, p)).encode('utf-8')

if __name__ == '__main__':
    main()
