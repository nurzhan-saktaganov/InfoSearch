#!/bin/sh

echo '$> cat ./1_1000/docs-000.txt | python mapper.py | sort -s -k1,1 | python reducer.py > index.txt'
cat ./1_1000/docs-000.txt | python mapper.py | sort -s -k1,1 | python reducer.py > index.txt
