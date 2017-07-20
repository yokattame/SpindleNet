import numpy as np
from argparse import ArgumentParser

from utils import *


def main(args):
  id_offset = 0
  merged_train_kv = {}
  merged_val_kv = {}
  for datalist_dir in args.datalist_dirs:
    train_files, train_labels = read_kv(osp.join(datalist_dir, 'train.txt'))
    val_files, val_labels = read_kv(osp.join(datalist_dir, 'val.txt'))
    unique_ids = set(map(int, train_labels + val_labels))
    id_mapping = {idx: i + id_offset for i, idx in enumerate(unique_ids)}
    for k, v in zip(train_files, train_labels):
      merged_train_kv[k] = id_mapping[int(v)]
    for k, v in zip(val_files, val_labels):
      merged_val_kv[k] = id_mapping[int(v)]
    id_offset += len(id_mapping)
  mkdir_if_missing(osp.join(args.output_dir))
  write_kv(merged_train_kv.keys(), map(str, merged_train_kv.values()),
      osp.join(args.output_dir, 'train.txt'))
  write_kv(merged_val_kv.keys(), map(str, merged_val_kv.values()),
      osp.join(args.output_dir, 'val.txt'))
  print "Max ID:", id_offset
  with open(osp.join(args.output_dir, 'sum_id.txt'), 'w') as f:
    f.write(str(id_offset) + '\n')


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Merge multiple lists of train / val image file and "
      "label into a single-task one")
  parser.add_argument(
      '--datalist-dirs', type=str, nargs='+',
      help="Datalist directories containing train.txt and val.txt.")
  parser.add_argument(
      'output_dir',
      help="Output directories for the lists")
  args = parser.parse_args()
  assert args.datalist_dirs != None
  main(args)

