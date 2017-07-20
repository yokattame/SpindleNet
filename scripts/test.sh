#!/usr/bin/env bash
# Change to the project root directory. Assume this file is at scripts/.
cd $(dirname ${BASH_SOURCE[0]})/../

# Some constants
CAFFE_DIR=external/caffe

EXP_DIR=external/exp
DATALISTS_DIR=${EXP_DIR}/datalists
RESULTS_DIR=${EXP_DIR}/results
SNAPSHOTS_DIR=${EXP_DIR}/snapshots

MODELS_DIR=models

extract_features() {
  local model_name=$1
  local dataset=$2
  local trained_model=$3
  local blob=fc7/spindle

  local result_dir=${RESULTS_DIR}/${model_name}/${dataset}_${blob}
  rm -rf ${result_dir}
  mkdir -p ${result_dir}

  # Extract test probe, and test gallery features.
  for subset in test_probe test_gallery; do
    echo "Extracting ${subset} set"
    local num_samples=$(wc -l ${DATALISTS_DIR}/${dataset}/${subset}.txt | awk '{print $1}')
    local num_iters=$(((num_samples + 99) / 100))
    local tmp_model=${MODELS_DIR}/${model_name}/${model_name}_tmp.prototxt
    sed -e "s/\${dataset}/${dataset}/g; s/\${subset}/${subset}/g" \
      ${MODELS_DIR}/${model_name}/${model_name}_test.prototxt > ${tmp_model}
    ${CAFFE_DIR}/build/tools/extract_features \
      ${trained_model} ${tmp_model} ${blob},label \
      ${result_dir}/${subset}_features_lmdb,${result_dir}/${subset}_labels_lmdb \
      ${num_iters} lmdb GPU 0
    python tools/convert_lmdb_to_numpy.py \
      ${result_dir}/${subset}_features_lmdb ${result_dir}/${subset}_features.npy \
      --truncate ${num_samples}
    python tools/convert_lmdb_to_numpy.py \
      ${result_dir}/${subset}_labels_lmdb ${result_dir}/${subset}_labels.npy \
      --truncate ${num_samples}
    rm ${tmp_model}
  done
}

model_name=spindlenet

trained_model=${SNAPSHOTS_DIR}/${model_name}/${model_name}_iter_50000.caffemodel

# Extract features on all datasets
for dataset in cuhk03 cuhk01 prid viper 3dpes ilids market1501 sensereid; do
  extract_features ${model_name} ${dataset} ${trained_model}
done

# Evaluate performance
for dataset in cuhk03 cuhk01 prid viper 3dpes ilids market1501 sensereid; do
  echo ${dataset} #> ${result_dir}/result.log
  blob=fc7/spindle
  result_dir=${RESULTS_DIR}/${model_name}/${dataset}_${blob}
  python tools/evaluation.py ${result_dir} #> ${result_dir}/result.log
done

