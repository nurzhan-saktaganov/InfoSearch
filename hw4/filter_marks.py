#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

__author__ = 'Nurzhan Saktaganov'

# -m / --marks - <file with marks>
# -u / --urls - <file with urls>
# -o / --output - <output, filtered marks>
    
def get_args():
    parser = argparse.ArgumentParser(\
        description='Filter assessors\' marks by urls', epilog='by ' +__author__)
    parser.add_argument('-m', '--marks', help='assessors\' marks', metavar='<file with marks>',\
        dest='marks', required=True, type=str)
    parser.add_argument('-u', '--urls', help='urls file', metavar='<file with urls>',\
        dest='urls', required=True, type=str)
    parser.add_argument('-o', '--output', help='output, filtered marks', metavar='<output>',\
        dest='output', required=False, type=str, default='output.marks')
    return parser.parse_args()

def main():
    args = get_args()

    get_url = lambda line: line.strip().split('\t')[1]
    normalize = lambda url: url[:-1] if url.count('/') > 3 and url.count('?') == 0 and url[-1] == '/' else url

    with open(args.urls, 'r') as f:
        url_filter = [normalize(get_url(line)) for line in f]
   
    output = open(args.output, 'w')
    with open(args.marks, 'r') as f:
        for line in f:
            if line.strip().split('\t')[1] in url_filter:
                output.write(line)
    output.close()
    
if __name__ == '__main__':
    main()
