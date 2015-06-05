#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import Simple9
import VarByte
import base64

__author__ = 'Nurzhan Saktaganov'

def main():
    previous_term, list_of_docs = None, []

    if len(sys.argv) == 2 and sys.argv[1] == 'Simple9':
        encoder = Simple9.Simple9
    else:
        encoder = VarByte.VarByte

    for line in sys.stdin:
        current_term, doc_id, count, positions, endings = line.decode('utf-8').strip().split('\t')
        if current_term == previous_term or previous_term == None:
            list_of_docs.append([int(doc_id), int(count), map(int, positions.split(',')), map(int, endings.split(','))])
        else:
            print_result(term=previous_term, list_of_docs=list_of_docs, encoder=encoder)
            list_of_docs = []
            list_of_docs.append([int(doc_id), int(count), map(int, positions.split(',')), map(int, endings.split(','))])

        previous_term = current_term

    print_result(term=previous_term, list_of_docs=list_of_docs, encoder=encoder)


#output format: <term><\tab><document frequency><\tab><list of doc_id><\tab>
#                    <list of counts><\tab><comma separated list of positions list>
#                    <\tab><comma separated list of endings list>
def print_result(term, list_of_docs, encoder):
    # sort by doc id for encoding
    list_of_docs.sort(key=lambda value: value[0])

    encoded_list_of_doc_id = encoder.encode([list_of_docs[i][0] for i in range(len(list_of_docs))], True)
    encoded_list_of_counts = encoder.encode([list_of_docs[i][1] for i in range(len(list_of_docs))], False)
    encoded_list_of_positions_list = \
        map(lambda _list: encoder.encode(_list, True), [list_of_docs[i][2] for i in range(len(list_of_docs))])
    encoded_list_of_endings_list = \
        map(lambda _list: encoder.encode(_list, False), [list_of_docs[i][3] for i in range(len(list_of_docs))])

    output = term + '\t' + str(len(list_of_docs)) + '\t' \
                + encoded_list_of_doc_id + '\t' \
                + encoded_list_of_counts + '\t' \
                + ','.join(encoded_list_of_positions_list) + '\t'\
                + ','.join(encoded_list_of_endings_list)

    print output.encode('utf-8')


if __name__ == '__main__':
    main()