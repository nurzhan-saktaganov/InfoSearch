#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import base64 
import zlib

import lxml
import lxml.html.clean

SPLIT_RGX = re.compile('\w+', re.U)

# output format: <term><\tab><doc_id><\space><count><\space><comma separated list of positions><\newline>
def main():

    script_cleaner = lxml.html.clean.Cleaner(scripts=True,javascript=True\
        ,comments=True,style=True,links=True,meta=False, remove_tags=['a', 'img']) #,kill_tags=['script','style'])

    with open(sys.argv[1], 'r') as f:
        stop_words = [word.strip().decode('utf-8') for word in f.readlines()]

    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')

        html_code = unicode(zlib.decompress(base64.b64decode(html_b64encoded)), encoding='utf-8')
        html_noscript = script_cleaner.clean_html(html_code)

        #code from comment https://sfera-mail.ru/blog/Find/611.html#comment2000
        document = lxml.html.document_fromstring(html_noscript)
        text = " ".join(lxml.etree.XPath("//text()")(document)).lower()

        words = [word for word in re.findall(SPLIT_RGX, text) if word not in stop_words]

        output = ''
        for word in words:
            output += word + ' '
        output = output[:-1]

        sys.stdout.write(doc_id + '\t' + str(len(words)) + '\t' + \
                base64.b64encode(zlib.compress(output.encode('utf-8'))) + '\n')

if __name__ == '__main__':
    main()