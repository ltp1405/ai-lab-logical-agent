from copy import Error, deepcopy
from typing import Any, Dict, List, Tuple
from lib.game.board_model import Action, Direction
from lib.knowledge_base.cell import CellValue
from lib.knowledge_base.world_view import WorldView
from lib.percepts import Percepts


class KnowledgeBase:
    def __init__(self) -> None:
        self.world: WorldView = WorldView()
        self.top: int | None = None
        self.right: int | None = None
        self.bottom: int | None = None
        self.left: int | None = None

    def __getattribute__(self, __name: str) -> Any:
        match __name:
            case "exit":
                if self.left != None and self.bottom != None:
                    return (self.left, self.bottom)
            case "safe_cells":
                safe_cells: List[Tuple[int, int]] = []
                for i in range(-11, 10):
                    for j in range(-11, 10):
                        if self.world[(i, j)].is_safe:
                            if self.check_oob(i, j):
                                continue
                            safe_cells.append((i, j))
                return safe_cells
            case "wumpus_cells":
                wumpus_cells: List[Tuple[Tuple[int, int], CellValue]] = []
                for i in range(-11, 10):
                    for j in range(-11, 10):
                        if self.check_oob(i, j):
                            continue
                        if self.world[(i, j)].is_wumpus == CellValue.TRUE:
                            wumpus_cells.insert(
                                0,
                                ((i, j), CellValue.TRUE),
                            )
                        elif self.world[(i, j)].is_wumpus == CellValue.MAYBE:
                            wumpus_cells.insert(
                                -1,
                                ((i, j), CellValue.MAYBE),
                            )
                return wumpus_cells
            case "pit_cells":
                pit_cells: List[Tuple[Tuple[int, int], CellValue]] = []
                for i in range(-11, 10):
                    for j in range(-11, 10):
                        if self.check_oob(i, j):
                            continue
                        if self.world[(i, j)].is_pit == CellValue.TRUE:
                            pit_cells.insert(
                                0,
                                ((i, j), CellValue.TRUE),
                            )
                        elif self.world[(i, j)].is_pit == CellValue.MAYBE:
                            pit_cells.insert(
                                -1,
                                ((i, j), CellValue.MAYBE),
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
    ) -> Dict[Tuple[int, int], Any]:
        res: Dict[Tuple[int, int], Any] = {}
        print(f"tell: ({x}, {y})")
        self.world[(x, y)].is_safe = True
        if percept["bump"]:
            if action == None:
                raise Error("No action provided for bump percept")
            else:
                # set_bound_res: Dict[Tuple[int, int], Any]
                match action[1]:
                    case Direction.UP:
                        self.top = y
                        self.world.set_bound(Direction.UP, y)
                    case Direction.RIGHT:
                        self.right = x
                        self.world.set_bound(Direction.RIGHT, x)
                    case Direction.DOWN:
                        self.bottom = y
                        self.world.set_bound(Direction.DOWN, y)
                    case Direction.LEFT:
                        self.left = x
                        self.world.set_bound(Direction.LEFT, x)
                # res.update(set_bound_res)
        stench_res: Dict[Tuple[int, int], Any]
        if percept["stench"]:
            stench_res = self.world.set_item((x, y, "is_stench"), CellValue.TRUE)
        else:
            stench_res = self.world.set_item((x, y, "is_stench"), CellValue.FALSE)
        if action == None:
            pass
        elif percept["scream"]:
            match action[1]:
                case Direction.UP:
                    self.world.set_item((x, y + 1, "is_safe"), True)
                    res[(x, y + 1)] = self.world[(x, y + 1)]
                case Direction.DOWN:
                    self.world.set_item((x, y - 1, "is_safe"), True)
                    res[(x, y - 1)] = self.world[(x, y - 1)]
                case Direction.LEFT:
                    print("set safe", x - 1, y)
                    self.world.set_item((x - 1, y, "is_safe"), True)
                    res[(x - 1, y)] = self.world[(x - 1, y)]
                case Direction.RIGHT:
                    self.world.set_item((x + 1, y, "is_safe"), True)
                    res[(x + 1, y)] = self.world[(x + 1, y)]
        elif action[0] == Action.SHOOT:
            match action[1]:
                case Direction.UP:
                    self.world.set_item((x, y + 1, "is_wumpus"), CellValue.FALSE)
                    res[(x, y + 1)] = self.world[(x, y + 1)]
                case Direction.DOWN:
                    self.world.set_item((x, y - 1, "is_wumpus"), CellValue.FALSE)
                    res[(x, y - 1)] = self.world[(x, y - 1)]
                case Direction.LEFT:
                    self.world.set_item((x - 1, y, "is_wumpus"), CellValue.FALSE)
                    res[(x - 1, y)] = self.world[(x - 1, y)]
                case Direction.RIGHT:
                    self.world.set_item((x + 1, y, "is_wumpus"), CellValue.FALSE)
                    res[(x + 1, y)] = self.world[(x + 1, y)]
        res.update(stench_res)
        breeze_res: Dict[Tuple[int, int], Any]
        if percept["breeze"]:
            breeze_res = self.world.set_item((x, y, "is_breeze"), CellValue.TRUE)
        else:
            breeze_res = self.world.set_item((x, y, "is_breeze"), CellValue.FALSE)
        res.update(breeze_res)
        if percept["glitter"]:
            self.world[(x, y)].is_gold = CellValue.TRUE
        else:
            self.world[(x, y)].is_gold = CellValue.FALSE
        res[(x, y)] = self.world[(x, y)]
        return res

    def ask(self, x: int, y: int, attribute: str) -> CellValue:
        return getattr(self.world[(x, y)], attribute)

    def check_oob(self, x: int, y: int) -> bool:
        if self.top != None and y > self.top:
            return True
        if self.right != None and x > self.right:
            return True
        if self.bottom != None and y < self.bottom:
            return True
        if self.left != None and x < self.left:
            return True
        return False
