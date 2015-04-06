#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import lxml.etree
import optparse

#from optparse import OptionParser
from sklearn.ensemble import RandomForestClassifier
from functions import get_part
from functions import get_training_set
from functions import get_features

__author__ = 'Nurzhan Saktaganov'

TERMINAL_CHARACTERS = [u'.', u'?', u'!']
THE_NUMBERS = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
OPT = 69

def get_options():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--learn', dest='learn_path', \
            help='xml file with train set', metavar='FILE')
    parser.add_option('-s', '--split', dest='split_path', \
            help='txt file for splitting', metavar='FILE')
    parser.add_option('-o', '--output', dest='output_path', \
            help='result file name', metavar='FILE')
    options, args = parser.parse_args()
    return options

def main():
    options = get_options()
    source_path = options.learn_path
    to_split_path = options.split_path
    output_path = options.output_path

    classifier = RandomForestClassifier(n_estimators=70 \
        , criterion='gini', max_features='auto', n_jobs=1)

    tree = lxml.etree.parse(source_path)
    root = tree.getroot()

    training_set_X, training_set_y = get_training_set(root)

    classifier.fit(training_set_X, training_set_y)

    #for i in range(len(training_set_X)):
        #pass #print training_set_X[i] + [training_set_y[i]]

    output = open(output_path, 'w')
    to_split = open(to_split_path, 'r')

    for line in to_split:
        line = line.decode('utf-8')
        begin = 0
        for i in range(len(line)):
            if line[i] not in TERMINAL_CHARACTERS:
                continue

            if i > 0:
                context = line[i - 1: i + 3]
            else:
                continue #context = '\r' + line[i: i + 3]

            left = i - 1
            while left >= 0 and line[left] not in TERMINAL_CHARACTERS:
                left -= 1

            left_distance = i - left

            right = i + 1
            while right <= len(line) - 1 and line[right] not in TERMINAL_CHARACTERS:
                right += 1

            if i == len(line)  - 1:
                right_distance = OPT
            else:
                right_distance = right - i

            x = get_features(context, left_distance, right_distance)
            if classifier.predict(x) == 1:
                output.write(line[begin: i + 1].encode('utf-8') + '\n')
                begin = i + 2

        if line[begin:] != u'\n':
            output.write(line[begin:-1].encode('utf-8') + '\n')

if __name__ == '__main__':
    main()