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

for path in train_paths:
    image = cv2.imread(TRAIN_PATH + path)
    image = PIL_to_array(image)
    image = threshold(image)
    cv2.imwrite('data/train_preprocessed/' + path, image)

for path in test_paths:
    image = cv2.imread(TEST_PATH + path)
    image = PIL_to_array(image)
    image = threshold(image)
    cv2.imwrite('data/test_preprocessed/' + path, image)
