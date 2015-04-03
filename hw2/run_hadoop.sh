#!/bin/sh
#rm -r hw2_files
mkdir hw2_files
cp mapper.py hw2_files/
cp reducer.py hw2_files/
cp VarByte.py hw2_files/
cp Simple9.py hw2_files/

hadoop fs -rm -r hw2_index

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
	 -file ./hw2_files \
	 -mapper ./hw2_files/mapper.py \
	 -reducer ./hw2_files/reducer.py \
	 -input  /data/sites/lenta.ru/all/docs* \
	 -output hw2_index
