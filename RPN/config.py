def config():
  param = {}
  param['use_gpu'] = 0
  param['caffe_model'] = 'RPN/model/pose_iter_265000.caffemodel'
  param['deploy_file'] = 'RPN/model/pose_deploy.prototxt'
  param['box_size'] = 256
  param['pad_value'] = 128
  param['magic'] = 0.2
  param['sigma'] = 21
  param['caffe_path'] = 'external/caffe/python/'
  param['map_layer_name'] = 'Mconv5_stage3'
  return param

