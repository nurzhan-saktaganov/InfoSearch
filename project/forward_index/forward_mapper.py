#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import base64
import zlib

import lxml
import lxml.html.clean

import argparse

from sklearn.ensemble import RandomForestClassifier
from functions import get_features
import pickle

import Simple9
import VarByte

__author__ = 'Nurzhan Saktaganov'

# for normalize text
SPLIT_RGX = re.compile('\w+', re.U)
TARGET_RGX = re.compile('[\n\s]+', re.U)

# for sentences splitter
TERMINAL_CHARACTERS = [u'.', u'?', u'!']
THE_NUMBERS = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
OPT = 30

# image filter
IMAGE_MIN_WIDTH = 300
IMAGE_MIN_HEIGHT = 200


def get_args():
    # -c / --classifier - <file with classifier>
    # -x / --xpaths - <file with xpaths to delete>
    # -b / --banned - <file with documents not to index>
    # -e / --encode - <compressing algorithm, default='VarByte'>
    parser = argparse.ArgumentParser(\
        description='Inverted index mapper', epilog='by ' + __author__)
    parser.add_argument('-c', '--classifier', help='file with classifier',\
        metavar='<classifier file path>', dest='classifier', required=True, type=str)
    parser.add_argument('-x', '--xpaths', help='file with xpaths to delete',\
        metavar='<xpaths file path>', dest='xpaths', required=False,type=str, default=None)
    parser.add_argument('-b', '--banned', help='file with documents not to index',\
        metavar='<banned documents file path>', dest='banned', required=False,type=str,default=None)
    parser.add_argument('-e', '--encode',help='compressing algorithm: default=VarByte',\
        dest='encode', required=False, default='VarByte', type=str, choices=['VarByte', 'Simple9'])
    return parser.parse_args()

def main():
    args = get_args()

    # hadoop cluster doesn't support the "kill_tags" argument
    script_cleaner = lxml.html.clean.Cleaner(scripts=True,javascript=True,\
        comments=True,style=True,links=True,meta=False,remove_tags=['a', 'img']) #,kill_tags=['script','style'])

    xpaths, banned = [], []

    # better title xpath for lenta
    meta_content_title_xpath = '//meta[@property="og:title"]/@content'

    # standard title xpath
    title_xpath = '/html/head/title/text()'

    # images xpath
    images_xpath = '//img'

    # select encoder
    if args.encode == 'Simple9':
        encoder = Simple9.Simple9
    else:
        encoder = VarByte.VarByte

    # loading sentences splitter classifier
    with open(args.classifier, 'r') as f:
        classifier = pickle.load(f)

    # loading xpaths
    if args.xpaths != None:
        with open(args.xpaths, 'r') as f:
            xpaths = list(set([xpath.strip().decode('utf-8') for xpath in f.readlines()]))

    # loading banned documents list
    if args.banned != None:
        with open(args.banned, 'r') as f:
            banned = [int(doc_id.strip()) for doc_id in f.readlines()]

    for line in sys.stdin:
        doc_id, html_b64encoded = line.split('\t')

        if int(doc_id) in banned:
            continue

        html_text = zlib.decompress(base64.b64decode(html_b64encoded)).decode('utf-8')
        html_structure = lxml.html.document_fromstring(html_text)

        # try get better title
        title_list = html_structure.xpath(meta_content_title_xpath)

        if len(title_list) == 0:
            title_list = html_structure.xpath(title_xpath)
 
        if len(title_list) != 0:
            html_title = title_list[0]
        else:
            html_title = u'Lenta.Ru'

        b64encoded_title = base64.b64encode(html_title.encode('utf-8'))

        # deleteing unnecessary info, including title (if corresponding xpath in xpaths)
        for xpath in xpaths:
            delete_by_xpath(html_structure, xpath)

        # get images list, before cleaning img tags
        images = html_structure.xpath(images_xpath)

        images_url = []

        for image in images:
            try:
                width = int(image.attrib['width'])
                height = int(image.attrib['height'])
                if width >= IMAGE_MIN_WIDTH \
                    and height >= IMAGE_MIN_HEIGHT:
                    images_url.append(base64.b64encode(image.attrib['src']))
            except Exception, e:
                pass

        if len(images_url) == 0:
            images_url.append('0')


        # code from comment https://sfera-mail.ru/blog/Find/611.html#comment2000
        html_structure = script_cleaner.clean_html(html_structure)
        text = " ".join(lxml.etree.XPath("//text()")(html_structure))

        text = re.sub(TARGET_RGX, ' ', text)
        sentences = split(classifier, text)
        b64encoded_sentences = map(lambda sentence: base64.b64encode(sentence.encode('utf-8')), sentences)

        current_position = 0
        sentences_begin_positions = []
        for sentence in sentences:
            sentences_begin_positions.append(current_position)
            words = re.findall(SPLIT_RGX, sentence)
            current_position += len(words)

        # output format
        # <doc id><\tab><b64 encoded title><\tab>
        #   <comma separated base64 encoded list of img urls>
        #   <\tab><comma separated base64 encoded list of sentences>
        #   <\tab><encoded list of sentences begin positions>

        output = doc_id + '\t' + b64encoded_title + '\t' \
                    + ','.join(images_url) + '\t' \
                    + ','.join(b64encoded_sentences) + '\t' \
                    + encoder.encode(sentences_begin_positions,to_diff=True)

        print output


def split(classifier, paragraph):
    begin, sentences = 0, []
    for i in range(len(paragraph)):
        if paragraph[i] not in TERMINAL_CHARACTERS:
            continue

        if i > 0:
            context = paragraph[i - 1: i + 3]
        else:
            continue

        left = i - 1
        while left >= 0 and paragraph[left] not in TERMINAL_CHARACTERS:
            left -= 1

        left_distance = i - left

        right = i + 1
        while right <= len(paragraph) - 1 and paragraph[right] not in TERMINAL_CHARACTERS:
            right += 1

        if i == len(paragraph) - 1:
            right_distance = OPT
        else:
            right_distance = right - i

        x = get_features(context, left_distance, right_distance)

        if classifier.predict(x) == 1:
            sentences.append(paragraph[begin: i + 1].strip())
            begin = i + 2

    if paragraph[begin:] != u'\n':
        sentences.append(paragraph[begin: -1].strip())

    return sentences

def delete_by_xpath(content, xpath):
    for elem in content.xpath(xpath):
        elem.getparent().remove(elem)

if __name__ == '__main__':
    main()
