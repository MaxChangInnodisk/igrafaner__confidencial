from typing import List
import numpy as np
import csv
import cv2


def l2_normalize(x, axis=-1, epsilon=1e-10):
    output = x / np.sqrt(np.maximum(np.sum(np.square(x),
                         axis=axis, keepdims=True), epsilon))
    return output


def euclidean(vects):
    """Find the Euclidean distance between two vectors.

    Arguments:
        vects: List containing two tensors of same length.

    Returns:
        Tensor containing euclidean distance
        (as floating point value) between vectors.
    """
    x, y = vects
    sum_square = np.sum(np.square(x - y), axis=-1, keepdims=True)
    ret = np.sqrt(np.maximum(sum_square, 1e-7))
    return ret


def image_process(frame: np.ndarray,
                  mean: List[float] = [0.0, 0.0, 0.0],
                  std: List[float] = [1.0, 1.0, 1.0]):
    assert len(mean) == len(
        std), f"mean ({len(mean)}) and std ({len(std)}) should has same length"

    h, w, c = frame.shape

    assert c == len(
        mean), f"Support input channel is {c}, but mean and std is {len(mean)}"
    for i in range(c):
        frame[:, :, i] = (frame[:, :, i]-mean[i])/std[i]

    return frame
