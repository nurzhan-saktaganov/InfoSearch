#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import Simple9
import VarByte
import base64

import collections

def main():

    previous_term = None
    dictionary = {}

    encoder = VarByte.VarByte

    if len(sys.argv) == 2 and sys.argv[1] == 'Simple9':
    	encoder = Simple9.Simple9

    for line in sys.stdin:
        current_term, doc_id, count, positions = line[:-1].split('\t')
        if current_term == previous_term or previous_term == None:
            dictionary[int(doc_id)] = [int(count), map(int, positions.split(','))]
        else:
            print_result(term=previous_term, dictionary=dictionary, encoder=encoder)
            dictionary = {}
            dictionary[int(doc_id)] = [int(count), map(int, positions.split(','))]

        previous_term = current_term

    print_result(term=previous_term, dictionary=dictionary, encoder=encoder)


#output format: <term><\tab><document frequency><\tab><list of doc_id><\tab>
#                    <list of counts><\tab><comma separated list of positions list>
def print_result(term, dictionary, encoder):
    # dictionary sorted by key
    ordered_dictionary = collections.OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))
    list_of_doc_id, list_of_counts, list_of_positions_list = [], [], []

    for key, value in ordered_dictionary.iteritems():
        list_of_doc_id.append(key)
        list_of_counts.append(value[0])
        list_of_positions_list.append(value[1])

    encoded_list_of_doc_id = encoder.encode(list_of_doc_id, True)
    encoded_list_of_counts = encoder.encode(list_of_counts, False)
    encoded_list_of_positions_list = map(encoder.encode, list_of_positions_list)

    output = term.decode('utf-8') + '\t' + str(len(list_of_doc_id)) + '\t'\
                 + encoded_list_of_doc_id + '\t'\
                 + encoded_list_of_counts + '\t'\
                 + ','.join(encoded_list_of_positions_list)

    print output.encode('utf-8')

if __name__ == '__main__':
    main()