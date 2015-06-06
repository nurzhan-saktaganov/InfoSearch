#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import lxml.etree
import argparse

from sklearn.ensemble import RandomForestClassifier
#from functions import get_part
from functions import get_features

import pickle

__author__ = 'Nurzhan Saktaganov'

TERMINAL_CHARACTERS = [u'.', u'?', u'!']
THE_NUMBERS = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
OPT = 30


def get_args():
    # -c / --classifier - <file with classifier>
    # -i / --input - <file with sentences to split>
    # -o / --output - <file with splitted sentences>
    parser = argparse.ArgumentParser(\
        description='Sentences splitter', epilog='by ' + __author__)
    parser.add_argument('-c', '--classifier', help='file with classifier',\
        metavar='<classifier file path>', dest='classifier', required=True, type=str)
    parser.add_argument('-i', '--input', help='file with sentences to split',\
        metavar='<input file path>', dest='input', required=True, type=str)
    parser.add_argument('-o', '--output', help='file with splitted sentences; prints to stdout if not specified',\
        metavar='<output file path>', dest='output', required=False, type=str, default=None)
    return parser.parse_args()


def main():
    args = get_args()

    with open(args.classifier, 'r') as f:
        classifier = pickle.load(f)

    if args.output != None:
        output = open(args.output, 'w')
    else:
        output = sys.stdout

    with open(args.input, 'r') as f:
        for paragraph in f:
            sentences = split(classifier, paragraph.decode('utf-8'))
            output.write('\n'.join(sentences).encode('utf-8'))



def split(classifier, paragraph):
    begin, sentences = 0, []
    for i in range(len(paragraph)):
        if paragraph[i] not in TERMINAL_CHARACTERS:
            continue

        if i > 0:
            context = paragraph[i - 1: i + 3]
        else:
            continue

        left = i - 1
        while left >= 0 and paragraph[left] not in TERMINAL_CHARACTERS:
            left -= 1

        left_distance = i - left

        right = i + 1
        while right <= len(paragraph) - 1 and paragraph[right] not in TERMINAL_CHARACTERS:
            right += 1

        if i == len(paragraph) - 1:
            right_distance = OPT
        else:
            right_distance = right - i

        x = get_features(context, left_distance, right_distance)

        if classifier.predict(x) == 1:
            sentences.append(paragraph[begin: i + 1].strip())
            begin = i + 2

    if paragraph[begin:] != u'\n':
        sentences.append(paragraph[begin: -1].strip())

    return sentences


if __name__ == '__main__':
    main()