#!/bin/sh

hadoop fs -text ./hw5_sorted_pr/part-00000 | head -n 30 > top30PR.txt
hadoop fs -text ./hw5_sorted_authority/part-00000 | head -n 30 > top30AUTH.txt
hadoop fs -text ./hw5_sorted_hub/part-00000 | head -n 30 > top30HUB.txt
