#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import base64 
import zlib

import lxml
import lxml.html.clean

SPLIT_RGX = re.compile('\w+', re.U)

def main():

    script_cleaner = lxml.html.clean.Cleaner(scripts=False,javascript=False\
        ,comments=True,style=False,links=False,meta=False,kill_tags=['script','style'])

    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')

        html_code = zlib.decompress(base64.b64decode(html_b64encoded))
        html_noscript = script_cleaner.clean_html(html_code)

        #code from comment https://sfera-mail.ru/blog/Find/611.html#comment2000
        document = lxml.html.document_fromstring(html_noscript)
        text = " ".join(lxml.etree.XPath("//text()")(document))
        words = re.findall(SPLIT_RGX, text)

        terms = set([word.lower().encode('utf-8') for word in words])

        for term in terms:
            print '%s\t%s' % (term, doc_id)

if __name__ == '__main__':
    main()