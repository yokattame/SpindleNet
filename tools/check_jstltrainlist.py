import numpy as np
from argparse import ArgumentParser
from collections import defaultdict

from utils import *


def main(args):
  files, labels = read_kv(osp.join(args.jstl_dir, 'train.txt'))

  with open(osp.join(args.jstl_dir, 'sum_id.txt'), 'r') as f:
    sum_id = int(f.readline())

  dic = np.asarray([False for i in xrange(sum_id)])
  pdict = defaultdict(str)
  for i, label in enumerate(labels):
    dic[int(label) - 1] = True
    pid = files[i].split('/')[-1].split('_')[0]
    assert pdict[label] == pid or pdict[label] == ''
    pdict[label] = pid
    
  if dic.all() == True:
    print "The train.txt is good."
  else:
    print "The train.txt is bad."


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Check jstl_x/trainlist")
  parser.add_argument(
      'jstl_dir',
      help="Root directory of the jstl containing train.txt and sum_id.txt")
  args = parser.parse_args()
  main(args)

