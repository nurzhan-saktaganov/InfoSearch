import html2text 
import os 
import codecs
import re


def get_dir_content(dir_name):
    subdirs = []
    for name in os.listdir(dir_name):
        subdirs.append(dir_name + '/' + name + '/')

    html_files_name = []
    just_names = []
    
    for subdir in subdirs:
        html_files_name.append(subdir + os.listdir(subdir)[0])
        just_names.append(os.listdir(subdir)[0])

    #just_names.sort()
    #html_files_name.sort()
    print just_names

    return html_files_name

def open_files(files_name):
    files = []
    for file_name in files_name:
        files.append(codecs.open(file_name, encoding='utf-8', mode='r'))

    return files

def get_html_text(files):

    h2text = html2text.HTML2Text()
    h2text.ignore_links = True
    h2text.ignore_images = True
    h2text.images_to_alt = False

    texts = []
    for elem in files:
        texts.append(re.findall('\w+', h2text.handle(elem.read()), re.U))

    return texts
     
def get_bool_matrix(texts, k_gram):
    dictionary = {}
    bool_row = [0] * len(texts)

    for doc_id in range(len(texts)):
        shingles_count = len(texts[doc_id]) - k_gram + 1
        for i in range(shingles_count):
            shingle = texts[doc_id][i] + texts[doc_id][i+1]
            if (not (shingle in dictionary)):
                dictionary[shingle] = [0] * len(texts)
            dictionary[shingle][doc_id] = 1
    
    bool_matrix = []
    for k, v in dictionary.iteritems():
        bool_matrix.append(v)

    return bool_matrix

def get_jaccar_koef(bool_matrix):
    doc_num = len(bool_matrix[0])
    jaccar_koef = []
    for i in range(doc_num):
        jaccar_koef.append([1] * doc_num)

    for i in range(doc_num):
        for j in range(doc_num):
            if( j > i):
                intersect = 0
                union = 0
                for k in range(len(bool_matrix)):
                    tmp = bool_matrix[k][i] + bool_matrix[k][j]
                    if(tmp == 2):
                        intersect += 1
                    if(tmp > 0):
                        union += 1

                tmp = 1.0 * intersect / union
                #print "%d / %d" % (intersect, union)
                jaccar_koef[i][j] = tmp
                jaccar_koef[j][i] = tmp


    return jaccar_koef

def print_matrix(in_jaccar_koef):
    
    jaccar_koef = []

    for i in range(len(in_jaccar_koef)):
        tmp = []
        for j in range(len(in_jaccar_koef)):
            tmp.append("%.2f" % in_jaccar_koef[i][j])
        print tmp
        #jaccar_koef.append(tmp)

def main():
    rel_dir = 'shingles/shingles-small'
    k_gram = 2

    html_files_name = get_dir_content(rel_dir)
    files = open_files(html_files_name)
    texts = get_html_text(files)
    bool_matrix = get_bool_matrix(texts, k_gram)
    jaccar_koef = get_jaccar_koef(bool_matrix)
    print_matrix(jaccar_koef)

    return 0  
    
   	
main()
