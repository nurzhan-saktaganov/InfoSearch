__author__ = 'Nurzhan Saktaganov'

import random
import sys
from urlparse import urlparse
import string
import operator
from scipy.cluster.hierarchy import fclusterdata


class URLAnalyzer:
    def __init__(self, list_of_url, alfa=0.1):
        self.list_of_url = list_of_url
        self.features = []
        self.frequency = []
        self.alfa = alfa

    def generate_features(self):
        features_dic = {}
        for url in self.list_of_url:
            parsed_url = urlparse(url)
            segments = parsed_url.path.split('/')[1:]
            if segments[-1] == '':
                segments = segments[:-1]
            # how much segments are here
            key = '_is_url_has_segments/' + str(len(segments))
            if key in features_dic.keys():
                pass  # features_dic[key] += 1
            else:
                pass  # features_dic[key] = 1

            for i in range(len(segments)):
                key = '_is_url_satisfy/' + str(i) + '/' + segments[i]
                if key in features_dic.keys():
                    features_dic[key] += 1
                else:
                    features_dic[key] = 1

                if is_digits(segments[i]):
                    key = '_is_url_satisfy_reg/' + str(i) + '/[0-9]+'
                    if key in features_dic.keys():
                        features_dic[key] += 1
                    else:
                        features_dic[key] = 1

        # {'feature_name':freq, ...} --> [['feature_name', freq], ...] sorted by freq
        sorted_features = sorted(features_dic.items(), key=operator.itemgetter(1), reverse=True)

        for key, frequency in sorted_features:
            self.features.append(key)
            self.frequency.append(frequency)

        features_count = int(self.alfa * len(self.features))
        self.features = self.features[:features_count]
        self.frequency = self.frequency[:features_count]

    def get_url_features(self, url):
        result = []
        for i in range(len(self.features)):
            tmp = self.features[i].split('/')
            if tmp[0] == '_is_url_has_segments':
                result.append(self._is_url_has_segments(url, int(tmp[1])))
            elif tmp[0] == '_is_url_satisfy':
                result.append(self._is_url_satisfy(url, int(tmp[1]), tmp[2]))
            elif tmp[0] == '_is_url_satisfy_reg':
                result.append(self._is_url_satisfy_reg(url, int(tmp[1]), tmp[2]))
            else:
                result.append(0)

        return result

    def _is_url_satisfy(self, url, segment_number, value):
        parsed_url = urlparse(url)
        segments = parsed_url.path.split('/')[1:]
        if segments[-1] == '':
            segments = segments[:-1]

        if len(segments) - 1 < segment_number:
            result = 0
        elif segments[segment_number] == value:
            result = 1
        else:
            result = 0

        return result

    def _is_url_satisfy_reg(self, url, segment_number, regexp):
        parsed_url = urlparse(url)
        segments = parsed_url.path.split('/')[1:]
        if segments[-1] == '':
            segments = segments[:-1]

        if len(segments) - 1 < segment_number:
            result = 0
        elif is_digits(segments[segment_number]):
            result = 1
        else:
            result = 0

        return result

    def _is_url_has_segments(self, url, segment_number):
        parsed_url = urlparse(url)
        segments = parsed_url.path.split('/')[1:]
        if segments[-1] == '':
            segments = segments[:-1]

        if len(segments) == segment_number:
            result = 1
        else:
            result = 0

        return result

    def set_clusters_info(self, clusters_info):
        self.clusters_info = clusters_info

    def generate_regexp(self):
        clusters_description = []
        for cluster in self.clusters_info:
            intersect = [1] * len(cluster[0])
            for vector in cluster:
                for i in range(len(vector)):
                    intersect[i] *= vector[i]
            clusters_description.append(intersect)

        tmp_descriptions = []

        for cluster_description in clusters_description:
            tmp_description = []
            for i in range(len(cluster_description)):
                if cluster_description[i] == 1:
                    tmp_description.append(self.features[i])
            if len(tmp_description) > 0:
                tmp_descriptions.append(tmp_description)
                # print tmp_description

        sorted_tmp_lists = []
        for description in tmp_descriptions:
            tmp_dic = {}
            for elem in description:
                splitted = elem.split('/')
                if splitted[0] == '_is_url_has_segments':
                    tmp_dic['count'] = int(splitted[1])
                else:
                    tmp_dic[int(splitted[1])] = splitted[2]

            sorted_tmp_list = sorted(tmp_dic.items(), key=operator.itemgetter(0))
            sorted_tmp_lists.append(sorted_tmp_list)

        sorted_tmp_lists.sort(key=len, reverse=True)

        reg_exps = []
        for description in sorted_tmp_lists:
            reg_exp = ''
            prev_pos = -1
            for elem in description:
                if elem[0] == 0:
                    reg_exp += '^/' + elem[1]
                elif elem[0] - 1 == prev_pos:
                    reg_exp += '/' + elem[1]
                else:
                    reg_exp += '/.*/' + elem[1]

                prev_pos = elem[0]

            reg_exp += '/.*'

            if not (reg_exp in reg_exps):
                reg_exps.append(reg_exp)

        return reg_exps


