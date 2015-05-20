#! /bin/sh

INPUT='/data/sites/lenta.ru/all/docs*'
OUTPUT='./hw5_raw_graph'

hadoop fs -rm -r ${OUTPUT}

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
	-file ./init \
	-mapper "./init/std_mapper.py ./init/lenta_urls.txt http://lenta.ru/" \
	-reducer NONE \
	-input ${INPUT} \
	-output ${OUTPUT}
