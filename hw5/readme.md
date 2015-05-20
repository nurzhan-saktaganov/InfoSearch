# Построение списка смежности
### ./init/std_mapper.py - Mapper для построения списка смежностей
	Используется скриптом lenta_run.sh
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

# Релизация на примере сайта http://lenta.ru/
### Этап 1. Построение списка смежности
	1.1 В директорию ./init скопировать нужный файл урлов.
	1.2 Переименовать этот файл в lenta_urls.txt
	1.3 Запустить скрипт lenta_run.sh
	
### Этап 2. Вычисление PageRank
	2.1 Запустить скрипт ./PageRank/pagerank_run.sh (делает 5 итераций)
	2.2 Запустить скрипт ./PageRank/sort_pagerank.sh (для сортировки по PR)
	
### Этап 3. Вычисление авторитетов и хабов
	3.1 Запустить скрипт ./HINTS/hints_run.sh (делает 5 итераций)
	3.2 Запустить скрипт ./HINTS/sort_authority.sh
	3.3 Запустить скрипт ./HINTS/sort_hub.sh
	
### Этап 4. Получение топ-30
	4.1 Запустить скрипт ./result/get_result.sh
	(в ./result появится три файла: top30PR.txt,
	top30AUTH.txt, top30HUB.txt)

# Полученные результаты
### ./result/top30PR.txt - топ-30 урлов с максимальным PageRank
	Было сделано 5 итераций

### ./result/top30AUTH.txt - топ-30 урлов с максимальной авторитетностью
	Авторитетность во втором столбце
	Было сделано 5 итераций
	
### ./result/top30HUB.txt - топ-30 урлов с максимальным хабом
	Хаб в третьем столбце
	Было сделано 5 итераций
