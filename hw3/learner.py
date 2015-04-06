#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import lxml.etree
from sklearn.ensemble import RandomForestClassifier

__author__ = 'Nurzhan Saktaganov'

TERMINAL_CHARACTERS = [u'.', u'?', u'!']
THE_NUMBERS = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']

def help():
    print 'Options:\n -s\t<source file>\n'

# Базовые правила
# 1. Тип разделителя: точка, вопросительный знак, восклиательный знак - 0, 1, 2
# 2. Наличие пробела слева
# 3. Наличие пробела справа
# 4. Символ пунктуации слева
# 5. Символ пунктуации справа
# 6. Цифра слева
# 7. Цифра справа
# 8. Прописная буква слева
# 9. Прописная буква справа
# 10. Строчная буква слева
# 11. Строчная буква справа
# 12. Открывающая скобка слева
# 13. Открывающая скобка справа
# 14. Закрывающая скобка слева
# 15. Закрывающая скобка справа
# 16. Титул справа
# 17. Слово справа с прописной буквы
# 18. Конец абзаца справа
# 19. Расстояние до левой точки
# 20. Расстояние до правой точки

def main():
    classifier = RandomForestClassifier(n_estimators=15 \
        , criterion='gini', max_features='auto', n_jobs=1)

    source_path = get_source_path()
    to_split_path = './input.txt'

    tree = lxml.etree.parse(source_path)
    root = tree.getroot()

    training_set_X, training_set_y = get_training_set(root)

    classifier.fit(training_set_X, training_set_y)

    for i in range(len(training_set_X)):
        pass #print training_set_X[i] + [training_set_y[i]]

    to_split = open(to_split_path, 'r')
    for line in to_split:
        line = line.decode('utf-8')
        begin = 0
        for i in range(len(line)):
            if line[i] not in TERMINAL_CHARACTERS:
                continue

            if i > 0:
                context = line[i - 1: i + 3]
            else:
                continue #context = '\r' + line[i: i + 3]
            x = get_features(context)
            if classifier.predict(x) == 1:
                print line[begin: i + 1].encode('utf-8')
                begin = i + 2

        if line[begin:] != u'\n':
            print line[begin:-1].encode('utf-8')


            #print line[i - 1: i + 3]


# Формат context <0: символ слева><1 :терминал><2: символ справав>[<3: необязательный символ>]
def get_features(context):
    X = []
    
    # 1. Тип разделителя: точка, вопросительный знак, восклицательный знак - 0, 1, 2
    X.append(TERMINAL_CHARACTERS.index(context[1]))

    
    # 2. Наличие пробела слева
    if context[0] == u' ':
        X.append(1)
    else:
        X.append(0)
    
    # 3. Наличие пробела справа
    if context[2] == u' ':
        X.append(1)
    else:
        X.append(0)

    # 4. Символ пунктуации слева
    if context[0] in TERMINAL_CHARACTERS:
        X.append(1)
    else:
        X.append(0)

    # 5. Символ пунктуации справа
    if context[2] in TERMINAL_CHARACTERS:
        X.append(1)
    else:
        X.append(0)

    # 6. Цифра слева
    if context[0] in THE_NUMBERS:
        X.append(1)
    else:
        X.append(0)

    # 7. Цифра справа
    if context[2] in THE_NUMBERS:
        X.append(1)
    else:
        X.append(0)

    # 8. Прописная буква слева
    if context[0] != context.lower():
        X.append(1)
    else:
        X.append(0)

    # 9. Прописная буква справа
    if context[2] != context.lower():
        X.append(1)
    else:
        X.append(0)

    # 10. Строчная буква слева
    if context[0] != context.upper():
        X.append(1)
    else:
        X.append(0)

    # 11. Строчная буква справа
    if context[2] != context.upper():
        X.append(1)
    else:
        X.append(0)

    # 12. Открывающая скобка слева
    if context[0] == u'(':
        X.append(1)
    else:
        X.append(0)

    # 13. Открывающая скобка справа
    if context[2] == u'(':
        X.append(1)
    else:
        X.append(0)

    # 14. Закрывающая скобка слева
    if context[0] == u')':
        X.append(1)
    else:
        X.append(0)

    # 15. Закрывающая скобка справа
    if context[2] == u')':
        X.append(1)
    else:
        X.append(0)

    # 16. Титул справа
    if len(context) == 4 and context[3] != context[3].upper():
        X.append(1)
    else:
        X.append(0)

    # 17. Слово справа с прописной буквы
    if len(context) == 4 and context[3] != context[3].lower():
        X.append(1)
    else:
        X.append(0)

    # 18. Конец абзаца справа
    if context[2] == u'\n':
        X.append(1)
    else:
        X.append(0)

    return X


    
