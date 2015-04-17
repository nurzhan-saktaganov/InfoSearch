#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from DictionaryBuilder import DictionaryBuilder
import pickle
#import zlib

__author__ = 'Nurzhan Saktaganov'

def help():
    help_text =\
        'options:\n'\
      + '-i <input_file>\n'\
      + '[-o <output_file>] (by default is \'dictionary.dic\')\n'
    print help_text

def main():
    try:
        input_file = sys.argv[sys.argv.index('-i') + 1]
    except Exception, e:
        print 'The input file is not specified'
        help()
        exit()
    
    try:
        output_file = sys.argv[sys.argv.index('-o') + 1]
    except Exception, e:
        output_file = 'dictionary.dic'

    dictionary = DictionaryBuilder.build(input_file)
    #compressed = zlib.compress(dictionary)

    with open(output_file, 'w') as output:
        pickle.dump(dictionary, output)

if __name__ == '__main__':
    main()