from argparse import ArgumentParser
import sys
import numpy as np
import scipy.misc
from config import config
from skimage.transform import resize
import os
import os.path as osp

param = config()
if param['caffe_path'] not in sys.path:
  sys.path.insert(0, param['caffe_path'])
import caffe


def init_caffe_model(param):
  caffe.set_mode_gpu()
  caffe.set_device(param['use_gpu'])
  net = caffe.Net(param['deploy_file'], param['caffe_model'], caffe.TEST)
  return net


def preprocess_bbox(rect):
  centerx = rect['x'] + rect['width'] / 2.0
  centery = rect['y'] + rect['height'] / 2.0
  sz = np.max([rect['width'], rect['height']])
  rect['x'] = centerx - sz / 2.0
  rect['y'] = centery - sz / 2.0
  rect['width'] = sz
  rect['height'] = sz
  return rect


def crop_image_with_padding(img, left, top, right, bottom, pad_value):
  pad = np.array([0, 0, 0, 0])
  if right >= img.shape[1]:
    pad[1] = right - img.shape[1] + 1
  if left < 0:
    pad[0] = -left
    left = 0
    right += pad[0]
  if bottom >= img.shape[0]:
    pad[3] = bottom - img.shape[0] + 1
  if top < 0:
    pad[2] = -top
    top = 0
    bottom += pad[3]
  if np.sum(pad) > 0:
    img = np.pad(img, ((pad[2], pad[3]), (pad[0], pad[1]), (0, 0)), 'constant', constant_values=(pad_value,))
  img = img[int(top):int(bottom), int(left):int(right),:]
  return img


def produce_center_label_map(im_size, x, y, param):
  xv, yv = np.meshgrid(range(im_size), range(im_size))
  xv = xv - x
  yv = yv - y
  D = xv * xv + yv * yv
  return np.exp(-D / 2.0 / param['sigma'] / param['sigma'])


def preprocess(img, mean, param):
  img_out = scipy.misc.imresize(img, (param['box_size'], param['box_size'], 3))
  img_out = img_out / 256.0
  img_out -= mean

  img_out = np.transpose(img_out, (1, 0, 2))
  img_out = img_out[:, :, [2,1,0]]
  label_map = produce_center_label_map(param['box_size'], param['box_size'] / 2, param['box_size'] / 2, param)
  label_map = np.expand_dims(label_map, axis=2)
  img_out = np.expand_dims(np.concatenate((img_out, label_map), axis=2), axis=0)
  img_out = np.transpose(img_out, (0, 3, 2, 1))
  return img_out


def postprocess(map_origin, param):
  nparts = map_origin.shape[0]
  map_processed = np.zeros((param['box_size'], param['box_size'], nparts))
  for i in range(nparts):
    m = np.squeeze(map_origin[i, :, :])
    m[m > 1] = 1
    m[m < -1] = -1
    m = resize(m, (param['box_size'], param['box_size']))
    map_processed[:, :, i] = m
  return map_processed


def get_joints_from_map(joint_map, rect):
  nparts = joint_map.shape[2]
  map_sz = joint_map.shape[0]
  locs = np.zeros((3, nparts))
  for i in range(nparts):
    loc = np.argmax(joint_map[:, :, i])
    loc = np.unravel_index(loc, np.squeeze(joint_map[:, :, i]).shape)
    loc = np.asarray(loc)
    locs[2, i] = joint_map[loc[0], loc[1], i]
    loc = loc / float(map_sz)
    locs[0:2, i] = loc
  locs[0:2, :] *= rect['width']
  locs[0, :] += rect['y']
  locs[1, :] += rect['x']
  return locs


def macro(points, landmark, img, param, filename, bodyname, wf):
  minx = np.inf
  miny = np.inf
  maxx = -np.inf
  maxy = -np.inf
  for i in xrange(len(points)):
    minx = min(minx, landmark[0][points[i]])
    miny = min(miny, landmark[1][points[i]])
    maxx = max(maxx, landmark[0][points[i]])
    maxy = max(maxy, landmark[1][points[i]])

  dx = param['magic'] * (maxx - minx)
  dy = param['magic'] * (maxy - miny)
  minx = max(0, minx - dx)
  miny = max(0, miny - dy)
  maxx = min(img.shape[0], maxx + dx)
  maxy = min(img.shape[1], maxy + dy)

  if maxy - miny > maxx - minx:
    L = maxy - miny
    dx = (L - (maxx - minx)) / 2.0
    minx = max(0, minx - dx)
    maxx = min(img.shape[0], maxx + dx)
  else:
    L = maxx - minx
    dy = (L - (maxy - miny)) / 2.0
    miny = max(0, miny - dy)
    maxy = min(img.shape[1], maxy + dy)

  mag = img.shape[0] / 14.0
  if min(maxy - miny, maxx - minx) < mag * 2.0:
    cenx = (maxx + minx) / 2.0
    ceny = (maxy + miny) / 2.0
    maxx = min(img.shape[0], cenx + mag)
    minx = max(0, cenx - mag)
    maxy = min(img.shape[1], ceny + mag)
    miny = max(0, ceny - mag)

  wf.write(str(miny) + ' ' + str(minx) + ' ' + str(maxy) + ' ' + str(maxx) + '\n')

  #image = img[int(minx):int(maxx), int(miny):int(maxy)]
  #rr = {}
  #rr['x'] = 0
  #rr['y'] = 0
  #rr['width'] = image.shape[1]
  #rr['height'] = image.shape[0]
    
  #rect = preprocess_bbox(rr)
  #crop_img = crop_image_with_padding(image,rr['x'],rr['y'],rr['x']+rr['width'],rr['y']+rr['height'],param['pad_value'])
  #crop_img = scipy.misc.imresize(crop_img,(128,128,3))
  #scipy.misc.imsave(filename.split('.')[0] + '#' + bodyname + '.' + filename.split('.')[1], crop_img)
    