def get_training_set(xml_root):

    training_set_X = []
    training_set_y = []
    
    texts = get_part(xml_root, 'text')

    for text in texts:
        #print '----NEW TEXT'
        chapters = get_part(text, 'paragraphs')
        for chapter in chapters:
            #print '----NEW CHAPTER'
            paragraphs = get_part(chapter, 'paragraph')
            for paragraph in paragraphs:
                #print '----NEW PARAGRAPH'
                sentences = get_part(paragraph, 'source')
                list_of_sentences = []
                for sentence in sentences:
                    list_of_sentences.append(sentence.text)
                list_of_sentences[-1] = list_of_sentences[:-1]
                
                for i in range(len(list_of_sentences)):
                    for j in range(len(list_of_sentences[i])):
                        if list_of_sentences[i][j] not in TERMINAL_CHARACTERS:
                            continue

                        X = []

                        # 1. Тип разделителя: точка, вопросительный знак, восклиательный знак - 0, 1, 2
                        X.append(TERMINAL_CHARACTERS.index(list_of_sentences[i][j]))

                        # 2. Наличие пробела слева
                        if j > 0 and list_of_sentences[i][j - 1] == u' ':
                            X.append(1)
                        else:
                            X.append(0)

                        # 3. Наличие пробела справа
                        if (j == len(list_of_sentences[i]) - 1 and i < len(list_of_sentences) - 1) \
                                or (j < len(list_of_sentences[i]) - 1 and list_of_sentences[i][j + 1] == u' '):
                            X.append(1)
                        else:
                            X.append(0)

                        # 4. Символ пунктуации слева
                        if j > 0 and list_of_sentences[i][j - 1] in TERMINAL_CHARACTERS:
                            X.append(1)
                        else:
                            X.append(0)

                        # 5. Символ пунктуации справа
                        if j < len(list_of_sentences[i]) - 1 and list_of_sentences[i][j + 1] in TERMINAL_CHARACTERS:
                            X.append(1)
                        else:
                            X.append(0)

                        # 6. Цифра слева
                        if j > 0 and list_of_sentences[i][j - 1] in THE_NUMBERS:
                            X.append(1)
                        else:
                            X.append(0)

                        # 7. Цифра справа
                        if j < len(list_of_sentences[i]) - 1 and list_of_sentences[i][j + 1] in THE_NUMBERS:
                            X.append(1)
                        else:
                            X.append(0)

                        # 8. Прописная буква слева
                        if j > 0 and list_of_sentences[i][j - 1].lower() != list_of_sentences[i][j - 1]:
                            X.append(1)
                        else:
                            X.append(0)

                        # 9. Прописная буква справа
                        if j < len(list_of_sentences[i]) - 1 and \
                                list_of_sentences[i][j + 1].lower() != list_of_sentences[i][j + 1]:
                            X.append(1)
                        else:
                            X.append(0)

                        # 10. Строчная буква слева
                        if j > 0 and list_of_sentences[i][j - 1].upper() != list_of_sentences[i][j - 1]:
                            X.append(1)
                        else:
                            X.append(0)

                        # 11. Строчная буква справа
                        if j < len(list_of_sentences[i]) - 1 and \
                                list_of_sentences[i][j + 1].upper() != list_of_sentences[i][j + 1]:
                            X.append(1)
                        else:
                            X.append(0)

                        # 12. Открывающая скобка слева
                        if j > 0 and list_of_sentences[i][j - 1] == u'(':
                            X.append(1)
                        else:
                            X.append(0)

                        # 13. Открывающая скобка справа
                        if j < len(list_of_sentences[i]) - 1 and list_of_sentences[i][j + 1] == u'(':
                            X.append(1)
                        else:
                            X.append(0)

                        # 14. Закрывающая скобка слева
                        if j > 0 and list_of_sentences[i][j - 1] == u')':
                            X.append(1)
                        else:
                            X.append(0)

                        # 15. Закрывающая скобка справа
                        if j < len(list_of_sentences[i]) - 1 and list_of_sentences[i][j + 1] == u')':
                            X.append(1)
                        else:
                            X.append(0)

                        # 16. Титул справа
                        if j < len(list_of_sentences[i]) - 2 \
                                and list_of_sentences[i][j + 1] == u' ' \
                                and  list_of_sentences[i][j + 2].upper() != list_of_sentences[i][j + 2]:
                            X.append(1)
                        else:
                            X.append(0)

                        # 17. Слово справа с прописной буквы
                        if (j < len(list_of_sentences[i]) - 2 \
                                    and list_of_sentences[i][j + 1] == u' ' \
                                    and list_of_sentences[i][j + 2].lower() != list_of_sentences[i][j + 2]) \
                                or (j == len(list_of_sentences[i]) - 1 \
                                    and i < len(list_of_sentences) - 1 \
                                    and len(list_of_sentences[i + 1]) > 0 \
                                    and list_of_sentences[i + 1][0].lower() != list_of_sentences[i + 1][0]):
                            X.append(1)
                        else:
                            X.append(0)


                        # 18. Конец абзаца справа
                        if j == len(list_of_sentences[i]) - 1 and i == len(list_of_sentences):
                            X.append(1)
                        else:
                            X.append(0)

                        #X.append(left)

                        #X.append(right)

                        # Вектор признаков для текущего разделителя
                        training_set_X.append(X)

                        # Признак конца предложения
                        if j == len(list_of_sentences[i]) - 1:
                            training_set_y.append(1)
                        else:
                            training_set_y.append(0)

    return training_set_X, training_set_y

def get_part(etree_node, part):
    for node in etree_node.findall('.//' + part):
        yield node

def get_source_path():
    if len(sys.argv) > 2 \
        or (len(sys.argv) == 2 \
            and (sys.argv[1] == '--help' \
                 or sys.argv[1] == '-h')):
        help()
        exit()
    elif len(sys.argv) == 2:
        source_path = sys.argv[1]
    else:
        source_path = './part_sentences.xml'
    return source_path

if __name__ == '__main__':
    main()