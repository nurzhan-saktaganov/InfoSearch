#! /bin/sh

INPUT='./hw5_raw_graph'
OUTPUT='./hw5_HINTS_Step_0'

hadoop fs -rm -r ${OUTPUT}
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
	-file init_mapper.py init_reducer.py \
	-mapper init_mapper.py \
	-reducer init_reducer.py \
	-input ${INPUT} \
	-output ${OUTPUT} \
	-numReduceTasks 16

for ((i=1;i<=5;i++))
do
	INPUT=${OUTPUT}
	OUTPUT='./hw5_HINTS_Step_'${i}

	hadoop fs -rm -r ${OUTPUT}
	hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
		-D mapred.child.java.opts=-Xmx512M \
		-file mapper.py reducer.py \
		-mapper mapper.py \
		-reducer reducer.py \
		-input ${INPUT} \
		-output ${OUTPUT} \
		-numReduceTasks 16

	hadoop fs -rm -r ${INPUT}
done
