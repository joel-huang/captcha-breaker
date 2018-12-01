import os
import cv2
from lib.utils import PIL_to_array
from lib.utils import threshold

TRAIN_PATH = 'data/train/'
TEST_PATH = 'data/test/'

train_paths = os.listdir(TRAIN_PATH)
test_paths = os.listdir(TEST_PATH)
try:
    os.makedirs('data/train_preprocessed/')
    os.makedirs('data/test_preprocessed/')
except OSError:
    if not os.path.isdir('data/train_preprocessed/') and os.path.isdir('data/test_preprocessed/'):
        raise

def prepare_lines(filename, random_str, boxes):
    if len(random_str) != len(boxes):
        raise Exception('The lengths of random string and list of boxes differ.')
    line = ""
    for i in range(len(random_str)):
        line += filename + ',' + str(boxes[i][0]) + ',' + str(boxes[i][1]) + ',' + str(boxes[i][2]) + ',' + str(boxes[i][3]) + ',' + random_str[i] + '\n'
    return line

ftrain = open("data/bboxes_train_preprocessed.csv","w+")
for path in train_paths:
    image = cv2.imread(TRAIN_PATH + path)
    image = PIL_to_array(image)
    image = threshold(image)
    cv2.imwrite('data/train_preprocessed/' + path, image)
    lines = prepare_lines('train_preprocessed/' + filename, random_str, boxes)
    ftrain.write(lines)
ftrain.close()

ftest = open("data/bboxes_test_preprocessed.csv","w+")
for path in test_paths:
    image = cv2.imread(TEST_PATH + path)
    image = PIL_to_array(image)
    image = threshold(image)
    cv2.imwrite('data/test_preprocessed/' + path, image)
    lines = prepare_lines('test/' + filename, random_str, boxes)
    ftest.write(lines)
ftest.close()

