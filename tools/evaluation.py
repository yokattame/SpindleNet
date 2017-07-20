import numpy as np
from argparse import ArgumentParser
from sklearn.metrics.pairwise import pairwise_distances

from utils import *


def _cmc_core(D, G, P, k):
  order = np.argsort(D, axis=0)
  res = np.zeros((k, D.shape[1]))
  for i in xrange(k):
    for j in xrange(D.shape[1]):
      if G[order[i][j]] == P[j]:
        res[i][j] += 1
  return (res.sum(axis=1) * 1.0 / D.shape[1]).cumsum()


def _get_test_data(result_dir):
  PF = np.load(osp.join(result_dir, 'test_probe_features.npy'))
  PL = np.load(osp.join(result_dir, 'test_probe_labels.npy'))
  GF = np.load(osp.join(result_dir, 'test_gallery_features.npy'))
  GL = np.load(osp.join(result_dir, 'test_gallery_labels.npy'))
  # Reassign the labels to make them sequentially numbered from zero
  unique_labels = np.unique(np.r_[PL, GL])
  labels_map = {l: i for i, l in enumerate(unique_labels)}
  PL = np.asarray([labels_map[l] for l in PL])
  GL = np.asarray([labels_map[l] for l in GL])
  return PF, PL, GF, GL


def main(args):
  PF, PL, GF, GL = _get_test_data(args.result_dir)
  D = pairwise_distances(GF, PF, metric=args.method, n_jobs=-2)

  gallery_labels_set = np.unique(GL)

  for label in PL:
    if label not in gallery_labels_set:
      print 'Probe-id is out of Gallery-id sets.'

  Times = 100
  k = 20

  res = np.zeros(k)

  gallery_labels_map = [[] for i in xrange(gallery_labels_set.size)]
  for i, g in enumerate(GL):
    gallery_labels_map[g].append(i)

  for __ in xrange(Times):
    # Randomly select one gallery sample per label selected
    newD = np.zeros((gallery_labels_set.size, PL.size))
    for i, g in enumerate(gallery_labels_set):
      j = np.random.choice(gallery_labels_map[g])
      newD[i, :] = D[j, :]
    # Compute CMC
    res += _cmc_core(newD, gallery_labels_set, PL, k)
  res /= Times

  for topk in [1, 5, 10, 20]:
    print "{:8}{:8.1%}".format('top-' + str(topk), res[topk - 1])


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Evaluate performance")
  parser.add_argument(
      'result_dir',
      help="Result directory. Containing extracted features and labels. ")
  parser.add_argument(
      '--method',
      choices=['euclidean', 'cosine'],
      default='cosine')
  args = parser.parse_args()
  main(args)

