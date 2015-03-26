#!/usr/bin/env python

import sys
import Simple9
import VarByte
import base64

def main():

    previous_term = None
    list_of_doc_id = []
    encoder = VarByte.VarByte

    for line in sys.stdin:
        current_term, doc_id = line.split('\t')
        if current_term == previous_term or previous_term == None:
            list_of_doc_id.append(int(doc_id))
        else:
            print_result(previous_term, list_of_doc_id,encoder)
            list_of_doc_id = [int(doc_id)]

        previous_term = current_term

    print_result(previous_term, list_of_doc_id,encoder)



def print_result(term, list_of_doc_id,encoder):
    encoded_byte_list = encoder.encode(list_of_doc_id)

    output = ''
    for byte in encoded_byte_list:
        output += byte

    output = base64.b64encode(output)

    sys.stdout.write(term + '\t'+ output + '\n')


if __name__ == '__main__':
    main()