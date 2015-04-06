#/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nurzhan Saktaganov'

import sys
import lxml.etree


def main():
    source_path = './sentences.xml'
    output_path = './input.txt'
    check_path = './check.txt'

    output = open(output_path, 'w')
    check = open(check_path, 'w')
    
    tree = lxml.etree.parse(source_path)
    root = tree.getroot()
    texts = get_part(root, 'text')
    for text in texts:
        chapters = get_part(text, 'paragraphs')
        for chapter in chapters:
            paragraphs = get_part(chapter, 'paragraph')
            for paragraph in paragraphs:
                sentences = get_part(paragraph, 'source')
                list_of_sentences = []
                for sentence in sentences:
                    list_of_sentences.append(sentence.text)

                for i in range(len(list_of_sentences) - 1):
                    output.write((list_of_sentences[i] + u' ').encode('utf-8'))
                    check.write((list_of_sentences[i] + u'\n').encode('utf-8'))
                output.write((list_of_sentences[-1] + u'\n').encode('utf-8'))
                check.write((list_of_sentences[-1] + u'\n').encode('utf-8'))

    output.close()

def get_part(etree_node, part):
    for node in etree_node.findall('.//' + part):
        yield node

if __name__ == '__main__':
    main()