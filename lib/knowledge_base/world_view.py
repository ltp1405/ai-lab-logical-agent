from typing import List, Tuple
from lib.game.board import Direction

from lib.knowledge_base.cell import Cell, CellValue


class WorldView:
    cells: List[List[Cell]]
    kx = [1, -1, 0, 0]
    ky = [0, 0, 1, -1]

    def __init__(self) -> None:
        for i in range(22):
            self.cells.append([])
            for _ in range(22):
                self.cells[i].append(Cell())

    def __get_item__(self, x: int, y: int) -> Cell:
        return self.cells[x + 11][y + 11]

    def __set_item__(self, x: int, y: int, cell: Cell | Tuple[str, CellValue]) -> None:
        if isinstance(cell, Tuple[str, CellValue]):
            self.cells[x + 11][y + 11].__setattr__(cell[0], cell[1])
            if self.cells[x + 11][y + 11].is_empty == True:
                for i in range(4):
                    self.cells[x + self.kx[i] + 11][y + self.ky[i] + 11].is_safe = True
            match cell:
                case ("is_stench", CellValue.TRUE):
                    for i in range(4):
                        if (
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus
                            == CellValue.UNKNOWN
                        ):
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus = CellValue.MAYBE
                case ("is_stench", CellValue.FALSE):
                    for i in range(4):
                        if (
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus
                            == CellValue.UNKNOWN
                            or self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus
                            == CellValue.MAYBE
                        ):
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus = CellValue.FALSE
                case ("is_breeze", CellValue.TRUE):
                    for i in range(4):
                        not_pit_cnt = 0
                        if (
                            self.cells[x + self.kx[i] + 11][y + self.ky[i] + 11].is_pit
                            == CellValue.FALSE
                        ):
                            not_pit_cnt += 1
                        if (
                            self.cells[x + self.kx[i] + 11][y + self.ky[i] + 11].is_pit
                            == CellValue.UNKNOWN
                        ):
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_pit = CellValue.MAYBE
                    if not_pit_cnt == 3:
                        for i in range(4):
                            if (
                                self.cells[x + self.kx[i] + 11][
                                    y + self.ky[i] + 11
                                ].is_pit
                                == CellValue.MAYBE
                            ):
                                self.cells[x + self.kx[i] + 11][
                                    y + self.ky[i] + 11
                                ].is_pit = CellValue.TRUE

        elif isinstance(cell, Cell):
            self.cells[x + 11][y + 11] = cell
        else:
            raise TypeError("cell must be Cell or CellValue")

    def set_bound(self, direction: Direction, value: int) -> None:
        match direction:
            case Direction.UP:
                for i in range(-11, value - 1):
                    for j in range(-11, 10):
                        self.cells[i + 11][j + 11].is_oob = True
            case Direction.RIGHT:
                for i in range(-11, 10):
                    for j in range(-11, value - 1):
                        self.cells[i + 11][j + 11].is_oob = True
            case Direction.DOWN:
                for i in range(value + 1, 10):
                    for j in range(-11, 10):
                        self.cells[i + 11][j + 11].is_oob = True
            case Direction.LEFT:
                for i in range(-11, 10):
                    for j in range(value + 1, 10):
                        self.cells[i + 11][j + 11].is_oob = True
