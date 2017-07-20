import shutil
from argparse import ArgumentParser
from glob import glob
from collections import defaultdict

from utils import *


def main(args):
  # cam_0 to cam_5
  for i in xrange(6):
    mkdir_if_missing(osp.join(args.output_dir, 'cam_' + str(i)))
  # Collect the person_id and view_id into dict
  images = glob(osp.join(args.market1501_dir, 'bounding_box_train', '*.jpg'))
  pdict = defaultdict(lambda: defaultdict(list))
  S = set()
  for imname in images:
    name = osp.basename(imname)
    pid = int(name[:4]) - 1
    vid = int(name[6:7]) - 1
    pdict[pid][vid].append(imname)
    S.add(pid)
  images = glob(osp.join(args.market1501_dir, 'gt_bbox', '*.jpg'))
  for imname in images:
    name = osp.basename(imname)
    pid = int(name[:4]) - 1
    vid = int(name[6:7]) - 1
    if pid in S:
      pdict[pid][vid].append(imname)
  identities = []
  for i, pid in enumerate(pdict):
    vids = pdict[pid].keys()
    p_images = [[] for j in xrange(6)]
    for vid in vids:
      for src_file in pdict[pid][vid]:
        tgt_file = 'cam_{}/{:05d}_{:05d}.jpg'.format(vid, i, len(p_images[vid]))
        shutil.copy(src_file, osp.join(args.output_dir, tgt_file))
        p_images[vid].append(tgt_file)
    identities.append(p_images)
  # Save meta information into a json file
  meta = {'name': 'market1501', 'shot': 'multiple', 'num_cameras': 6}
  meta['identities'] = identities
  write_json(meta, osp.join(args.output_dir, 'meta.json'))
  # Market's test is special. So we just use partial data for train / val.
  split = {'trainval': range(len(identities)),
      'test_probe': [],
      'test_gallery': []}
  write_json(split, osp.join(args.output_dir, 'split.json'))


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Convert the market1501 dataset into the uniform format")
  parser.add_argument(
      'market1501_dir',
      help="Root directory of the market1501 dataset containing bounding_box_train/ and gt_bbox/")
  parser.add_argument(
      'output_dir',
      help="Output directory for the formatted market1501 dataset")
  args = parser.parse_args()
  main(args)

