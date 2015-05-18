#! /bin/sh

# -D mapreduce.job.reduces=2

INPUT='./hw5_raw_graph'
OUTPUT='./hw5_PageRank_Step_0'

hadoop fs -rm -r ${OUTPUT}
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
	-file init_mapper.py reducer.py \
	-mapper init_mapper.py \
	-reducer reducer.py \
	-input ${INPUT} \
	-output ${OUTPUT} \
	-numReduceTasks 8

for ((i=1;i<=5;i++))
do
	INPUT=${OUTPUT}
	OUTPUT='./hw5_PageRank_Step_'${i}

	hadoop fs -rm -r ${OUTPUT}
	hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
		-file mapper.py reducer.py \
		-mapper mapper.py \
		-reducer reducer.py \
		-input ${INPUT} \
		-output ${OUTPUT} \
		-numReduceTasks 8
		
	hadoop fs -rm -r ${INPUT}
done
