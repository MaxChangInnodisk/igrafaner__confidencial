import time
from collections import defaultdict


class FailedCompDict(dict):

    def __init__(self):
        self.types = defaultdict(list)
        self.count = 0

    def __setitem__(self, uuid: str, info: dict):
        self.types[info['type']].append(uuid)
        self.count += 1
        super().__setitem__(uuid, info)


class CountingList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0

    def append(self, item):
        super().append(item)
        self.count += 1


class StopWatch:

    def __init__(self) -> None:
        self.min = 0
        self.max = 0
        self.avg = 0
        self.total = 0
        self.count = 0
        self.pre = time.time()

    def split_start(self) -> float:
        self.pre = time.time()
        return self.pre

    def split_stop(self) -> float:
        cost = time.time() - self.pre
        self.count += 1
        self.total += cost

        self.min = min(cost, self.min)
        self.max = max(cost, self.max)
        self.avg = self.total/self.count

        return cost
