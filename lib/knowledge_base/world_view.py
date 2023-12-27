from typing import Any, Dict, List, Tuple
from lib.game.board_model import Direction
from rich import print

from lib.knowledge_base.cell import Cell, CellValue


class WorldData:
    def __init__(self) -> None:
        self.cells: List[List[Cell]] = []
        for i in range(22):
            self.cells.append([])
            for _ in range(22):
                self.cells[i].append(Cell())

    def __getitem__(self, pos: Tuple[int, int]) -> Cell:
        x, y = pos
        return self.cells[-y - 11][x + 11]

    def __setitem__(self, pos: Tuple[int, int], cell: Cell) -> None:
        x, y = pos
        self.cells[-y - 11][x + 11] = cell

    def __repr__(self) -> str:
        return repr(self.cells)


class WorldView:
    kx = [1, -1, 0, 0]
    ky = [0, 0, 1, -1]

    def __init__(self) -> None:
        self.cells = WorldData()

    def __str__(self) -> str:
        return str(self.cells)

    def __getitem__(self, pos: Tuple[int, int]) -> Cell:
        return self.cells[pos]

    def infer(self) -> Dict[Tuple[int, int], Any]:
        res: Dict[Tuple[int, int], Any] = {}
        for y in range(-11, 10):
            for x in range(-11, 10):
                if self.cells[(x, y)].is_empty == True:
                    for i in range(4):
                        self.cells[(x + self.kx[i], y + self.ky[i])].is_safe = True
                        res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                            (x + self.kx[i], y + self.ky[i])
                        ]
                if self.cells[(x, y)].is_stench == CellValue.TRUE:
                    not_wumpus_cnt = 0
                    for i in range(4):
                        if (
                            self.cells[(x + self.kx[i], y + self.ky[i])].is_wumpus
                            == CellValue.FALSE
                        ):
                            not_wumpus_cnt += 1
                        if (
                            self.cells[(x + self.kx[i], y + self.ky[i])].is_wumpus
                            == CellValue.UNKNOWN
                        ):
                            self.cells[
                                (x + self.kx[i], y + self.ky[i])
                            ].is_wumpus = CellValue.MAYBE
                            res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                (x + self.kx[i], y + self.ky[i])
                            ]

                    if not_wumpus_cnt == 3:
                        for i in range(4):
                            if (
                                self.cells[(x + self.kx[i], y + self.ky[i])].is_wumpus
                                == CellValue.MAYBE
                            ):
                                self.cells[
                                    (x + self.kx[i], y + self.ky[i])
                                ].is_wumpus = CellValue.TRUE
                                res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                    (x + self.kx[i], y + self.ky[i])
                                ]
                if self.cells[(x, y)].is_stench == CellValue.FALSE:
                    for i in range(4):
                        if (
                            self.cells[(x + self.kx[i], y + self.ky[i])].is_wumpus
                            == CellValue.UNKNOWN
                            or self.cells[(x + self.kx[i], y + self.ky[i])].is_wumpus
                            == CellValue.MAYBE
                        ):
                            self.cells[
                                (x + self.kx[i], y + self.ky[i])
                            ].is_wumpus = CellValue.FALSE
                            res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                (x + self.kx[i], y + self.ky[i])
                            ]
                if self.cells[(x, y)].is_breeze == CellValue.TRUE:
                    not_pit_cnt = 0
                    for i in range(4):
                        if (
                            self.cells[(x + self.kx[i], y + self.ky[i])].is_pit
                            == CellValue.FALSE
                        ):
                            not_pit_cnt += 1
                        if (
                            self.cells[(x + self.kx[i], y + self.ky[i])].is_pit
                            == CellValue.UNKNOWN
                        ):
                            self.cells[
                                (x + self.kx[i], y + self.ky[i])
                            ].is_pit = CellValue.MAYBE
                            res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                (x + self.kx[i], y + self.ky[i])
                            ]
                    if not_pit_cnt == 3:
                        for i in range(4):
                            if (
                                self.cells[(x + self.kx[i], y + self.ky[i])].is_pit
                                == CellValue.MAYBE
                            ):
                                self.cells[
                                    (x + self.kx[i], y + self.ky[i])
                                ].is_pit = CellValue.TRUE
                                res[(x + self.kx[i], y + self.ky[i])] = self.cells[
                                    (x + self.kx[i], y + self.ky[i])
                                ]
        return res

    def set_item(
        self, pos: Tuple[int, int, str], cell: CellValue | bool
    ) -> Dict[Tuple[int, int], Any]:
        x, y, attr = pos
        res: Dict[Tuple[int, int], Any] = {}
        self.cells[(x, y)].__setattr__(attr, cell)
        res = self.infer()
        res[(x, y)] = self.cells[(x, y)]
        return res

    def set_bound(self, direction: Direction, value: int) -> None:
        match direction:
            case Direction.UP:
                for y in range(value + 1, 10):
                    for x in range(-11, 10):
                        self.cells[(x, y)].is_oob = True
            case Direction.RIGHT:
                for y in range(-11, 10):
                    for x in range(value + 1, 10):
                        self.cells[(x, y)].is_oob = True
            case Direction.DOWN:
                for y in range(-11, value - 1):
                    for x in range(-11, 10):
                        self.cells[(x, y)].is_oob = True
            case Direction.LEFT:
                for y in range(-11, 10):
                    for x in range(-11, value - 1):
                        self.cells[(x, y)].is_oob = True

    # def set_bound(self, direction: Direction, value: int) -> Dict[Tuple[int, int], Any]:
    #     res: Dict[Tuple[int, int], Any] = {}
    #     match direction:
    #         case Direction.UP:
    #             for i in range(-11, value - 1):
    #                 for j in range(-11, 10):
    #                     self.cells[i + 11][j + 11].is_oob = True
    #                     res[(i, j)] = self.cells[i + 11][j + 11]
    #         case Direction.RIGHT:
    #             for i in range(-11, 10):
    #                 for j in range(-11, value - 1):
    #                     self.cells[i + 11][j + 11].is_oob = True
    #                     res[(i, j)] = self.cells[i + 11][j + 11]
    #         case Direction.DOWN:
    #             for i in range(value + 1, 10):
    #                 for j in range(-11, 10):
    #                     self.cells[i + 11][j + 11].is_oob = True
    #                     res[(i, j)] = self.cells[i + 11][j + 11]
    #         case Direction.LEFT:
    #             for i in range(-11, 10):
    #                 for j in range(value + 1, 10):
    #                     self.cells[i + 11][j + 11].is_oob = True
    #                     res[(i, j)] = self.cells[i + 11][j + 11]
    #     return res
