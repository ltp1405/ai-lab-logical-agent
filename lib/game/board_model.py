from collections import namedtuple
from dataclasses import dataclass
import enum
from lib.game.board_data import BoardData, TileType
from lib.percepts import Percepts

GOLD_POINTS = 100
PIT_POINTS = -10000
WUMPUS_POINTS = -10000
ARROW_POINTS = -100
CLIMB_OUT_POINTS = 10
MOVE_POINTS = -10


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Action(enum.Enum):
    MOVE = 1
    SHOOT = 2
    CLIMB = 3


@dataclass
class Position:
    x: int
    y: int


class BoardModel:
    def __init__(self, board_data: BoardData):
        self.board_data = board_data
        self.board = board_data.board_data
        self.revealed = [
            [False for _ in range(self.board_data.width)]
            for _ in range(self.board_data.height)
        ]
        self.width = board_data.width
        self.height = board_data.height
        # x, y
        self._agent = Position(
            x=self.board_data.initial_agent_pos[1],
            y=self.board_data.height - 1 - self.board_data.initial_agent_pos[0],
        )
        self.agent_direction = Direction.RIGHT
        self.points = 0
        self.game_over = False
        self.current_percepts = Percepts()
        self._update_percepts()
        self.revealed[self._agent.y][self._agent.x] = True
        self.initial_agent_pos = self._agent

    def _current_agent_tile_on_board(self) -> set[TileType]:
        y, x = self._agent.y, self._agent.x
        y = self.board_data.height - 1 - y
        return self.board_data.board_data[y][x]

    def change_agent_direction(self, direction: Direction):
        self.agent_direction = direction

    def _update_percepts(self):
        tiles = self._current_agent_tile_on_board()
        percepts = Percepts()
        for tile in tiles:
            if tile == TileType.GOLD:
                percepts["glitter"] = True
            elif tile == TileType.BREEZE:
                percepts["breeze"] = True
            elif tile == TileType.STENCH:
                percepts["stench"] = True
        self.current_percepts = percepts

    def act(self, action: Action) -> Percepts:
        """
        Move the agent in the given direction.
        Return the tiles that the agent can perceive (percepts).
        The order is [up, down, left, right].
        - None if the agent cannot perceive that tile (out of bounds)
        - [] if the agent can perceive that tile but there is nothing there
        """
        if self.game_over:
            raise Exception(f"Game is over: {self.points} points")
        if action == Action.MOVE:
            y, x = self._agent.y, self._agent.x
            if (
                self._agent == Position(x=0, y=0)
                and self.agent_direction == Direction.DOWN
            ):
                self.points += CLIMB_OUT_POINTS
                self.game_over = True
                print(f"Points: {self.points}")
                return self.current_percepts
            if self.agent_direction == Direction.UP:
                y += 1
            elif self.agent_direction == Direction.DOWN:
                y -= 1
            elif self.agent_direction == Direction.LEFT:
                x -= 1
            elif self.agent_direction == Direction.RIGHT:
                x += 1
            if 0 <= y < self.board_data.height and 0 <= x < self.board_data.width:
                self._agent = Position(x=x, y=y)
                y = self.board_data.height - 1 - y
                x = self._agent.x
                self.revealed[y][x] = True
                self.points += MOVE_POINTS
                tiles = self._current_agent_tile_on_board()
                percepts = Percepts()
                remove_gold = False
                for tile in tiles:
                    if tile == TileType.GOLD:
                        self.points += GOLD_POINTS
                        print(f"Points: {self.points}")
                        percepts["glitter"] = True
                        remove_gold = True
                    elif tile == TileType.PIT:
                        self.points += PIT_POINTS
                        self.game_over = True
                        print(f"Points: {self.points}")
                    elif tile == TileType.WUMPUS:
                        self.points += WUMPUS_POINTS
                        self.game_over = True
                        print(f"Points: {self.points}")
                    elif tile == TileType.BREEZE:
                        percepts["breeze"] = True
                    elif tile == TileType.STENCH:
                        percepts["stench"] = True
                if remove_gold:
                    self.board_data.board_data[y][x].remove(TileType.GOLD)
                self.current_percepts = percepts
                return percepts
            else:
                percepts = self.current_percepts
                percepts["bump"] = True
                return percepts
        elif action == Action.SHOOT:
            percepts = self.current_percepts
            hit = self._shoot()
            if hit:
                percepts["scream"] = True
            return percepts

        elif action == Action.CLIMB:
            if self._agent == Position(x=0, y=0):
                self.points += CLIMB_OUT_POINTS
                self.game_over = True
                print(f"Points: {self.points}")
                return self.current_percepts
            raise Exception("Cannot climb out: not at (0, 0)")

    def _remove_stench_around(self, x: int, y: int):
        try:
            if TileType.STENCH in self.board_data.board_data[y - 1][x]:
                self.board_data.board_data[y - 1][x].remove(TileType.STENCH)
        except IndexError:
            pass
        try:
            if TileType.STENCH in self.board_data.board_data[y + 1][x]:
                self.board_data.board_data[y + 1][x].remove(TileType.STENCH)
        except IndexError:
            pass
        try:
            if TileType.STENCH in self.board_data.board_data[y][x - 1]:
                self.board_data.board_data[y][x - 1].remove(TileType.STENCH)
        except IndexError:
            pass
        try:
            if TileType.STENCH in self.board_data.board_data[y][x + 1]:
                self.board_data.board_data[y][x + 1].remove(TileType.STENCH)
        except IndexError:
            pass

    def model_agent_position(self) -> Position:
        """
        Row-first top-down position of the agent
        """
        return self._agent

    def tl_agent_position(self) -> Position:
        """
        Position of the agent relative to the top-left corner
        """
        return Position(
            x=self._agent.x,
            y=self.board_data.height - 1 - self._agent.y,
        )

    def _shoot(self) -> bool:
        self.points += ARROW_POINTS
        match self.agent_direction:
            case Direction.UP:
                for y in range(self._agent.y + 1, self.board_data.height):
                    y = self.board_data.height - 1 - y
                    if TileType.WUMPUS in self.board_data.board_data[y][self._agent.x]:
                        self.board_data.board_data[y][self._agent.x].remove(
                            TileType.WUMPUS
                        )
                        self._remove_stench_around(self._agent.x, y)
                        return True
            case Direction.DOWN:
                for y in range(self._agent.y - 1, 0, -1):
                    y = self.board_data.height - 1 - y
                    if TileType.WUMPUS in self.board_data.board_data[y][self._agent.x]:
                        self.board_data.board_data[y][self._agent.x].remove(
                            TileType.WUMPUS
                        )
                        print("REMOVING WUMPUS")
                        self._remove_stench_around(self._agent.x, y)
                        return True
            case Direction.LEFT:
                y = self.board_data.height - 1 - self._agent.y
                for x in range(self._agent.x - 1, 0, -1):
                    if TileType.WUMPUS in self.board_data.board_data[y][x]:
                        self.board_data.board_data[y][x].remove(TileType.WUMPUS)
                        self._remove_stench_around(x, y)
                        return True
            case Direction.RIGHT:
                y = self.board_data.height - 1 - self._agent.y
                for x in range(self._agent.x + 1, self.board_data.width):
                    if TileType.WUMPUS in self.board_data.board_data[y][x]:
                        self.board_data.board_data[y][x].remove(TileType.WUMPUS)
                        self._remove_stench_around(x, y)
                        return True
        return False
