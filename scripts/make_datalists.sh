#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

EXP=external/exp

for d in 3dpes cuhk01 cuhk02 cuhk03 ilids market1501 prid psdb shinpuhkan viper sensereid; do
  echo "Making $d datalists..."
  python tools/make_lists.py $EXP/datasets/$d $EXP/datalists/$d
done

