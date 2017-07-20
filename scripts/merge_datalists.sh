#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

EXP=external/exp
DATALISTS=$EXP/datalists

python tools/merge_lists.py \
    $DATALISTS/jstl_10 \
    --datalist-dirs $DATALISTS/3dpes $DATALISTS/cuhk01 $DATALISTS/cuhk02 \
        $DATALISTS/cuhk03 $DATALISTS/ilids $DATALISTS/market1501 \
        $DATALISTS/prid $DATALISTS/psdb $DATALISTS/shinpuhkan $DATALISTS/viper

python tools/check_jstltrainlist.py $DATALISTS/jstl_10

