import os
import random
import json
from argparse import ArgumentParser

import cv2
import mmcv
import numpy as np
import torch
from mmcv.transforms import Compose
from mmdet.utils import get_test_pipeline_cfg
from mmengine.config import Config, ConfigDict
from mmengine.utils import ProgressBar, path

from mmyolo.utils import register_all_modules
from mmyolo.utils.misc import get_file_list
from sklearn.metrics import pairwise_distances  # Import pairwise_distances từ sklearn

from projects.easydeploy.model import ORTWrapper, TRTWrapper  # Import các wrappers phù hợp


logger = setup_logger(__name__)


def preprocess(config):
    data_preprocess = config.get('model', {}).get('data_preprocessor', {})
    mean = data_preprocess.get('mean', [0., 0., 0.])
    std = data_preprocess.get('std', [1., 1., 1.])
    mean = torch.tensor(mean, dtype=torch.float32).reshape(1, 3, 1, 1)
    std = torch.tensor(std, dtype=torch.float32).reshape(1, 3, 1, 1)

    class PreProcess(torch.nn.Module):

        def __init__(self):
            super().__init__()

        def forward(self, x):
            x = x[None].float()
            x -= mean.to(x.device)
            x /= std.to(x.device)
            return x

    return PreProcess().eval()

def calculate_center_distances(bboxes):
    num_boxes = bboxes.shape[0]
    if num_boxes < 2:
        return [1]* num_boxes, [1] * num_boxes
      
    centers = (bboxes[:, :2] + bboxes[:, 2:]) / 2  # (N, 2)
    distances = pairwise_distances(centers, metric='euclidean')  # (N, N)

    np.fill_diagonal(distances, np.inf)

    min_distances = distances.min(axis=1)
    min_distances_list = [float(dist) if dist != np.inf else 0 for dist in min_distances]
    min_scores = [np.sqrt(1 - np.exp(-(dist - 68) / 76)) if dist is not 0 else 0 for dist in min_distances_list]

    return min_distances_list, min_scores

def get_object(bgr , config):
    """
    Object detection with Center Distance and Score Calculation

    This function takes an image path and a checkpoint path as input and performs object detection.
    It uses the model to detect objects in the image and calculates the center distances of each object.
    The function then appends the detection results to a list and returns it.

    Args:
        img (str): Image path
        config (str): Config file path
        checkpoint (str): Checkpoint file path

    Returns:
        list: A list of dictionaries containing the detection results. Each dictionary contains the keys 'image', 'detections', 'bbox', 'score', 'label', 'label_name', 'distance', 'distance_score', and 'combine_score'.
    """
    
    # args = parse_args()

    register_all_modules()

    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(100)]

    model = ORTWrapper(config.model_checkpoint, config.device)
    
    model.to(config.device)
    model.eval()

    cfg = Config.fromfile(config.model_config) # conffig model
    class_names = cfg.get('class_name', None)

    test_pipeline = get_test_pipeline_cfg(cfg)
    test_pipeline[0] = ConfigDict({'type': 'mmdet.LoadImageFromNDArray'})
    test_pipeline = Compose(test_pipeline)

    pre_pipeline = preprocess(cfg)
    all_results = []

    rgb = mmcv.imconvert(bgr, 'bgr', 'rgb')
    data, samples = test_pipeline(dict(img=rgb, img_id=1)).values()
    pad_param = samples.get('pad_param', np.array([0, 0, 0, 0], dtype=np.float32))
    h, w = samples.get('ori_shape', rgb.shape[:2])
    pad_param = torch.from_numpy(np.array([pad_param[2], pad_param[0], pad_param[2], pad_param[0]]))
    scale_factor = samples.get('scale_factor', [1., 1])
    scale_factor = torch.from_numpy(np.array([scale_factor * 2]))
    data = pre_pipeline(data).to(config_module.device)

    with torch.no_grad():
        result = model(data)

    if isinstance(result, torch.Tensor):
        num_dets = result.shape[0]
        bboxes = result[:, :4]
        scores = result[:, 4]
        labels = result[:, 5].int()
    elif isinstance(result, (list, tuple)) and len(result) == 4:
        num_dets, bboxes, scores, labels = result
        scores = scores[0, :num_dets]
        bboxes = bboxes[0, :num_dets]
        labels = labels[0, :num_dets]
    else:
        raise ValueError("Unexpected model output format.")

    bboxes = bboxes - pad_param
    bboxes = bboxes / scale_factor

    bboxes[:, 0::2].clamp_(0, w)
    bboxes[:, 1::2].clamp_(0, h)
    bboxes = bboxes.round().int()

    bboxes_np = bboxes.cpu().numpy()
    min_distances, min_scores = calculate_center_distances(bboxes_np)

    image_results = {
        # 'image': filename,
        'detections': [],
    }

    for idx, (bbox, score, label) in enumerate(zip(bboxes, scores, labels)):
        bbox = bbox.tolist()
       

        if class_names is not None:
            if label < len(class_names):
                label_name = class_names[label]
                name = f'cls:{label_name}_score:{score:0.4f}'
            else:
                label_name = str(label)
            name = f'{label_name}_score:{score:.2f}'
        else:
            name = f'{label}_score:{score:.2f}'
        combine_score= float(score * 0.8 + 0.2 * min_scores[idx])
        # Thêm kết quả vào danh sách
        detection = {
            'bbox': bbox,
            'score': float(score),
            'label': int(label),
            'label_name': label_name if class_names is not None else str(label),
            'distance': min_distances[idx],  
            'distance_score': min_scores[idx], 
            'combine_score' : combine_score,
        }
        image_results['detections'].append(detection)
    all_results.append(image_results)
    return all_results


