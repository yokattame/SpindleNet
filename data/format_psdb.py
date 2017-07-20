import numpy as np
from argparse import ArgumentParser
from scipy.misc import imread
from scipy.misc import imsave

from utils import *


def main(args):
  try:
    from scipy.io import loadmat
    matdata = loadmat(osp.join(args.psdb_dir, 'person.mat'))
  except:
    from hdf5storage import loadmat
    matdata = loadmat(osp.join(args.psdb_dir, 'person.mat'))
  mkdir_if_missing(osp.join(args.output_dir, 'cam_0'))
  mkdir_if_missing(osp.join(args.output_dir, 'cam_1'))
  identities = []
  # Randomly choose half of the images as cam_0, others as cam_1
  for person in matdata['person'].squeeze():
    pid = person[0].squeeze()
    imname = person[1].squeeze()
    bbox = person[2].squeeze()
    num = imname.shape[0]
    images = []
    for i in xrange(num):
      image = imread(osp.join(args.psdb_dir, 'images', imname[i][0]))
      crop_image = image[int(bbox[i][1]):int(bbox[i][1]) + int(bbox[i][3]), int(bbox[i][0]):int(bbox[i][0]) + int(bbox[i][2])]
      images.append(crop_image)
    np.random.shuffle(images)
    p_images = [[], []]
    for image in images[:(num // 2)]:
      file_name = 'cam_0/{:05d}_{:05d}.bmp'.format(pid - 1, len(p_images[0]))
      imsave(osp.join(args.output_dir, file_name), image)
      p_images[0].append(file_name)
    for image in images[(num // 2):]:
      file_name = 'cam_1/{:05d}_{:05d}.bmp'.format(pid - 1, len(p_images[1]))
      imsave(osp.join(args.output_dir, file_name), image)
      p_images[1].append(file_name)
    identities.append(p_images)
  # Save meta information into a json file
  meta = {'name': 'psdb', 'shot': 'multiple', 'num_cameras': 2}
  meta['identities'] = identities
  write_json(meta, osp.join(args.output_dir, 'meta.json'))
  # We don't test on this dataset. Just use all the data for train / val.
  split = {
      'trainval': range(len(identities)),
      'test_probe': [],
      'test_gallery': []}
  write_json(split, osp.join(args.output_dir, 'split.json'))


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Convert the psdb dataset into the uniform format")
  parser.add_argument(
      'psdb_dir',
      help="Root directory of the psdb dataset containing person.mat")
  parser.add_argument(
      'output_dir',
      help="Output directory for the formatted psdb dataset")
  args = parser.parse_args()
  main(args)

