#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle

import base64
import VarByte
import Simple9

import argparse

from sets import Set
import signal

__author__ = 'Nurzhan Saktaganov'

normalize = lambda url: url[:-1] if url.count('/') > 3 and url.count('?') == 0 and url[-1] == '/' else url

def good_bye(signal,frame):
    print 'See You!'
    exit()

def get_args():
    parser = argparse.ArgumentParser(\
        description='None', epilog='by ' + __author__)
    parser.add_argument('-i','--invert', help='inverted index file, output of mapper.py',
        metavar='<inverted index file path>', dest='invert', required=True, type=str)
    parser.add_argument('-u','--urls', help='file with urls',metavar='<urls file path>',\
        dest='urls', required=True, type=str)
    parser.add_argument('-d','--dictionary',help='dictionary file',\
        metavar='<dictionary file path>', dest='dictionary', required=True, type=str)
    parser.add_argument('-m','--marks', help='assessors\' marks',\
        metavar='<file with marks>', dest='marks', required=True, type=str)
    parser.add_argument('-c', '--compress',help='compressing algorithm: default=VarByte',\
        dest='compress', required=False, default='VarByte', type=str, choices=['VarByte', 'Simple9'])
    return parser.parse_args()


def main():
    signal.signal(signal.SIGINT, good_bye)
    args = get_args()

    index_file = args.invert
    dictionary_file = args.dictionary
    urls_file = args.urls

    with open(args.marks, 'r') as f:
        # marks is list of [request, url]
        marks = [line.decode('utf-8').strip().split('\t') for line in f]
    
    if args.compress == 'Simple9':
        encoder = Simple9.Simple9
    else:
        encoder = VarByte.VarByte

    with open(dictionary_file) as f:
        dictionary = pickle.load(f)

    doc_id_to_url = {}
    with open(urls_file) as f:
        for line in f:
            doc_id, url = line[:-1].split('\t')
            doc_id_to_url[int(doc_id)] = normalize(url)

    f = open(index_file)

    doc_count = len(doc_id_to_url.keys())

    for current_request, best_url in marks:
        request = current_request.split(' ')

        include = []

        for subrequest in request:
            if subrequest not in dictionary:
                continue
            offset, size = dictionary[subrequest]
            f.seek(offset)
            b64encoded = f.read(size)
            byte_list = [char for char in base64.b64decode(b64encoded)]
            include.append(encoder.decode(byte_list))

        result = Set([])

        if len(include) == 0:
            boolean_postion = 0
            print '%s\t%d' % (current_request.encode('utf-8'), boolean_position)
            continue

        result = Set(include[0])
        for i in range(1, len(include)):
            result.intersection_update(Set(include[i]))

        result_urls = [doc_id_to_url[doc_id] for doc_id in result]

        try:
            boolean_position = result_urls.index(best_url) + 1
        except Exception, e:
            boolean_postion = 0

        print '%s\t%d' % (current_request.encode('utf-8'), boolean_position)

if __name__ == '__main__':
    main()