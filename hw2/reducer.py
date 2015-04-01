#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import Simple9
import VarByte
import base64

def main():

    previous_term = None
    list_of_doc_id = []
    encoder = VarByte.VarByte

    if len(sys.argv) == 2 and sys.argv[1] == 'Simple9':
    	encoder = Simple9.Simple9


    for line in sys.stdin:
        current_term, doc_id = line.split('\t')
        if current_term == previous_term or previous_term == None:
            list_of_doc_id.append(int(doc_id))
        else:
            list_of_doc_id.sort()
            print_result(term=previous_term, list_of_doc_id=list_of_doc_id,encoder=encoder)
            list_of_doc_id = [int(doc_id)]

        previous_term = current_term

    list_of_doc_id.sort()
    print_result(term=previous_term, list_of_doc_id=list_of_doc_id,encoder=encoder)



def print_result(term, list_of_doc_id, encoder):
    encoded_byte_list = encoder.encode(list_of_doc_id)
    
    output = ''
    for byte in encoded_byte_list:
        output += byte

    output = base64.b64encode(output)

    sys.stdout.write(term + '\t'+ output + '\n')


if __name__ == '__main__':
    main()