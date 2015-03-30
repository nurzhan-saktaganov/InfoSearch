hadoop fs -rm -r hw2_index

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
	 -file mapper.py reducer.py  VarByte.py Simple9.py\
	 -mapper mapper.py \
	 -reducer reducer.py \
	 -input  /data/sites/lenta.ru/1_10/docs-000.txt \
	 -output hw2_index
