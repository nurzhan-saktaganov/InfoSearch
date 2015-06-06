# -*- encoding: utf-8 -*-

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
# 19. Расстояние до левого разделителя
# 20. Расстояние до правого разделителя

TERMINAL_CHARACTERS = [u'.', u'?', u'!']
THE_NUMBERS = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
OPT = 30

# Формат context <0: символ слева><1 :терминал><2: символ справав>[<3: необязательный символ>]
def get_features(context, left_distance, right_distance):
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

    # 19. Расстояние до левого разделителя
    X.append(left_distance)

    # 20. Расстояние до правого разделителя
    X.append(right_distance)

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

                        # 19. Расстояние до левого разделителя
                        left = j - 1
                        while left >= 0 \
                                and list_of_sentences[i][left] not in TERMINAL_CHARACTERS:
                            left -= 1
                        left_distance = j - left
                        X.append(left_distance)


                        # 20. Расстояние до правого разделителя
                        right = j + 1
                        while right <= len(list_of_sentences[i]) - 1 \
                                and list_of_sentences[i][right] not in TERMINAL_CHARACTERS:
                            right += 1

                        if right == len(list_of_sentences[i]) \
                                and i < len(list_of_sentences) - 1:
                            tmp = 0
                            while tmp < len(list_of_sentences[i + 1]) - 1 \
                                    and list_of_sentences[i + 1][tmp] not in TERMINAL_CHARACTERS:
                                tmp += 1
                            right += tmp
                        elif right == len(list_of_sentences[i]):
                            right += OPT 

                        right_distance = right - j

                        X.append(right_distance)

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

def print_estimate(y_predicted, y_true):
    tp = fp = tn = fn = 0
    for i in range(len(y_true)):
        if y_predicted[i] == 1 and y_true[i] == 1:
            tp += 1
        elif y_predicted[i] == 1 and y_true[i] == 0:
            fp += 1
        elif y_predicted[i] == 0 and y_true[i] == 1:
            fn += 1
        elif y_predicted[i] == 0 and y_true[i] == 0:
            tn += 1

    print 'tp = %d\nfp = %d\nfn = %d\ntn = %d' % (tp, fp, fn, tn)

    tmp = tp + fp + fn + tn
    if tmp == 0:
        tmp = 0.0
    else:
        tmp = 1.0 * (tp + tn) / tmp
    print 'accuracy  = %lf' % (tmp, )
    
    tmp = tp + fp
    if tmp == 0:
        tmp = 0.0
    else:
        tmp = 1.0 * tp / tmp
    print 'precision = %lf' % (tmp, )
    
    tmp = tp + fn
    if tmp == 0:
        tmp = 0.0
    else:
        tmp = 1.0 * tp / tmp
    print 'recall    = %lf' % (tmp, )
