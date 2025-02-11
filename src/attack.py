from __future__ import annotations

from typing import Protocol


class Magnet(Protocol):
    def offset(self, time: float) -> float:
        ...


class StationaryMagnet(Magnet):
    def __init__(self, magnitude: float):
        self.magnitude = magnitude

    def offset(self, time: float) -> float:
        return self.magnitude
