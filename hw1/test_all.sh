#!/bin/bash
declare projects=("kinopoisk" "lenta" "povarenok" "wikipedia" "zr")

files_path="./"
regexp_file="regexp.txt"

for project in "${projects[@]}"
do
	general_url="$files_path$project.ru/urls.$project.general"
	examined_url="$files_path$project.ru/urls.$project.examined"
	rm $regexp_file
	echo "PROJECT $project:"
	echo "$ python program1.py $general_url $examined_url"
	python program1.py $general_url $examined_url
	echo "$ sleep 2"
	sleep 2
	echo "$ python program2.py $general_url $examined_url $regexp_file"
	python program2.py $general_url $examined_url $regexp_file
	echo "$ sleep 2"
	sleep 2
	echo "-----------------------------------------------------"
done 