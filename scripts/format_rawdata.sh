#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

RAW=external/raw_data
EXP=external/exp

echo "Formatting CUHK03 ..."
if [ ! -d "$RAW/cuhk03_release" ]; then
  unzip -q -d $RAW/ $RAW/cuhk03_release.zip
fi
# Save the matfile in the v7 format to fast computation
cd $RAW/cuhk03_release
matlab -nodisplay -nojvm -nosplash -r "load('cuhk-03.mat'); save('cuhk-03.mat', 'detected', 'labeled', 'testsets', '-v7'); exit;"
cd -
python data/format_cuhk03.py $RAW/cuhk03_release $EXP/datasets/cuhk03

echo "Formatting CUHK01 ..."
if [ ! -d "$RAW/cuhk01" ]; then 
  unzip -q -d $RAW/cuhk01/ $RAW/CUHK01.zip
fi
python data/format_cuhk01.py $RAW/cuhk01 $EXP/datasets/cuhk01

echo "Formatting PRID ..."
if [ ! -d "$RAW/prid" ]; then
  unzip -q -d $RAW/prid/ $RAW/prid_2011.zip
fi
python data/format_prid.py $RAW/prid $EXP/datasets/prid

echo "Formatting VIPeR ..."
if [ ! -d "$RAW/VIPeR" ]; then 
  unzip -q -d $RAW/ $RAW/VIPeR.v1.0.zip
fi
python data/format_viper.py $RAW/VIPeR $EXP/datasets/viper

echo "Formatting 3DPeS ..."
if [ ! -d "$RAW/3DPeS" ]; then 
  unzip -q -d $RAW/ $RAW/3DPeS_ReId_Snap.zip
fi
python data/format_3dpes.py $RAW/3DPeS $EXP/datasets/3dpes

echo "Formatting i-LIDS ..."
if [ ! -d "$RAW/i-LIDS" ]; then 
  tar -xf $RAW/i-LIDS.tar.gz -C $RAW/
fi
python data/format_ilids.py $RAW/i-LIDS $EXP/datasets/ilids

echo "Formatting Shinpuhkan ..."
if [ ! -d "$RAW/Shinpuhkan2014dataset" ]; then
  unzip -q -d $RAW/ $RAW/Shinpuhkan2014dataset.zip
fi
python data/format_shinpuhkan.py $RAW/Shinpuhkan2014dataset $EXP/datasets/shinpuhkan

echo "Formatting CUHK02 ..."
if [ ! -d "$RAW/cuhk02" ]; then
  tar -xf $RAW/cuhk02.tar.gz -C $RAW/
fi
python data/format_cuhk02.py $RAW/cuhk02 $EXP/datasets/cuhk02

echo "Formatting psdb..."
if [ ! -d "$RAW/psdb" ]; then 
  tar -xf $RAW/psdb.tar -C $RAW/
fi
# Save the matfile in the v7 format to fast computation
cd $RAW/psdb
matlab -nodisplay -nojvm -nosplash -r "load('person.mat'); save('person.mat', 'person', '-v7'); exit;"
cd -
python data/format_psdb.py $RAW/psdb $EXP/datasets/psdb

echo "Formatting Market-1501..."
if [ ! -d "$RAW/Market-1501-v15.09.15" ]; then
  unzip -q -d $RAW/ $RAW/Market-1501-v15.09.15.zip
fi
python data/format_market1501.py $RAW/Market-1501-v15.09.15 $EXP/datasets/market1501

echo "Formatting SenseReID.zip..."
if [ ! -d "$RAW/SenseReID" ]; then
  unzip -q -d $RAW/ $RAW/SenseReID.zip
fi

