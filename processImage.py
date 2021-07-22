# IMPORT PACKAGES
import cv2
import numpy as np

# =========
# FUNCTIONS
# =========


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
