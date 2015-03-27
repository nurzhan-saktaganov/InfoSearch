#!/bin/bash
# lenta.ru povarenok.ru zr.ru
pr1='lenta.ru'
pr2='povarenok.ru'
pr3='zr.ru'

project=$pr3
mkdir index
echo '$> cat ./1_1000/'$project'/docs-000.txt | python mapper.py | sort -s -k1,1 | python reducer.py > index/'$project'.txt'
cat ./1_1000/${project}/docs-000.txt | python mapper.py | sort -s -k1,1 | python reducer.py > index/${project}.txt
rm VarByte.pyc Simple9.pyc

