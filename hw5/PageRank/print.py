#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def main():
    for line in sys.stdin:
        splitted = line[:-1].decode('utf-8').split('\t')
        url, pr, urls = splitted
        print ('%s\t%s' % (url, pr)).encode('utf-8')

if __name__ == '__main__':
    main()