def micro(points, landmark, img, param, filename, bodyname, wf):
  minx = np.inf
  miny = np.inf
  maxx = -np.inf
  maxy = -np.inf
  for i in xrange(len(points)):
    minx = min(minx, landmark[0][points[i]])
    miny = min(miny, landmark[1][points[i]])
    maxx = max(maxx, landmark[0][points[i]])
    maxy = max(maxy, landmark[1][points[i]])
    
  dx = param['magic'] * (maxx - minx)
  dy = param['magic'] * (maxy - miny)
  minx = max(0, minx - dx)
  miny = max(0, miny - dy)
  maxx = min(img.shape[0], maxx + dx)
  maxy = min(img.shape[1], maxy + dy)
  
  mag = img.shape[0] / 14.0
  if min(maxy - miny, maxx - minx) < mag * 2.0:
    cenx = (maxx + minx) / 2.0
    ceny = (maxy + miny) / 2.0
    maxx = max(min(img.shape[0], cenx + mag), maxx)
    minx = min(max(0, cenx - mag), minx)
    maxy = max(min(img.shape[1], ceny + mag), maxy)
    miny = min(max(0, ceny - mag), miny)
  
  wf.write(str(miny) + ' ' + str(minx) + ' ' + str(maxy) + ' ' + str(maxx) + '\n')
      

def apply_model(image, net, param, rect, filename, wf):
  #print 'Doing ' + filename
  rect = preprocess_bbox(rect)
  cropped_img = crop_image_with_padding(image, rect['x'], rect['y'], rect['x'] + rect['width'], rect['y'] + rect['height'], param['pad_value'])
  input_img = preprocess(cropped_img, 0.5, param)

  net.blobs['data'].reshape(1, 4, param['box_size'], param['box_size'])
  net.blobs['data'].data[...] = input_img
  output = net.forward()
  joint_map_origin = np.squeeze(output[param['map_layer_name']])
  joint_map_processed = postprocess(joint_map_origin, param)
  joints_loc = get_joints_from_map(joint_map_processed, rect)

  points = [0, 1, 2, 5]
  macro(points, joints_loc, image, param, filename, 'head', wf)
  points = [2, 3, 4, 5, 6, 7, 8, 11]
  macro(points, joints_loc, image, param, filename, 'body', wf)
  points = [8, 9, 10, 11, 12, 13]
  macro(points, joints_loc, image, param, filename, 'leg', wf)
  points = [2, 3, 4]
  micro(points, joints_loc, image, param, filename, 'rarm', wf)
  points = [5, 6, 7]
  micro(points, joints_loc, image, param, filename, 'larm', wf)
  points = [8, 9, 10]
  micro(points, joints_loc, image, param, filename, 'rleg', wf)
  points = [11, 12, 13]
  micro(points, joints_loc, image, param, filename, 'lleg', wf)

  #foo = np.copy(image)
  #for k in xrange(14):
  #  for i in xrange(3):
  #    for j in xrange(3):
  #      xxx = i - 1 + int(joints_loc[0][k])
  #      xxx = max(0, xxx)
  #      xxx = min(xxx, foo.shape[0] - 1)
  #      yyy = j - 1 + int(joints_loc[1][k])
  #      yyy = max(0, yyy)
  #      yyy = min(yyy, foo.shape[1] - 1)
  #      foo[xxx][yyy][0] = 255
  #      foo[xxx][yyy][1] = 0
  #      foo[xxx][yyy][2] = 0
  #scipy.misc.imsave(filename.split('.')[0] + '##.' + filename.split('.')[1], foo)


def main(args):
  net = init_caffe_model(param)
  f = open(args.datalist)
  wf = open(args.output_datalist, 'w')
  cnt = 0
  for line in f:
    wf.write('# ' + str(cnt) + '\n')
    image_name = line.split(' ')[0]
    wf.write(image_name + '\n')
    label = int(line.split(' ')[1])
    wf.write(str(label) + '\n')
    #if 'jstl' not in args.dataset:
    #  image_name = 'external/exp/datasets/' + args.dataset + '/' + image_name
    img = scipy.misc.imread(image_name)
    rect = {}
    rect['x'] = 0
    rect['y'] = 0
    rect['width'] = img.shape[1]
    rect['height'] = img.shape[0]
    apply_model(img, net, param, rect, image_name, wf)
    cnt += 1
    if cnt % 1000 == 0:
      print str(cnt) + ' done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'


if __name__ == '__main__':
  parser = ArgumentParser(
      description="Gen region proposal datalist")
  parser.add_argument(
      'datalist',
      help="The datalist which need to gen region proposal")
  parser.add_argument(
      'output_datalist',
      help="Output datalist")
  parser.add_argument('dataset')
  args = parser.parse_args()
  main(args)

