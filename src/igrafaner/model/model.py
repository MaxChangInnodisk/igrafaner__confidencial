from typing import List
import numpy as np
import onnxruntime as ort
import cv2
import time

import threading
from collections import deque, defaultdict

from .utils import image_process, euclidean


class OnnxSiamese:

    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self.model = ort.InferenceSession(self.model_path)
        self.inputs = self.model.get_inputs()
        self.outputs = self.model.get_outputs()
        self.metric = defaultdict(float)

    def info(self):
        for inp in self.inputs:
            print(inp.name, inp.type, inp.shape)
        for out in self.outputs:
            print(out.name, out.type, out.shape)

    def preprocess(self, frame: np.ndarray, shape: list, dtype=np.float32) -> np.ndarray:
        ts = time.time()
        blob = np.zeros(shape, dtype=dtype)
        b, c, h, w = shape

        fp32 = frame.astype(dtype)
        resized = cv2.resize(fp32, [w, h])
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        norm = image_process(rgb, std=[255.0, 255.0, 255.0])
        imagenet_norm = image_process(frame=norm,
                                      mean=[0.485, 0.456, 0.406],
                                      std=[0.229, 0.224, 0.225])
        chw = np.transpose(imagenet_norm, (2, 0, 1))
        blob[0, :, :, :] = chw
        self.metric['preprocess'] = round(time.time() - ts, 3)
        return blob

    def postprocess(self, outputs: List[np.ndarray]) -> List[float]:
        ts = time.time()
        for idx, out in enumerate(self.outputs):
            if tuple(out.shape) == outputs[idx].shape:
                continue
            outputs[idx] = outputs[idx].reshape(out.shape)

        results = euclidean((outputs[0], outputs[1]))
        self.metric['postprocess'] = round(time.time() - ts, 3)

        return results

    def inference(self, sample: np.ndarray, golden: np.ndarray):
        output_name = [out.name for out in self.outputs]
        input_blob = {
            self.inputs[0].name: self.preprocess(
                frame=sample,
                shape=self.inputs[0].shape),
            self.inputs[1].name: self.preprocess(
                frame=golden,
                shape=self.inputs[1].shape)
        }
        ts = time.time()
        outputs = self.model.run(output_name, input_blob)
        self.metric['inference'] = round(time.time() - ts, 3)
        
        return self.postprocess(outputs)


def test_fake_data(
        model_path: str = "/home/max/inno/NV/igrafaner/meta/test_max/oi_model.onnx",
        limit = 100):
    print('Test on fake data...')
    onnxs = OnnxSiamese(model_path=model_path)
    a = b = np.ones([256, 256, 3])
    for _ in range(limit):
        outs = onnxs.inference(a, b)[0]
