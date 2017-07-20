#!/usr/bin/env bash
# Change to the project root directory. Assume this file is at scripts/.
cd $(dirname ${BASH_SOURCE[0]})/../

# Some constants
CAFFE_DIR=external/caffe

EXP_DIR=external/exp
SNAPSHOTS_DIR=${EXP_DIR}/snapshots
MODELS_DIR=models
LOGS_DIR=logs


model_name=lleg

mkdir -p ${LOGS_DIR}/${model_name}
mkdir -p ${SNAPSHOTS_DIR}/${model_name}
  
solver=${MODELS_DIR}/${model_name}/${model_name}_solver.prototxt 
log=${LOGS_DIR}/${model_name}/

pretrained_model=${SNAPSHOTS_DIR}/base/base_iter_70000.caffemodel

GLOG_log_dir=${log} ${CAFFE_DIR}/build/tools/caffe train --solver=${solver} --gpu=3 \
    --weights=${pretrained_model}

