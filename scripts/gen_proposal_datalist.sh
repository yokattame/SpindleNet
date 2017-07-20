#!/usr/bin/env bash
# Change to the project root directory. Assume this file is at scripts/.
cd $(dirname ${BASH_SOURCE[0]})/../

EXP_DIR=external/exp
DATALISTS_DIR=${EXP_DIR}/datalists

echo "-----jstl_10 train-----"
python RPN/inference.py $DATALISTS_DIR/jstl_10/train.txt $DATALISTS_DIR/jstl_10/train_p.txt jstl_10
echo "-----jstl_10 val-----"
python RPN/inference.py $DATALISTS_DIR/jstl_10/val.txt $DATALISTS_DIR/jstl_10/val_p.txt jstl_10

for dataset in cuhk03 cuhk01 prid viper 3dpes ilids market1501 sensereid; do
  echo "-----${dataset} test_probe-----"
  python RPN/inference.py $DATALISTS_DIR/${dataset}/test_probe.txt $DATALISTS_DIR/${dataset}/test_probe_p.txt ${dataset}
  echo "-----${dataset} test_gallery-----"
  python RPN/inference.py $DATALISTS_DIR/${dataset}/test_gallery.txt $DATALISTS_DIR/${dataset}/test_gallery_p.txt ${dataset}
done

