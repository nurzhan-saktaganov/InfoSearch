#!/usr/bin/env python

import sys

def main():

    previous_term = None
    list_of_doc_id = []

    for line in sys.stdin:
        current_term, doc_id = line.split('\t')
        if current_term == previous_term or previous_term == None:
            list_of_doc_id.append(int(doc_id))
        else:
            print_result(previous_term, list_of_doc_id)
            list_of_doc_id = [int(doc_id)]

        previous_term = current_term

    print_result(previous_term, list_of_doc_id)



def print_result(term, list_of_doc_id):
    sys.stdout.write(term)
    for doc_id in list_of_doc_id:
        sys.stdout.write('\t' + str(doc_id))
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()