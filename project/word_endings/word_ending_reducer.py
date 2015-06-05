#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

__author__ = 'Nurzhan Saktaganov'

def main():
    previous_ending = None

    for ending in sys.stdin:
        current_ending = ending.decode('utf-8').strip()

        if current_ending == previous_ending or previous_ending == None:
            pass
        else:
            print previous_ending.encode('utf-8')

        previous_ending = current_ending

    print previous_ending.encode('utf-8')

if __name__ == '__main__':
    main()