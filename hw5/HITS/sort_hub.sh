#! /bin/sh

INPUT='hw5_HINTS_Step_5'
OUTPUT='hw5_sorted_hub'

hadoop fs -rm -r ${OUTPUT}

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
	-D mapred.child.java.opts=-Xmx512M \
	-D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
	-D stream.num.map.output.key.fields=3 \
	-D mapred.text.key.comparator.options=-k3,3nr \
	-D mapred.reduce.tasks=1 \
	-file print.py \
	-input ${INPUT} \
	-output ${OUTPUT} \
	-mapper print.py \
	-reducer org.apache.hadoop.mapred.lib.IdentityReducer
