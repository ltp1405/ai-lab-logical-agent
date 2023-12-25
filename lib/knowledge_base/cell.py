from enum import Enum
from logging import raiseExceptions
from typing import Any


class CellValue(Enum):
    TRUE = 1
    FALSE = 2
    MAYBE = 3
    UNKNOWN = 4

    def __str__(self) -> str:
        match self:
            case CellValue.TRUE:
                return "T"
            case CellValue.FALSE:
                return "F"
            case CellValue.MAYBE:
                return "M"
            case CellValue.UNKNOWN:
                return "U"

    def __repr__(self) -> str:
        return str(self)


class Cell:
    def __init__(self) -> None:
        self.is_gold: CellValue = CellValue.UNKNOWN
        self._is_wumpus: CellValue = CellValue.UNKNOWN
        self._is_pit: CellValue = CellValue.UNKNOWN
        self.is_stench: CellValue = CellValue.UNKNOWN
        self.is_breeze: CellValue = CellValue.UNKNOWN

    def __str__(self) -> str:
        return f"(G: {self.is_gold}, W: {self.is_wumpus}, P: {self.is_pit}, S: {self.is_stench}, B: {self.is_breeze})"

    def __repr__(self) -> str:
        return f"(G: {self.is_gold}, W: {self.is_wumpus}, P: {self.is_pit}, S: {self.is_stench}, B: {self.is_breeze})"

    @property
    def is_empty(self):
        match (self.is_breeze, self.is_stench):
            case (CellValue.FALSE, CellValue.FALSE):
                return True
            case _:
                return False

    @property
    def is_safe(self):
        if self.is_wumpus == CellValue.FALSE and self.is_pit == CellValue.FALSE:
            return True
        else:
            return False

    @is_safe.setter
    def is_safe(self, value: bool):
        if value:
            self.is_wumpus = CellValue.FALSE
            self.is_pit = CellValue.FALSE

    @property
    def is_oob(self):
        pass

    @is_oob.setter
    def is_oob(self, value: bool):
        if value:
            self._is_wumpus = CellValue.FALSE
            self._is_pit = CellValue.FALSE
            self.is_stench = CellValue.FALSE
            self.is_breeze = CellValue.FALSE
            self.is_gold = CellValue.FALSE

    @property
    def is_wumpus(self):
        return self._is_wumpus

    @is_wumpus.setter
    def is_wumpus(self, value):
        self._is_wumpus = value
        if value == CellValue.TRUE:
            self.is_pit = CellValue.FALSE
            self.is_gold = CellValue.FALSE

    @property
    def is_pit(self):
        return self._is_pit

    @is_pit.setter
    def is_pit(self, value):
        self._is_pit = value
        if value == CellValue.TRUE:
            self.is_wumpus = CellValue.FALSE
            self.is_gold = CellValue.FALSE

    @property
    def is_glitter(self):
        return self.is_gold

    @is_glitter.setter
    def is_glitter(self, value):
        if value == CellValue.TRUE:
            self.is_gold = CellValue.TRUE
        else:
            self.is_gold = CellValue.FALSE