#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import base64 
import zlib

import lxml
import lxml.html.clean

import html2text

SPLIT_RGX = re.compile('\w+', re.U)

# output format: <term><\tab><doc_id><\space><count><\space><comma separated list of positions><\newline>
def main():

    script_cleaner = lxml.html.clean.Cleaner(scripts=True,javascript=True\
        ,comments=True,style=True,links=True,meta=False, remove_tags=['a', 'img']) #,kill_tags=['script','style'])

    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')

        html_code = unicode(zlib.decompress(base64.b64decode(html_b64encoded)), encoding='utf-8')
        html_noscript = script_cleaner.clean_html(html_code)

        #code from comment https://sfera-mail.ru/blog/Find/611.html#comment2000
        document = lxml.html.document_fromstring(html_noscript)
        text = " ".join(lxml.etree.XPath("//text()")(document)).lower()

        words = re.findall(SPLIT_RGX, text)

        print '%s\t%d' % (doc_id, len(words))

if __name__ == '__main__':
    main()