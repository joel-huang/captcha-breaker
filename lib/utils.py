import cv2
import numpy as np

def PIL_to_array(pil_image):
	return np.array(pil_image)

def threshold(image):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = cv2.GaussianBlur(image,(3,3),0)
	_, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	return image
