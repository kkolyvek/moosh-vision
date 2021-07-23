# IMPORT PACKAGES
import cv2
import numpy as np

# =========
# FUNCTIONS
# =========


def MooshEdits(frame):
    """
    Executes following processes to 'frame':
    - Bilateral Filter: to smooth image while retaining edges
    - Convert RGB -> HSV: easier to to set filter limits with
    - Masking: filter colors to find edges
    - Convert HSV -> Grayscale: cv2.findContours requires grayscale
    - Find Contours: set contour thresholds and create contour
    """

    # Do processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret1, thresh1 = cv2.threshold(gray, 110, 255, cv2.THRESH_TRUNC)
    gray_invert = cv2.bitwise_not(thresh1)
    ret2, thresh2 = cv2.threshold(gray_invert, 160, 255, cv2.THRESH_TOZERO)
    # contours, hierarchy = cv2.findContours(
    #     thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    processedFrame = cv2.cvtColor(thresh2, cv2.COLOR_GRAY2BGR)

    # Final edits and return (bounding box)
    # maxContour = []
    # for c in contours:
    #     if np.size(c) > np.size(maxContour):
    #         maxContour = c
    # (x, y, w, h) = cv2.boundingRect(maxContour)
    # cv2.rectangle(processedFrame, (x, y), (x+w, y+h), (0, 255, 0), 1)
    # cv2.drawContours(processedFrame, contours, -1, (0, 0, 255), 1)
    return processedFrame


def brightnessContrast(img, alpha=1, beta=0):
    """
    Alters brightness and contrast of an image following:
    g(i,j) = alpha * f(i, j) + beta
    where alpha is understood to be contrast and beta is brightness
    """
    if alpha != 1 or beta != 0:
        dummy = np.array([])
        return cv2.convertScaleAbs(img, dummy, alpha, beta)

    return img
