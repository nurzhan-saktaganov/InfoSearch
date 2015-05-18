#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import base64 
import zlib

from lxml import html

__author__ = 'Nurzhan Saktaganov' 

# mapper.py for PageRank
# has two positional arguments
# 1. file with urls (doc_id -> url)
# 2. site name (e.g. http://site.dom/)

normalize = lambda url: url[:-1] if url.count('/') > 3 and url.count('?') == 0 and url[-1] == '/' else url

get_link = lambda raw_link, site_name:  (site_name[:-1] + raw_link) if raw_link.startswith('/') else raw_link

get_inner_links = lambda html_code, site_name: [normalize(get_link(raw_link=link[2],site_name=site_name)) \
        for link in html.iterlinks(html_code) \
            if link[2].startswith(site_name) or \
                (link[2].startswith('/') and not link[2].startswith('//'))]
                
get_uniq_inner_links = lambda html_code, site_name: list(set(get_inner_links(html_code=html_code,site_name=site_name)))

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
        
        inner_links = get_uniq_inner_links(html_code=html_code,site_name=site_name)
        
        print (doc_url + '\t' + ','.join(inner_links)).encode('utf-8')

if __name__ == '__main__':
    main()
