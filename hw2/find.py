#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle

import base64
import VarByte
import Simple9

from sets import Set
import signal

def help():
    help_text =\
        'options:\n'\
      + '-i <index_file>\n'\
      + '-u <urls_file>\n'\
      + '-d <dictionary file>\n'\
      + '[-e <VarByte|Simple9>] (by default is VarByte)\n'
    print help_text

def good_bye(signal,frame):
    print 'See You!'
    exit()


def main():
    signal.signal(signal.SIGINT, good_bye)
    
    try:
        index_file = sys.argv[sys.argv.index('-i') + 1]
        dictionary_file = sys.argv[sys.argv.index('-d') + 1]
        urls_file = sys.argv[sys.argv.index('-u') + 1]
    except Exception, e:
        help()
        exit()

    try:
    	encoder_name = sys.argv[sys.argv.index('-e') + 1]
    except Exception, e:
    	encoder_name = 'VarByte'

    if encoder_name == 'Simple9':
    	encoder = Simple9.Simple9
    else:
    	encoder = VarByte.VarByte

    with open(dictionary_file) as f:
        dictionary = pickle.load(f)

    doc_id_to_url = {}
    with open(urls_file) as f:
        for line in f:
            doc_id, url = line[:-1].split('\t')
            doc_id_to_url[int(doc_id)] = url

    f = open(index_file)

    doc_count = len(doc_id_to_url.keys())

    while True:
        try:
            sys.stdout.write('\nfind: ')
            line = raw_input().decode('utf-8')
        except Exception, e:
            print e
            continue

        request = line.split(' AND ')

        for subrequest in request:
            print subrequest

        include, exclude = [], []

        for subrequest in request:
            subrequest = subrequest.lower().split(' ')
            if len(subrequest) == 2 \
                    and subrequest[1] in dictionary\
                    and subrequest[0] == 'not':
                offset, size = dictionary[subrequest[1]]
                f.seek(offset)
                b64encoded = f.read(size)
                byte_list = [char for char in base64.b64decode(b64encoded)]
                exclude += encoder.decode(byte_list)
            elif len(subrequest) == 1 and\
                    subrequest[0] in dictionary:
                offset, size = dictionary[subrequest[0]]
                f.seek(offset)
                b64encoded = f.read(size)
                byte_list = [char for char in base64.b64decode(b64encoded)]
                include.append(encoder.decode(byte_list))
            elif len(subrequest) == 1:
                include, exclude = [], []
                print 'No matches!'
                
        result = Set([])

        if len(include) == 0 and len(exclude) > 0:
            result = Set(range(doc_count))
        elif len(include) > 0:
            result = Set(include[0])
            for i in range(1, len(include)):
                result.intersection_update(Set(include[i]))

        result.difference_update(Set(exclude))

        for doc_id in result:
            print doc_id_to_url[doc_id]


if __name__ == '__main__':
    main()