import os
import os.path as osp
import json
import codecs


def mkdir_if_missing(d):
  if not osp.isdir(d):
    os.makedirs(d)


def read_list(file_path, coding=None):
  if coding is None:
    with open(file_path, 'r') as f:
      arr = [line.strip() for line in f.readlines()]
  else:
    with codecs.open(file_path, 'r', coding) as f:
      arr = [line.strip() for line in f.readlines()]
  return arr


def write_list(arr, file_path, coding=None):
  arr = ['{}'.format(item) for item in arr]
  if coding is None:
    with open(file_path, 'w') as f:
      for item in arr:
        f.write(item + '\n')
  else:
    with codecs.open(file_path, 'w', coding) as f:
      for item in arr:
        f.write(item + u'\n')


def read_kv(file_path, coding=None):
  arr = read_list(file_path, coding)
  if len(arr) == 0:
    return [], []
  return zip(*map(str.split, arr))


def write_kv(k, v, file_path, coding=None):
  arr = zip(k, v)
  arr = [' '.join(item) for item in arr]
  write_list(arr, file_path, coding)


def read_json(file_path):
  with open(file_path, 'r') as f:
    obj = json.load(f)
  return obj


def write_json(obj, file_path):
  with open(file_path, 'w') as f:
    json.dump(obj, f, indent=2, separators=(',', ': '))

