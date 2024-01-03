from enum import Enum
from typing import List, Tuple, Set, Dict
from lib.game.board_model import Action, Direction
from lib.game.board_data import TileType
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import Cell, CellValue
from lib.knowledge_base.knowledge_base import KnowledgeBase
from lib.percepts import Percepts
from copy import deepcopy
from rich import print
import random


# x , y, predicate, value
Clause = Tuple[int, int, str, CellValue]


class Decision(Enum):
    EXIT = 1
    CONTINUE = 2
    BACKTRACK = 3
    RESTART = 4


class AgentState(Enum):
    FIND_GOLD = 1
    TRY_TO_EXIT = 2


class Agent:
    def __init__(
        self,
        board: BoardModelWithKB,
    ) -> None:
        self.board = board
        self.golds = 0
        self.state = AgentState.FIND_GOLD
        self.stack: List[Tuple[int, int]] = [(0, 0)]

    def identify_direction(self, room: Tuple[int, int]) -> Direction:
        x, y = (
            self.board.virtual_agent_position().x,
            self.board.virtual_agent_position().y,
        )
        if room == (x, y + 1):
            return Direction.UP
        elif room == (x, y - 1):
            return Direction.DOWN
        elif room == (x + 1, y):
            return Direction.RIGHT
        elif room == (x - 1, y):
            return Direction.LEFT
        raise Exception("Cannot identify direction")

    def safe_rooms(
        self,
        find_all: bool = False,
    ) -> List[Tuple[int, int]]:
        safe_cells: List[Tuple[int, int]] = self.board.kb.__getattribute__("safe_cells")
        if find_all:
            return safe_cells
        adjacent_rooms = self._adjacent_rooms()
        return [room for room in safe_cells if room in adjacent_rooms]

    def wumpus_rooms(
        self,
        target: CellValue | None = None,
    ) -> Dict[Tuple[int, int], CellValue] | List[Tuple[int, int]]:
        wumpus_cells = self.board.kb.__getattribute__("wumpus_cells")
        converted = self._convert(wumpus_cells)
        if target in (CellValue.TRUE, CellValue.MAYBE):
            return [room for room in converted if converted[room] == target]
        return converted

    def pit_rooms(
        self,
        target: CellValue | None = None,
    ) -> List[Tuple[Tuple[int, int], CellValue]] | List[Tuple[int, int]]:
        pit_cells = self.board.kb.__getattribute__("pit_cells")
        converted = self._convert(pit_cells)
        if target in (CellValue.TRUE, CellValue.MAYBE):
            return [room for room in converted if converted[room] == target]
        return converted

    def _convert(
        self, rooms: List[Tuple[Tuple[int, int], CellValue]]
    ) -> Dict[Tuple[int, int], CellValue]:
        """Converts a list of rooms to a dictionary. Only use adjacent rooms

        Args:
            rooms (List[Tuple[Tuple[int, int], CellValue]]): List of rooms and its predicate

        Returns:
            Dict[Tuple[int, int], CellValue]: Dictionary of rooms and its predicate
        """
        adjacent_rooms = self._adjacent_rooms()
        res = dict()
        for room in rooms:
            if room[0] in adjacent_rooms:
                res[room[0]] = room[1]
        return res

    def exit_room(self) -> Tuple[int, int] | None:
        _, bottom, left, _ = self.board.known_bounds()
        if bottom is not None and left is not None:
            return self.board.kb.__getattribute__("exit")
        return None

    def backtrack(self) -> Tuple[int, int] | None:
        # Pop the current room off the stack if len(stack) > 1
        if len(self.stack) > 1:
            self.stack.pop()
            return self.stack[-1]
        return None

    def latest_room(self) -> Tuple[int, int] | None:
        if len(self.stack) == 0:
            return None
        return self.stack[-1]

    def _adjacent_rooms(self) -> Set[Tuple[int, int]]:
        x, y = (
            self.board.virtual_agent_position().x,
            self.board.virtual_agent_position().y,
        )
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
            if (left, bottom - 1) in res and self.state is not AgentState.TRY_TO_EXIT:
                res.remove((left, bottom - 1))
        return res

    def random_select_room(self, rooms: List[Tuple[int, int]]) -> Tuple[int, int]:
        if len(rooms) == 1:
            return rooms[0]
        if self.state == AgentState.TRY_TO_EXIT:
            # Prioritize the exit room: going DOWN, LEFT
            filtered_rooms = [room for room in rooms if self.identify_direction(room) in (Direction.DOWN, Direction.LEFT)]
            if len(filtered_rooms) > 0:
                return random.choice(filtered_rooms)
        room = random.choice(rooms)
        while (
            self.state == AgentState.FIND_GOLD
            and self.identify_direction(room) == Direction.DOWN
        ):
            room = random.choice(rooms)
        return room

    def take_action(
        self,
        action: Action,
        to_room: Tuple[int, int],
    ) -> Percepts:
        """Takes an action in the board

        Args:
            action (Action): Action to take
            to_room (Tuple[int, int]): Room to move to, or to shoot to, to identify the direction
        Returns:
            bool: Whether the agent is still alive
        """
        direction = self.board.identify_direction_to_modify(to_room)
        self.board.change_agent_direction(direction)
        percepts = self.board.act(action)
        top, bottom, left, right = self.board.known_bounds()
        if action == Action.MOVE:
            if self.stack[-1] == to_room:
                self.stack.pop()
            self.stack.append(to_room)
        print(f"Known bounds: {top}, {bottom}, {left}, {right}")
        if percepts["glitter"]:
            self.golds += 1
        # Check the current percepts to see if the agent is still alive
        self._is_alive = not self.board.game_over
        return percepts
