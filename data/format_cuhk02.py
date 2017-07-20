import shutil
from argparse import ArgumentParser
from glob import glob

from utils import *


def main(args):
  mkdir_if_missing(osp.join(args.output_dir, 'cam_0'))
  mkdir_if_missing(osp.join(args.output_dir, 'cam_1'))
  identities = []
  # cuhk01 is same as P1
  for i in xrange(4):
    cam1_images = glob(osp.join(args.cuhk02_dir, 'P' + str(i + 2), 'cam1', '*.png'))
    cam2_images = glob(osp.join(args.cuhk02_dir, 'P' + str(i + 2), 'cam2', '*.png'))
    cam1_images.sort()
    cam2_images.sort();
    assert len(cam1_images) == len(cam2_images)
    prev_pid = -1
    index = len(identities) - 1
    for name in cam1_images:
      p_id = int(osp.basename(name)[:3])
      if prev_pid != p_id:
        identities.append([[], []])
      p_images = identities[-1]
      file_name = 'cam_0/{:05d}_{:05d}.png'.format(len(identities) - 1, len(p_images[0]))
      shutil.copy(name, osp.join(args.output_dir, file_name))
      p_images[0].append(file_name)
      prev_pid = p_id
    prev_pid = -1
    for name in cam2_images:
      p_id = int(osp.basename(name)[:3])
      if prev_pid != p_id:
        index += 1
      p_images = identities[index]
      file_name = 'cam_1/{:05d}_{:05d}.png'.format(index, len(p_images[1]))
      shutil.copy(name, osp.join(args.output_dir, file_name))
      p_images[1].append(file_name)
      prev_pid = p_id
    # Save meta information into a json file
    meta = {'name': 'cuhk02', 'shot': 'multiple', 'num_cameras': 2}
    meta['identities'] = identities
    write_json(meta, osp.join(args.output_dir, 'meta.json'))
    # We don't test on this dataset. Just use all the data for train / val.
    split = {'trainval': range(len(identities)),
        'test_probe': [],
        'test_gallery': []}
    write_json(split, osp.join(args.output_dir, 'split.json'))


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Convert the CUHK-02 dataset into the uniform format")
  parser.add_argument(
      'cuhk02_dir',
      help="Root directory of the CUHK-02 dataset containing P2/ - P5/")
  parser.add_argument(
      'output_dir',
      help="Output directory for the formatted CUHK-02 dataset")
  args = parser.parse_args()
  main(args)

