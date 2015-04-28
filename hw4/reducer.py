#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import Simple9
import VarByte
import base64

#global variables

def main():

    previous_term = None
    list_of_docs = []

    encoder = VarByte.VarByte

    if len(sys.argv) == 2 and sys.argv[1] == 'Simple9':
        encoder = Simple9.Simple9

    for line in sys.stdin:
        current_term, doc_id, count, positions = line.strip().split('\t')
        if current_term == previous_term or previous_term == None:
            list_of_docs.append([int(doc_id), int(count), map(int, positions.split(','))])
        else:
            print_result(term=previous_term, list_of_docs=list_of_docs, encoder=encoder)
            list_of_docs = []
            list_of_docs.append([int(doc_id), int(count), map(int, positions.split(','))])

        previous_term = current_term

    print_result(term=previous_term, list_of_docs=list_of_docs,encoder=encoder)


#output format: <term><\tab><document frequency><\tab><list of doc_id><\tab>
#                    <list of counts><\tab><comma separated list of positions list>
def print_result(term, list_of_docs,encoder):
    # sort by doc id
    list_of_docs.sort(key=lambda value: value[0])

    encoded_list_of_doc_id = encoder.encode([list_of_docs[i][0] for i in range(len(list_of_docs))], True)
    encoded_list_of_counts = encoder.encode([list_of_docs[i][1] for i in range(len(list_of_docs))], False)
    encoded_list_of_positions_list = map(encoder.encode, [list_of_docs[i][2] for i in range(len(list_of_docs))])

    output = term.decode('utf-8') + '\t' + str(len(list_of_docs)) + '\t' \
                + encoded_list_of_doc_id + '\t'\
                + encoded_list_of_counts + '\t' \
                + ','.join(encoded_list_of_positions_list)

    print output.encode('utf-8')

if __name__ == '__main__':
    main()