def get_urls(url_file_name, count=0):
    with open(url_file_name) as f:
        urls = f.readlines()

    if count > 0:
        random.shuffle(urls)
        urls = urls[:count]

    for i in range(len(urls)):
        if urls[i][-1] == '\n':
            urls[i] = urls[i][:-1]

    return urls


def is_digits(arg):
    result = True
    for char in arg:
        result = result and (char in string.digits)
    return result


def main():
    file_location = '/home/nurzhan/data/src/sfera/infosearch/hw1/zr.ru/'
    general_url_file_name = file_location + 'urls.zr.general'
    good_url_file_name = file_location + 'urls.zr.examined'
    regexp_output_file_name = 'regexp.txt'
    # tmp_file_name = 'tmp_file.txt'
    n_samples = 4000

    if len(sys.argv) == 3:
        general_url_file_name = sys.argv[1]
        good_url_file_name = sys.argv[2]

    try:
        good_urls = get_urls(good_url_file_name, n_samples / 2)
        general_urls = get_urls(general_url_file_name, len(good_urls))

    except IOError, io_error:
        print io_error
        return

    all_urls = good_urls + general_urls
    print 'got %d urls' % (len(all_urls),)

    feature_extractor = URLAnalyzer(all_urls, alfa=0.05 / (1.0 * n_samples / 1000))
    print 'generating features'
    feature_extractor.generate_features()

    vectors = []
    percents = 0
    print 'get urls features'
    for i in range(len(all_urls)):
        vectors.append(feature_extractor.get_url_features(all_urls[i]))
        if i % (n_samples / 100) == 0:
            percents += 1
            sys.stdout.write(str(percents) + '%\r')
    sys.stdout.write("\n")

    print 'clusterization'
    clusters = fclusterdata(X=vectors, t=0.3, metric='jaccard', criterion='distance')
    tmp_dic = {}
    for i in clusters:
        tmp_dic[i] = 1

    # tmp_file = open(tmp_file_name, 'w')
    tmp_list = tmp_dic.keys()[:]
    print 'generated %d clusters' % (len(tmp_list),)

    clusters_list = []
    for n in tmp_list:
        # tmp_file.write('----------new cluster -------------------\n')
        cluster = []
        for i in range(len(clusters)):
            if n == clusters[i]:
                # tmp_file.write(all_urls[i] + '\n')
                cluster.append(vectors[i])
        clusters_list.append(cluster)

    feature_extractor.set_clusters_info(clusters_list)
    reg_exps = feature_extractor.generate_regexp()
    reg_exps_output_file = open(regexp_output_file_name, 'w')
    print 'generated %d uniq reg_exp' % (len(reg_exps),)
    for reg_exp in reg_exps:
        reg_exps_output_file.write(reg_exp + '\n')
        # print reg_exp

if __name__ == '__main__':
    main()