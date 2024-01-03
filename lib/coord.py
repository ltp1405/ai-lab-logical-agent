from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CartesianCoord:
    x: int
    y: int

    def to_downward(self, height: int) -> DownwardCoord:
        return DownwardCoord(self.x, height - self.y - 1)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y


@dataclass
class DownwardCoord:
    x: int
    y: int

    def to_cartesian(self, height: int) -> CartesianCoord:
        return CartesianCoord(self.x, height - self.y - 1)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
