from typing import Dict, Tuple, Set
from lib.game.board_model import Action, Direction
from lib.game.board_data import TileType
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import Cell, CellValue
from lib.knowledge_base.knowledge_base import KnowledgeBase
from lib.percepts import Percepts
from copy import deepcopy
from rich import print


# x , y, predicate, value
Clause = Tuple[int, int, str, CellValue]


class Agent:
    def __init__(
        self,
        board: BoardModelWithKB,
    ) -> None:
        self.board = board
        self._is_alive = True
        self._find_gold = False

    def is_alive(self) -> bool:
        return self._is_alive

    def has_found_gold(self) -> bool:
        return self._find_gold

    def knowledge_base(self) -> KnowledgeBase:
        return self.board.kb

    def my_world(self) -> Dict[Tuple[int, int], Cell]:
        return self.board.get_known_tiles()

    def inspect(self, position: Tuple[int, int]) -> bool:
        """Inspect the position in the knowledge base. Check if the position is safe.

        Args:
            position (Tuple[int, int]): Position to inspect

        Returns:
            bool: Whether the position is safe
        """
        if position in self.my_world():
            return self.my_world()[position].is_safe
        return False

    def infer(
        self,
        alpha: Clause,
    ) -> bool:
        world = deepcopy(self.my_world())
        n_alpha = (alpha[0], alpha[1], alpha[2], CellValue.negate(alpha[-1]))
        x, y, predicate, value = n_alpha
        adjacent_rooms = self._adjacent_rooms((x, y))
        for room in adjacent_rooms:
            if room in world:
                match predicate:
                    case "is_pit":
                        if world[room].is_breeze == CellValue.MAYBE:
                            # Empty clause found
                            return False
                        if world[room].is_breeze == CellValue.negate(value):
                            # Empty clause found
                            return True
                    case "is_wumpus":
                        if world[room].is_stench == CellValue.MAYBE:
                            return False
                        if world[room].is_stench == CellValue.negate(value):
                            return True
        return False

    def find_adjacent_rooms(self) -> Set[Tuple[int, int]]:
        x, y = (
            self.board.virtual_agent_position().x,
            self.board.virtual_agent_position().y,
        )
        return self._adjacent_rooms((x, y))

    def _adjacent_rooms(self, position: Tuple[int, int]) -> Set[Tuple[int, int]]:
        x, y = position
        top, bottom, left, right = self.board.known_bounds()
        res = set()
        if top is None or y < top:
            res.add((x, y + 1))
        if right is None or x < right:
            res.add((x + 1, y))
        if left is None or x > left:
            res.add((x - 1, y))
        if bottom is None or y > bottom:
            res.add((x, y - 1))
        _, bottom, left, _ = self.board.known_bounds()
        if bottom is not None and left is not None:
            if (left, bottom - 1) in res and not self._find_gold:
                res.remove((left, bottom - 1))
        return res

    def take_action(self, action: Action, to_room: Tuple[int, int]) -> Percepts:
        """Takes an action in the board

        Args:
            action (Action): Action to take
            to_room (Tuple[int, int]): Room to move to, or to shoot to, to identify the direction
        Returns:
            bool: Whether the agent is still alive
        """
        try:
            direction = self.board.identify_direction_to_modify(to_room)
            self.board.change_agent_direction(direction)
            percepts = self.board.act(action)
            top, bottom, left, right = self.board.known_bounds()
            print(f"Known bounds: {top}, {bottom}, {left}, {right}")
            print(f"Agent percepts: {percepts}")
            if percepts['glitter']:
                self._find_gold = True
                print ("Found gold")
            # Check the current percepts to see if the agent is still alive
            self._is_alive = not self.board.game_over
            return percepts
        except Exception as e:
            if e.args[0].startswith("Cannot climb out"):
                return self.board.current_percepts
