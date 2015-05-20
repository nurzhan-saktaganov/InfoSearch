# Обнаружена ошибка, после исправления это сообщение будет удалено

# Построение списка смежностей (граф ссылок)
### std_mapper.py - Mapper для построения списка смежностей
 	Принимает два позиционных параметра:
 	1. Файл urls.txt, то есть файл пар: <doc_id><\tab><url>
 	2. Имя сайта в виде http://site.dom/
  
 	Reducer - не требуется
 
# Алгоритм PageRank
### ./PageRank/init_mapper.py - первичный mapper
	На вход подавать выход std_mapper.py
	
### ./PageRank/mapper.py - mapper, вызываемый итеративно
	На вход подавать выход reducer.py
	
### ./PageRank/reducer.py - первичный и итеративный reducer
	Также исполняет роль init_reducer.py для init_mapper.py
	На вход подавать выход init_mapper.py или mapper.py
	
# Алгоритм HINTS
### ./HINTS/init_mapper.py - первичный mapper
	На вход подавать выход std_mapper.py

### ./HINTS/init_reducer.py - первичный reducer
	На вход подавать выход init_mapper.py

### ./HINTS/mapper.py - итеративный mapper
	На вход подавать выход init_reducer.py или reducer.py

### ./HINTS/reducer.py - итеративный reducer
	На вход подавать выход mapper.py
