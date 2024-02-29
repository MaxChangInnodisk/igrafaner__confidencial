import json
import cv2
import numpy as np
from typing import Tuple
from pathlib import Path, PurePath
from collections import namedtuple


def read_json(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data


class GoldenComponent:
    def __init__(self,
                 buffer: np.ndarray,
                 threshold: float) -> None:
        self.buffer: np.ndarray = buffer
        self.threshold: float = threshold


class GoldenParser:

    def __init__(self,
                 root: str,
                 json_file: str = "inference_info.json",
                 panel_file: str = "panel_info.json") -> None:
        """
        Find golden data root and inference_panel_info.json
        """
        self.root = Path(root)
        assert self.root.exists(), \
            f"Root path not found. ({str(self.root)})"

        self.json_file = self.root.joinpath(json_file)
        assert self.json_file.exists(), f"json not found. ({self.json_file})"

        self.panel_file = self.root.joinpath(panel_file)
        assert self.panel_file.exists(), f"panel not found. ({self.panel_file})"

        self.data: dict = read_json(self.json_file.__str__())
        self.panels = read_json(self.panel_file.__str__())
        print(self.panels)
        
        self.part_nums = set(self.data.keys())

    def check_part_no(self, part_no: str) -> bool:
        return part_no in self.part_nums

    def check_cmodel(self, cmodel: str) -> bool:
        return cmodel in self.panels

    def get_golden(self, part_no: str, light_source: str) -> GoldenComponent:
        """
        Get data related with golden 

        Args:
            part_no (str): part number
            light_source (str): light source

        Returns:
            GoldenComponent: has attribute: buffer and threshold
        """
        golden_info = self.data[part_no][light_source][0]
        image_path = self.root.joinpath(
            golden_info["image_path"], golden_info["image_file"])

        return GoldenComponent(cv2.imread(str(image_path)), float(golden_info["threshold"]))


if __name__ == "__main__":
    gp = GoldenParser(root="/home/max/inno/NV/igrafaner/meta/test_max")

    print(gp.get_golden(
        part_no='5D48GSFACIKC0',
        light_source='UniformLight'))
