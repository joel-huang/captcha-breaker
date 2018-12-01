import sys
sys.path.insert(0, 'lib') # use modified library

import os
import random
import string
import numpy as np
from PIL import Image
from lib.image import ColorCaptcha
from lib.image import SUTDCaptcha
from lib.image import BWCaptcha
from lib.image import draw_rect

NUM_TRAIN = 40
NUM_TEST = 10

def makedirs(path):
    # Intended behavior: try to create the directory,
    # pass if the directory exists already, fails otherwise.
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def prepare_lines(filename, random_str, boxes):
    if len(random_str) != len(boxes):
        raise Exception('The lengths of random string and list of boxes differ.')
    line = ""
    for i in range(len(random_str)):
        line += filename + ',' + str(boxes[i][0]) + ',' + str(boxes[i][1]) + ',' + str(boxes[i][2]) + ',' + str(boxes[i][3]) + ',' + random_str[i] + '\n'
    return line

def make_data(type):
    if type == 'color':
        characters = string.digits + string.ascii_uppercase + string.ascii_lowercase
        n_class = len(characters)
        n_len = random.randint(4,7)
        random_str = ''.join([random.choice(characters) for j in range(n_len)])
        img, boxes = col_generator.generate_image(random_str, bbox=True)
        return random_str, img, boxes
        
    elif type == 'sutd':
        characters = string.digits + string.ascii_lowercase
        n_class = len(characters)
        n_len = 6
        random_str = ''.join([random.choice(characters) for j in range(n_len)])
        img, boxes = sutd_generator.generate_image(random_str, bbox=True)
        return random_str, img, boxes
        
    elif type == 'bw':
        characters = string.digits + string.ascii_uppercase
        n_class = len(characters)
        n_len = 4
        random_str = ''.join([random.choice(characters) for j in range(n_len)])
        img, boxes = bw_generator.generate_image(random_str, bbox=True)
        return random_str, img, boxes
        
    else:
        raise Exception('Wrong argument type.')

makedirs('data/train')
makedirs('data/test')

# ratios
ratios = {'color':  0.7,
          'sutd': 0.1,
          'bw':   0.2}

col_generator = ColorCaptcha(width=200, height=75, curve=True, dots=True)
sutd_generator = SUTDCaptcha(width=200, height=75)
bw_generator = BWCaptcha(width=200, height=75, scale_factor=1)

ftrain = open("data/bboxes_train.csv","w+")
# generate train set, index images to avoid rare clashing
image_index = 0
for captcha_type, ratio in ratios.items():
    for i in range(int(ratio * NUM_TRAIN)):
        random_str, img, boxes = make_data(captcha_type)
        filename = str(image_index) + '_' + random_str + '.png'
        img.save('data/train/' + filename, 'png')
        lines = prepare_lines('train/' + filename, random_str, boxes)
        ftrain.write(lines)
        image_index += 1
ftrain.close()

ftest = open("data/bboxes_test.csv","w+")
# generate test set, index images to avoid rare clashing
image_index = 0
for captcha_type, ratio in ratios.items():
    for i in range(int(ratio * NUM_TEST)):
        random_str, img, boxes = make_data(captcha_type)
        filename = str(image_index) + '_' + random_str + '.png'
        img.save('data/test/' + filename, 'png')
        lines = prepare_lines('test/' + filename, random_str, boxes)
        ftest.write(lines)
        image_index += 1
ftest.close()
