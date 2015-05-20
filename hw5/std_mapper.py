#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import base64 
import zlib
import re

from lxml import html

__author__ = 'Nurzhan Saktaganov' 

# mapper.py for PageRank
# has two positional arguments
# 1. file with urls (doc_id -> url)
# 2. site name (e.g. http://site.dom/)

URL_SEPARATOR = ' '
URL_RGX = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.U)

normalize = lambda url: url[:-1] if url.count('/') > 3 and url.count('?') == 0 and url[-1] == '/' else url

get_link = lambda raw_link, site_name:  (site_name[:-1] + raw_link) if raw_link.startswith('/') else raw_link

get_inner_links = lambda html_code, site_name: [normalize(get_link(raw_link=link[2],site_name=site_name)) \
        for link in html.iterlinks(html_code) \
            if link[2].startswith(site_name) or \
                (link[2].startswith('/') and not link[2].startswith('//'))]
                
get_uniq_inner_links = lambda html_code, site_name: list(set(get_inner_links(html_code=html_code,site_name=site_name)))

filter_symbols = [\
      u'а', u'б', u'в', u'г', u'д', u'е', u'ё' \
    , u'ж', u'з', u'и', u'й', u'к', u'л', u'м' \
    , u'н', u'о', u'п', u'р', u'с', u'т', u'у' \
    , u'ф', u'х', u'ц', u'ч', u'ш', u'щ', u'ъ' \
    , u'ы', u'ь', u'э', u'ю', u'я' \
    , u' ' \
]

def filter_function(url):
    for symbol in filter_symbols:
        if url.count(symbol) > 0:
            return False
    return URL_RGX.match(url)

def main():

    with open(sys.argv[1], 'r') as f:
        docID_to_url = {}
        for line in f:
            doc_id, url = line.strip().split('\t')
            docID_to_url[int(doc_id)] = normalize(url)
    
    site_name = sys.argv[2]
    
    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')
        
        doc_url = docID_to_url[int(doc_id)]
        
        html_code = unicode(zlib.decompress(base64.b64decode(html_b64encoded)), encoding='utf-8')

        inner_links = filter(filter_function, get_uniq_inner_links(html_code=html_code,site_name=site_name))
 
        print (doc_url + '\t' + URL_SEPARATOR.join(inner_links)).encode('utf-8')

if __name__ == '__main__':
    main()
