from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

import attack
import automaton


@dataclass()
class Step:
    time: float = field()
    position: tuple[float, float, float] = field()
    heading: float = field()
    roll: float = field()
    state: automaton.State = field()


@dataclass()
class Result:
    history: list[Step] = field()


@dataclass()
class Start:
    commands: Iterable[automaton.Command | None] = field()
    magnet: attack.Magnet | None = field()
