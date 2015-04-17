#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def main():

    for line in sys.stdin:
        print line[:-1]

if __name__ == '__main__':
    main()