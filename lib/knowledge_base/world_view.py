from typing import Any, Dict, List, Tuple
from lib.game.board import Direction

from lib.knowledge_base.cell import Cell, CellValue


class WorldView:
    kx = [1, -1, 0, 0]
    ky = [0, 0, 1, -1]

    def __init__(self) -> None:
        self.cells: List[List[Cell]] = []
        for i in range(22):
            self.cells.append([])
            for _ in range(22):
                self.cells[i].append(Cell())

    def __str__(self) -> str:
        s = ""
        for i in range(22):
            for j in range(22):
                s += str(self.cells[i][j]) + " "
            s += "\n"
        return s

    def __getitem__(self, pos: Tuple[int, int]) -> Cell:
        x, y = pos
        return self.cells[x + 11][y + 11]

    def __setitem__(
        self, pos: Tuple[int, int], cell: Cell | Tuple[str, CellValue]
    ) -> Dict[Tuple[int, int], Any]:
        x, y = pos
        res: Dict[Tuple[int, int], Any] = {}
        if isinstance(cell, Tuple):
            self.cells[x + 11][y + 11].__setattr__(cell[0], cell[1])
            if self.cells[x + 11][y + 11].is_empty == True:
                for i in range(4):
                    self.cells[x + self.kx[i] + 11][y + self.ky[i] + 11].is_safe = True
                    res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                        x + self.kx[i] + 11
                    ][y + self.ky[i] + 11]
            match cell:
                case ("is_stench", CellValue.TRUE):
                    not_wumpus_cnt = 0
                    for i in range(4):
                        if (
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus
                            == CellValue.FALSE
                        ):
                            not_wumpus_cnt += 1
                        if (
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus
                            == CellValue.UNKNOWN
                        ):
                            self.cells[x + self.kx[i] + 11][
                                y + self.ky[i] + 11
                            ].is_wumpus = CellValue.MAYBE
                            res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                x + self.kx[i] + 11
                            ][y + self.ky[i] + 11]

                    if not_wumpus_cnt == 3:
                        for i in range(4):
                            if (
                                self.cells[x + self.kx[i] + 11][
                                    y + self.ky[i] + 11
                                ].is_wumpus
                                == CellValue.MAYBE
                            ):
                                self.cells[x + self.kx[i] + 11][
                                    y + self.ky[i] + 11
                                ].is_wumpus = CellValue.TRUE
                                res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                    x + self.kx[i] + 11
                                ][y + self.ky[i] + 11]
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
                            res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                x + self.kx[i] + 11
                            ][y + self.ky[i] + 11]
                case ("is_breeze", CellValue.TRUE):
                    not_pit_cnt = 0
                    for i in range(4):
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
                            res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                x + self.kx[i] + 11
                            ][y + self.ky[i] + 11]
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
                                res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                    x + self.kx[i] + 11
                                ][y + self.ky[i] + 11]

        elif isinstance(cell, Cell):
            self.cells[x + 11][y + 11] = cell
            res[(x, y)] = self.cells[x + 11][y + 11]
        else:
            raise TypeError("cell must be Cell or CellValue")
        return res

    def set_bound(self, direction: Direction, value: int) -> Dict[Tuple[int, int], Any]:
        res: Dict[Tuple[int, int], Any] = {}
        match direction:
            case Direction.UP:
                for i in range(-11, value - 1):
                    for j in range(-11, 10):
                        self.cells[i + 11][j + 11].is_oob = True
                        res[(i, j)] = self.cells[i + 11][j + 11]
            case Direction.RIGHT:
                for i in range(-11, 10):
                    for j in range(-11, value - 1):
                        self.cells[i + 11][j + 11].is_oob = True
                        res[(i, j)] = self.cells[i + 11][j + 11]
            case Direction.DOWN:
                for i in range(value + 1, 10):
                    for j in range(-11, 10):
                        self.cells[i + 11][j + 11].is_oob = True
                        res[(i, j)] = self.cells[i + 11][j + 11]
            case Direction.LEFT:
                for i in range(-11, 10):
                    for j in range(value + 1, 10):
                        self.cells[i + 11][j + 11].is_oob = True
                        res[(i, j)] = self.cells[i + 11][j + 11]
        return res
