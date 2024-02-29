from typing import List, Union, Tuple, Optional
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
import numpy as np
import cv2
import os


class SampleComponent:

    src_path: str
    dst_path: str
    uid: str
    part_no: str
    light_source: str
    buffer: np.ndarray

    def __init__(self,
                 src_path: str,
                 xxyy: List[int],
                 uid: str,
                 part_no: str,
                 mount_folder: str,
                 split_keyword: str = "MAP/") -> None:
        self.uid = uid
        self.part_no = part_no

        self.src_path = str(PureWindowsPath(src_path).as_posix())

        self.include_keyword = \
            split_keyword.replace('/', '') in os.listdir(mount_folder)
        self.dst_path, self.light_source = self.parse_path(
            src_path=self.src_path,
            mount_folder=mount_folder,
            split_keyword=split_keyword if '/' == split_keyword[-1] else f"{split_keyword}/")

        self.buffer = self.get_buffer(image_path=self.dst_path, xxyy=xxyy)

    def parse_path(self,
                   src_path: str,
                   mount_folder: str,
                   split_keyword: str
                   ) -> Tuple[str, str]:

        if not Path(mount_folder).exists():
            raise FileExistsError(f"Mount folder is not exists ({mount_folder})")

        # Parse src_path and get dst_path
        infix = split_keyword
        prefix = Path(mount_folder)
        postfix = src_path.split(infix)[-1]

        if self.include_keyword:
            dst_path = prefix.joinpath(infix, postfix)
        else:
            dst_path = prefix.joinpath(postfix)

        if not dst_path.exists():
            raise FileExistsError(f"File is not exists ({dst_path})")

        return str(dst_path), Path(postfix).stem.split('_')[-1]

    def get_buffer(self,
                   image_path: str,
                   xxyy: List[int]) -> np.ndarray:
        x1, x2, y1, y2 = xxyy
        frame = cv2.imread(image_path)
        return frame[y1:y2, x1:x2]
