#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle

import base64
import VarByte
import Simple9

def help():
    help_text =\
        'options:\n'\
      + '-i <index_file>\n'\
      + '-u <urls_file>\n'\
      + '-d <dictionary file>\n'\
      + '[-e <VarByte|Simple9>] (by default is VarByte)\n'
    print help_text


def main():
    try:
        index_file = sys.argv[sys.argv.index('-i') + 1]
        dictionary_file = sys.argv[sys.argv.index('-d') + 1]
        urls_file = sys.argv[sys.argv.index('-u') + 1]
    except Exception, e:
        help()
        #exit()
        index_file = './inverted_index/lenta.ru.txt'
        dictionary_file = './dictionary.dic'
        urls_file = './1_1000/lenta.ru/urls.txt'

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

    while True:
        line = raw_input().decode('utf-8').lower()
        print line
        if line not in dictionary:
        	print 'No matches'
        	continue
        
        offset, size = dictionary[line]
        f.seek(offset)
        b64encoded = f.read(size)
        byte_list = [char for char in base64.b64decode(b64encoded)]
        for doc_id in encoder.decode(byte_list):
        	print doc_id_to_url[doc_id]



if __name__ == '__main__':
    main()