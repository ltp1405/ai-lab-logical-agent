from copy import Error
from typing import Any, List, Tuple
from lib.game.board import Action, Direction
from lib.knowledge_base.cell import CellValue
from lib.knowledge_base.world_view import WorldView
from lib.percepts import Percepts


class KnowledgeBase:
    world: WorldView
    top: int | None
    right: int | None
    bottom: int | None
    left: int | None

    def __init__(self) -> None:
        self.world = WorldView()

    def __getattribute__(self, __name: str) -> Any:
        match __name:
            case "exit":
                if self.left != None and self.bottom != None:
                    return (self.left, self.bottom)
            case "safe_cells":
                safe_cells = []
                for i in range(22):
                    for j in range(22):
                        if self.world[(i, j)].is_safe:
                            safe_cells.append((i - 11, j - 11))
                return safe_cells
            case "wumpus_cells":
                wumpus_cells: List[Tuple[Tuple[int, int], CellValue]] = []
                for i in range(22):
                    for j in range(22):
                        if self.world[(i, j)].is_wumpus == CellValue.TRUE:
                            wumpus_cells.insert(
                                0,
                                ((i - 11, j - 11), CellValue.TRUE),
                            )
                        elif self.world[(i, j)].is_wumpus == CellValue.MAYBE:
                            wumpus_cells.insert(
                                -1,
                                ((i - 11, j - 11), CellValue.MAYBE),
                            )
                return wumpus_cells
            case "pit_cells":
                pit_cells: List[Tuple[Tuple[int, int], CellValue]] = []
                for i in range(22):
                    for j in range(22):
                        if self.world[(i, j)].is_pit == CellValue.TRUE:
                            pit_cells.insert(
                                0,
                                ((i - 11, j - 11), CellValue.TRUE),
                            )
                        elif self.world[(i, j)].is_pit == CellValue.MAYBE:
                            pit_cells.insert(
                                -1,
                                ((i - 11, j - 11), CellValue.MAYBE),
                            )
                return pit_cells
            case _:
                return super().__getattribute__(__name)

    def tell(
        self,
        x: int,
        y: int,
        percept: Percepts,
        action: Tuple[Action, Direction] | None = None,
    ) -> None:
        if action == None:
            raise Error("TODO")
        if percept["bump"]:
            match action[1]:
                case Direction.UP:
                    self.top = y
                case Direction.RIGHT:
                    self.right = x
                case Direction.DOWN:
                    self.bottom = y
                case Direction.LEFT:
                    self.left = x
        if percept["scream"] or action[0] == Action.SHOOT:
            match action[1]:
                case Direction.UP:
                    self.world[(x, y + 1)].is_safe = True
                case Direction.DOWN:
                    self.world[(x, y - 1)].is_safe = True
                case Direction.LEFT:
                    self.world[(x + 1, y)].is_safe = True
                case Direction.RIGHT:
                    self.world[(x - 1, y)].is_safe = True
        if percept["stench"]:
            self.world[(x, y)].is_stench = CellValue.TRUE
        else:
            self.world[(x, y)].is_stench = CellValue.FALSE
        if percept["breeze"]:
            self.world[(x, y)].is_breeze = CellValue.TRUE
        else:
            self.world[(x, y)].is_breeze = CellValue.FALSE
        if percept["glitter"]:
            self.world[(x, y)].is_glitter = CellValue.TRUE
        else:
            self.world[(x, y)].is_glitter = CellValue.FALSE

    def ask(self, x: int, y: int, attribute: str) -> CellValue:
        return getattr(self.world[(x, y)], attribute)
