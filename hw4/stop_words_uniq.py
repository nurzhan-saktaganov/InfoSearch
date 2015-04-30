#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'


def main():
    stop_words = {}
    filters = [' ', '\t', '\n', '\r']
    for line in sys.stdin:
        stop_word = line.strip().decode('utf-8')
        if stop_word in filters:
            continue
        stop_words[stop_word] = 1

    for stop_word in stop_words.keys():
        print stop_word.encode('utf-8')

if __name__ == '__main__':
    main()