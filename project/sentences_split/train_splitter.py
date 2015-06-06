#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import lxml.etree
import argparse

#from optparse import OptionParser
from sklearn.ensemble import RandomForestClassifier

from functions import get_training_set

import pickle

__author__ = 'Nurzhan Saktaganov'

TERMINAL_CHARACTERS = [u'.', u'?', u'!']
THE_NUMBERS = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
OPT = 30


def get_args():
    # -t / --train - <file with sentences in hw3 format>
    # -o / --output - <file with result classifier>
    parser = argparse.ArgumentParser(\
        description='Sentences splitter trainer', epilog='by ' + __author__)
    parser.add_argument('-t', '--train', help='file with sentences (.xml format)',\
        metavar='<train set file path>', dest='train', required=True, type=str)
    parser.add_argument('-o', '--output', help='splitter classifier file',\
        metavar='<splitter classifier file>', dest='output', required=False, \
        type=str, default='classifier.data')
    return parser.parse_args()

def main():
    args = get_args()

    classifier = RandomForestClassifier(n_estimators=70, criterion='entropy', max_features='auto', n_jobs=1)

    tree = lxml.etree.parse(args.train)
    root = tree.getroot()

    training_set_X, training_set_y = get_training_set(root)

    classifier.fit(training_set_X, training_set_y)

    with open(args.output, 'w') as f:
        pickle.dump(classifier, f)


if __name__ == '__main__':
    main()