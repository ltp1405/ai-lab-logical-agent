from enum import Enum
from typing import Any


class CellValue(Enum):
    TRUE = 1
    FALSE = 2
    MAYBE = 3
    UNKNOWN = 3


class Cell:
    is_gold: CellValue
    is_wumpus: CellValue
    is_pit: CellValue
    is_stench: CellValue
    is_breeze: CellValue

    def __init__(self) -> None:
        self.is_gold = CellValue.UNKNOWN
        self.is_wumpus = CellValue.UNKNOWN
        self.is_pit = CellValue.UNKNOWN
        self.is_stench = CellValue.UNKNOWN
        self.is_breeze = CellValue.UNKNOWN

    def __getattribute__(self, __name: str) -> Any:
        match __name:
            case "is_safe":
                if self.is_wumpus == CellValue.FALSE and self.is_pit == CellValue.FALSE:
                    return True
                else:
                    return False
            case "is_glitter":
                return self.is_gold
            case "is_empty":
                match (self.is_wumpus, self.is_pit):
                    case (CellValue.FALSE, CellValue.FALSE):
                        return True
                    case _:
                        return False
            case _:
                return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        match __name:
            case "is_safe":
                if __value:
                    self.is_wumpus = CellValue.FALSE
                    self.is_pit = CellValue.FALSE
            case "is_glitter":
                if __value:
                    self.is_gold = CellValue.TRUE
                else:
                    self.is_gold = CellValue.FALSE
            case "is_oob":
                if __value:
                    self.is_wumpus = CellValue.FALSE
                    self.is_pit = CellValue.FALSE
                    self.is_stench = CellValue.FALSE
                    self.is_breeze = CellValue.FALSE
                    self.is_gold = CellValue.FALSE
            case "is_wumpus":
                if __value:
                    self.is_pit = CellValue.FALSE
                    self.is_gold = CellValue.FALSE
            case "is_pit":
                if __value:
                    self.is_wumpus = CellValue.FALSE
                    self.is_gold = CellValue.FALSE
            case _:
                super().__setattr__(__name, __value)
