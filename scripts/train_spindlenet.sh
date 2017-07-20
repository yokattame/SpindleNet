#!/usr/bin/env bash
# Change to the project root directory. Assume this file is at scripts/.
cd $(dirname ${BASH_SOURCE[0]})/../

# Some constants
CAFFE_DIR=external/caffe

EXP_DIR=external/exp
SNAPSHOTS_DIR=${EXP_DIR}/snapshots
MODELS_DIR=models
LOGS_DIR=logs


model_name=spindlenet

mkdir -p ${LOGS_DIR}/${model_name}
mkdir -p ${SNAPSHOTS_DIR}/${model_name}
  
solver=${MODELS_DIR}/${model_name}/${model_name}_solver.prototxt 
log=${LOGS_DIR}/${model_name}/

pretrained_model1=${SNAPSHOTS_DIR}/head/head_iter_70000.caffemodel
pretrained_model2=${SNAPSHOTS_DIR}/body/body_iter_70000.caffemodel
pretrained_model3=${SNAPSHOTS_DIR}/leg/leg_iter_70000.caffemodel
pretrained_model4=${SNAPSHOTS_DIR}/rarm/rarm_iter_70000.caffemodel
pretrained_model5=${SNAPSHOTS_DIR}/larm/larm_iter_70000.caffemodel
pretrained_model6=${SNAPSHOTS_DIR}/rleg/rleg_iter_70000.caffemodel
pretrained_model7=${SNAPSHOTS_DIR}/lleg/lleg_iter_70000.caffemodel
pretrained_model8=${SNAPSHOTS_DIR}/base/base_iter_70000.caffemodel

GLOG_log_dir=${log} ${CAFFE_DIR}/build/tools/caffe train --solver=${solver} --gpu=0 \
    --weights=${pretrained_model1},${pretrained_model2},${pretrained_model3},${pretrained_model4},${pretrained_model5},${pretrained_model6},${pretrained_model7},${pretrained_model8}

