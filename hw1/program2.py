import sys
import random
from urlparse import urlparse
import re

__author__ = 'Nurzhan Saktaganov'

def get_urls(url_file_name, count=0):
    with open(url_file_name) as f:
        urls = f.readlines()

    if count > 0:
        random.shuffle(urls)
        urls = urls[:count]

    for i in range(len(urls)):
        if urls[i][-1] == '\n':
            urls[i] = urls[i][:-1]
        if urls[i][-1] != '/':
            urls[i] += '/'

    return urls


def get_reg_exps(reg_exp_file_name):
    with open(reg_exp_file_name) as f:
        reg_exps = f.readlines()

    for i in range(len(reg_exps)):
        reg_exps[i] = reg_exps[i][:-1]

    return reg_exps


def estimate_purity(good_urls, general_urls, reg_exps):

    sum = 0
    total = 0
    for i in range(len(reg_exps)):
        good = 0
        general = 0
        for url in good_urls:
            if re.match(reg_exps[i], urlparse(url).path):
                good += 1
                total += 1

        for url in general_urls:
            if re.match(reg_exps[i], urlparse(url).path):
                general += 1
                total += 1

        #sys.stdout.write(str( '%.2lf' % (100.0 * (i + 1) / len(reg_exps), )) + '%\r')

        sum += max(good, general)

    sys.stdout.write("\n")

    return  1.0 * sum / (total)

def main():
    file_location = '/home/nurzhan/data/src/sfera/infosearch/hw1/zr.ru/'
    general_url_file_name = file_location + 'urls.zr.general'
    good_url_file_name = file_location + 'urls.zr.examined'
    reg_exp_input_file_name = 'regexp.txt'


    if len(sys.argv) == 4:
        general_url_file_name = sys.argv[1]
        good_url_file_name = sys.argv[2]
        reg_exp_input_file_name = sys.argv[3]

    try:
        good_urls = get_urls(good_url_file_name)
        general_urls = get_urls(general_url_file_name)
        reg_exps = get_reg_exps(reg_exp_input_file_name)

    except IOError, io_error:
        print io_error
        return

    total_purity = 0.0
    iterates_count = 5
    for i in range(iterates_count):
        random.shuffle(good_urls)
        random.shuffle(general_urls)
        purity = estimate_purity(good_urls[:1000], general_urls[:1000], reg_exps)
        print '%d. purity = %.2lf%%' % (i + 1, 100 * purity)
        total_purity += purity

    total_purity /= iterates_count
    print 'total purity = %.2lf%%' %   (100 * total_purity, )

if __name__ == '__main__':
    main()
