#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def main():
    marks_file_name = './marks/lenta1000.tsv'
    urls_file_name = './1_1000/lenta.ru/10_urls.txt'
    output_file_name = './1_1000/lenta.ru/10_filtered_marks.txt'

    marks_file = open(marks_file_name, 'r')
    urls_file = open(urls_file_name, 'r')
    output_file = open(output_file_name, 'w')

    url_filter = [line.strip().split('\t')[1][:-1] for line in urls_file]

    print url_filter[:100]

    for line in marks_file:
        if line.strip().split('\t')[1] in url_filter:
            output_file.write(line)

if __name__ == '__main__':
    main()