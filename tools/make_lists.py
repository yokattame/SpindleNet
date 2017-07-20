import numpy as np
from argparse import ArgumentParser
import os
import os.path as osp

from utils import *


def _get_list(images):
  ret = []
  for img in images:
    label = int(osp.basename(img)[:5])
    ret.append((img, label))
  return np.asarray(ret)


def _save(file_label_list, file_path):
  content = ['{} {}'.format(x, y) for x, y in file_label_list]
  write_list(content, file_path)


def main(args):
  test_probe, test_gallery = [], []
  mkdir_if_missing(args.output_dir)
  if args.dataset_dir.split('/')[-1] != "sensereid":
    meta = read_json(osp.join(args.dataset_dir, 'meta.json'))
    split = read_json(osp.join(args.dataset_dir, 'split.json'))
    identities = np.asarray(meta['identities'])
    # Make train / val.
    # To ensure each identity has at least one training image,
    # we first randomly choose one image per id in train set.
    trainval = identities[split['trainval']]
    train = []
    val = []
    res = []
    for person in trainval:
      vec = []
      for views in person:
        for img in views:
          vec.append(img)
      np.random.shuffle(vec)
      train.append(osp.join(args.dataset_dir, vec[0]))
      for img in vec[1:]:
        res.append(img)
    num_val = int((len(train) + len(res)) * args.val_ratio)
    np.random.shuffle(res)
    for img in res[:num_val]:
      val.append(osp.join(args.dataset_dir, img))
    for img in res[num_val:]:
      train.append(osp.join(args.dataset_dir, img))
    train = _get_list(train)
    val = _get_list(val)
    # Make test probe / gallery. Probe identities should be a subset of
    # gallery's. First half views are probe, others are gallery.
    assert len(set(split['test_probe']) - set(split['test_gallery'])) == 0
    for person in identities[split['test_probe']]:
      for views in person[:len(person) // 2]:
        for img in views:
          test_probe.append(osp.join(args.dataset_dir, img))
      for views in person[len(person) // 2:]:
        for img in views:
          test_gallery.append(osp.join(args.dataset_dir, img))
    only_in_gallery = list(set(split['test_gallery']) - set(split['test_probe']))
    for person in identities[only_in_gallery]:
      for views in person:
        for img in views:
          test_gallery.append(osp.join(args.dataset_dir, img))
  
    if args.dataset_dir.split('/')[-1] == "market1501":
      market_dataset_dir = "external/raw_data/Market-1501-v15.09.15"
      for root, dirs, files in os.walk(osp.join(market_dataset_dir, 'bounding_box_test')):
        for image in files:
          if image.split('.')[-1] == 'jpg':
            if image[0] == '-':
              continue

            name = osp.join(market_dataset_dir, 'bounding_box_test', image)
            label = int(image[0:4])
            test_gallery.append((name, label))
    
      for root, dirs, files in os.walk(osp.join(market_dataset_dir, 'query')):
        for image in files:
          if image.split('.')[-1] == 'jpg':
            if image[0] == '-':
              continue

            name = osp.join(market_dataset_dir, 'query', image)
            label = int(image[0:4])
            test_probe.append((name, label))
      test_probe = np.asarray(test_probe)
      test_gallery = np.asarray(test_gallery)
    else:
      test_probe = _get_list(test_probe)
      test_gallery = _get_list(test_gallery)

    _save(train, osp.join(args.output_dir, 'train.txt'))
    _save(val, osp.join(args.output_dir, 'val.txt'))
  else:
    sensereid_dataset_dir = "external/raw_data/SenseReID"
    for root, dirs, files in os.walk(osp.join(sensereid_dataset_dir, 'test_gallery')):
      for image in files:
        if image.split('.')[-1] == 'jpg':
          name = osp.join(sensereid_dataset_dir, 'test_gallery', image)
          label = int(image[0:5])
          test_gallery.append((name, label))
    
    for root, dirs, files in os.walk(osp.join(sensereid_dataset_dir, 'test_probe')):
      for image in files:
        if image.split('.')[-1] == 'jpg':
          name = osp.join(sensereid_dataset_dir, 'test_probe', image)
          label = int(image[0:5])
          test_probe.append((name, label))

    test_probe = np.asarray(test_probe)
    test_gallery = np.asarray(test_gallery)
  
  if test_gallery.shape[0] != 0:
    _save(test_probe, osp.join(args.output_dir, 'test_probe.txt'))
    _save(test_gallery, osp.join(args.output_dir, 'test_gallery.txt'))


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Create lists of image file and label")
  parser.add_argument(
      'dataset_dir',
      help="Directory of a formatted dataset")
  parser.add_argument(
      'output_dir',
      help="Output directory for the lists")
  parser.add_argument(
      '--val-ratio', type=float, default=0.2,
      help="Ratio between validation and trainval data. Default 0.2.")
  args = parser.parse_args()
  main(args)

