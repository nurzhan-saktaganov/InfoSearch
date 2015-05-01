# Построение обратного индекса
### mapper.py - Mapper для построения обратного индекса
	Принимает один параметр - путь к файлу со списком стоп-слов,
	где каждое стоп-слово на отдельной строке.

### reducer.py - Reducer для построения обратного индекса 
	Принимает один необязательный параметр, 
	который может быть VarByte или Simple9.
	Значение по умолчанию - VarByte.
	
# Построение прямого индекса
### forward_mapper.py - Mapper для построения прямого индекса
	Принимает один параметр - путь к файлу со списком стоп-слов,
	где каждое стоп-слово на отдельной строке. Reducer не требуется.

# Подготовка стоп-слов
### stop_words_uniq.py - унификатор стоп-слов
	В стандартный ввод подаются стоп-слова,
	где каждое стоп-слово на отдельной строке.
	Используется когда есть несколько источников стоп-слов. Например:
    $ cat source1.txt source2.txt | python stop_words_uniq.py > result.txt

### stop_words_final.txt - стоп-слова, использованные мною
    Источник: https://code.google.com/p/stop-words/
    Версия: stop-words-collection-2014-02-24.zip
    Взятые файлы:
        * stop-words_chinese_1_zh.txt
        * stop-words_english_1_en.txt
        * stop-words_english_2_en.txt
        * stop-words_english_3_en.txt
        * stop-words_english_4_google_en.txt
        * stop-words_english_5_en.txt
        * stop-words_english_6_en.txt
        * stop-words_japanese_1_ja.txt
        * stop-words_russian_1_ru.txt
        * stop-words_russian_2_ru.txt
        
# Подготовка оценок асессоров
### filter_marks.py - фильтрация оценок асессоров
    Параметры:
    -h, --help - вывод help
    -m <marks file>, --marks <marks file> - файл с оценками асессоров
    -u <urls file>, --urls <urls file> - файл cо списком пар doc_id url
    -o <output>, --output <output> - файл, в который пишется результат

# Предобработка прямого и обратного индексов
### prepare_data.py - подготовка словаря и других мета-данных
    -h, --help - вывод help
    -i <inverted index>, --invert <inverted index> - файл с обратным индексом
    -u <urls file>, --urls <urls file> - файл cо списком пар doc_id url
    -f <forward index>,--forward <forward index> - файл с прямым индексом
    -o <output>, --output <output> - файл, в который пишется результат

### DictionaryBuilder.py - вспомогательный класс для prepare_data.py

# Эволюционный подбор параметров
### prepare_evolution_trainer.py - подготовка данных для эволюционного поиска
    -h, --help - вывод help
    -p <prepared file path>, --prepared <prepared file path> - файл результата prepare_data.py
    -i <inverted index>, --invert <inverted index> - файл с обратным индексом
    -m <filtered marks>, --marks <filtered marks> - файл результата filter_marks.py
    -c {VarByte,Simple9}, --compress {VarByte,Simple9} - метод сжатия в обратном индексе.
    Необязательный параметр, по умолчанию VarByte
    -o <output>, --output <output> - файл, в который пишется результат

### evolution_trainer.py - эволюционный подбор параметров
    -h, --help - вывод help
    -t <train file>, --train <train file> - файл результата prepare_evolution_trainer.py
    -s <settings file>, --settings <settings file> - файл настроек эволюционного подбора
    -o <output>, --output <output> - файл, в который пишется результат
    
### Genetic.py - вспомогательный класс для evolution_trainer.py

### settings.txt - использованный файл настроек эволюционного подбора
    Файл настроек может содержать:
        MAX_GENERATIONS <максимальное количество поколений>
        POPULATION_SIZE <размер популяции>
        CHILDREN_COUNT <количество детей, не меньше чем POPULATION_SIZE / 2>
        MUTATION_POSSIBILITY <вероятность мутации>
    Каждая пара параметр-значение на отдельной строке. Параметр и значение разделены пробелом.
    
# Поиск
### find.py - утилита поиска
    -h, --help - вывод help
    -p <prepared file path>, --prepared <prepared file path> - файл результата prepare_data.py
    -i <inverted index>, --invert <inverted index> - файл с обратным индексом
    -e <estimates file>, --estimates <estimates file> - файл результата evolution_trainer.py
    -f <forward index>,--forward <forward index> - файл с прямым индексом.
    Теперь не используется, необязательный параметр
    -c {VarByte,Simple9}, --compress {VarByte,Simple9} - метод сжатия в обратном индексе.
    Необязательный параметр, по умолчанию VarByte
    