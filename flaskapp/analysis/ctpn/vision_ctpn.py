from typing import Text, List

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile

from lib.fast_rcnn.config import cfg, cfg_from_file
from lib.fast_rcnn.test import _get_blobs
from lib.text_connector.detectors import TextDetector
from lib.text_connector.text_connect_cfg import Config as TextLineCfg
from lib.rpn_msr.proposal_layer_tf import proposal_layer

from flaskapp.analysis.utils.box import Box, merge_boxes
from flaskapp.analysis.utils.deskew import skew_angle, rotate
from flaskapp.analysis.pytesseract.vision_pytesseract import ocr


def resize_im(im: np.ndarray,
              scale: int,
              max_scale: int = None) -> (np.ndarray, float):
    """
    Resize an image according to given scale. Scale will be
    adjusted depending on original image size and max_scale allowed.

    Returns the resized image, with the final scale applied
    (not necessary to return scale unless we intend to resize
    image back to original scale)

    :param im: image to be resized
    :param scale: scaling factor to be applied
    :param max_scale: maximum scale to be applied
    """

    # find appropriate scale relative to original image size
    f = float(scale) / min(im.shape[0], im.shape[1])

    if max_scale and f * max(im.shape[0], im.shape[1]) > max_scale:
        f = float(max_scale) / max(im.shape[0], im.shape[1])

    return cv2.resize(im, None, None, fx=f, fy=f,
                      interpolation=cv2.INTER_LINEAR), f


def draw_boxes(img: np.ndarray,
               boxes: np.ndarray) -> List[np.ndarray]:
    """
    Given an image, extract regions of interest indicated
    by the boxes and crop them from the image. Returns a
    list of cropped images representing the ROIs
    :param img: image to extract boxes from
    :param boxes: array of boxes where each box is an array of float.
                  each box contains the coordinates of its vertices and (?)
    """
    to_merge = []
    for box in boxes:
        if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(
                box[3] - box[0]) < 5:
            continue

        x = int(box[0])
        y = int(box[1])
        w = int(box[6]) - int(box[0])
        h = int(box[7]) - int(box[1])
        custombox = Box(x, y, w, h)
        to_merge.append(custombox)

    vertical_threshold = round(img.shape[0] * 0.05)
    horizontal_threshold = round(img.shape[1] * 0.05)
    merged_boxes = merge_boxes(to_merge,
                               v_thresh=vertical_threshold,
                               h_thresh=horizontal_threshold)

    cropped_images = []
    for custombox in merged_boxes:
        custombox = custombox.scale(fx=1.15, fy=1.15, max_height=img.shape[0],
                                    max_width=img.shape[1])
        cropped = img[
                  custombox.top_left_y:custombox.top_left_y + custombox.height,
                  custombox.top_left_x:custombox.top_left_x + custombox.width]
        cropped_images.append(cropped)

    return cropped_images


def create_tf_session(config_filepath: Text = './text.yml',
                      model_filepath: Text = './ctpn.pb') -> tf.Session:
    """
    Initialise a tensorflow session with given config/model
    :param config_filepath: filepath to configuration yaml file
    :param model_filepath: filepath to pre-trained model
    """
    # merge YAML config into default options __C (easydict)
    cfg_from_file(config_filepath)

    # Initialize a session with allow_soft_placement set to True.
    config = tf.ConfigProto(allow_soft_placement=True)
    sess = tf.Session(config=config)

    with gfile.FastGFile(model_filepath, 'rb') as f:
        # Initialize graph object
        graph_def = tf.GraphDef()

        # Read graph from file
        graph_def.ParseFromString(f.read())

        # Redundant? sets session to run with default graph?
        sess.graph.as_default()

        # Import the graph from graph_def into current default graph
        tf.import_graph_def(graph_def, name='')

        # Initialise ALL variables to hold specific values, and run the session
        # variables are added to GLOBAL_VARIABLES collection by default
        sess.run(tf.global_variables_initializer())

    return sess


from datetime import datetime
def detect_text_ctpn(image_bytes: bytes,
                     sess: tf.Session) -> (np.ndarray, np.ndarray, float):
    """
    Given an image and an active tensorflow session loaded with config/model,
    run the model to identify regions of interest (i.e. regions that are
    likely to contain text).

    :param image_bytes: image to detect text/perform ocr on
    :param sess: active tensorflow session with graph and config loaded
    """

    # TODO: Read more about this section, up to TextDetector()
    # Retrieve tensors from graph
    input_img = sess.graph.get_tensor_by_name('Placeholder:0')
    output_cls_prob = sess.graph.get_tensor_by_name('Reshape_2:0')
    output_box_pred = sess.graph.get_tensor_by_name(
        'rpn_bbox_pred/Reshape_1:0')

    # Process image
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_ANYCOLOR)
    img, scale = resize_im(img, scale=TextLineCfg.SCALE,
                           max_scale=TextLineCfg.MAX_SCALE)
    img = rotate(img, skew_angle(image=img))

    blobs, im_scales = _get_blobs(img, None)
    if cfg.TEST.HAS_RPN:
        im_blob = blobs['data']
        blobs['im_info'] = np.array(
            [[im_blob.shape[1], im_blob.shape[2], im_scales[0]]],
            dtype=np.float32)

    cls_prob, box_pred = sess.run([output_cls_prob, output_box_pred],
                                  feed_dict={input_img: blobs['data']})

    rois, _ = proposal_layer(cls_prob, box_pred, blobs['im_info'], 'TEST',
                             anchor_scales=cfg.ANCHOR_SCALES)

    scores = rois[:, 0]
    boxes = rois[:, 1:5] / im_scales[0]

    # apply nms and retain only high scoring boxes/proposals
    textdetector = TextDetector()
    boxes = textdetector.detect(boxes, scores[:, np.newaxis],
                                img.shape[:2])

    # crop regions of interest indicated by boxes
    cropped_images = draw_boxes(img, boxes)

    # for each region of interest, perform ocr
    mystrings = []
    for cropped in cropped_images:
        mystrings.append(ocr(cropped))

    # return collection of text extracted from the image
    return mystrings
