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


class BoardModel:
    def __init__(self, board_data: BoardData):
        self.board_data = board_data
        self.board = board_data.board_data
        self.revealed = [
            [False for _ in range(self.board_data.width)]
            for _ in range(self.board_data.height)
        ]
        # y, x
        self.width = board_data.width
        self.height = board_data.height
        self.agent = board_data.initial_agent_pos
        self.agent_direction = Direction.RIGHT
        self.points = 0
        self.game_over = False
        self.current_percepts = Percepts()
        self._update_percepts()
        self.revealed[self.agent[0]][self.agent[1]] = True
        self.initial_agent_pos = board_data.initial_agent_pos

    def _current_agent_tiles(self) -> set[TileType]:
        y, x = self.agent
        return self.board_data.board_data[y][x]

    def current_agent_position(self) -> tuple[int, int]:
        return self.agent

    def change_agent_direction(self, direction: Direction):
        self.agent_direction = direction

    def _update_percepts(self):
        tiles = self._current_agent_tiles()
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
            y, x = self.agent
            if (
                self.agent == (self.board_data.height - 1, 0)
                and self.agent_direction == Direction.DOWN
            ):
                self.points += CLIMB_OUT_POINTS
                self.game_over = True
                print(f"Points: {self.points}")
                return self.current_percepts
            if self.agent_direction == Direction.UP:
                y -= 1
            elif self.agent_direction == Direction.DOWN:
                y += 1
            elif self.agent_direction == Direction.LEFT:
                x -= 1
            elif self.agent_direction == Direction.RIGHT:
                x += 1
            if 0 <= y < self.board_data.height and 0 <= x < self.board_data.width:
                self.agent = (y, x)
                self.revealed[y][x] = True
                self.points += MOVE_POINTS
                tiles = self._current_agent_tiles()
                percepts = Percepts()
                for tile in tiles:
                    if tile == TileType.GOLD:
                        self.points += GOLD_POINTS
                        print(f"Points: {self.points}")
                        percepts["glitter"] = True
                        self.board_data.board_data[y][x].remove(TileType.GOLD)
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
            if self.agent == (self.board_data.height - 1, 0):
                self.points += CLIMB_OUT_POINTS
                self.game_over = True
                print(f"Points: {self.points}")
                return self.current_percepts
            raise Exception("Cannot climb out: not at (1, 1)")

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

    def _shoot(self) -> bool:
        self.points += ARROW_POINTS
        match self.agent_direction:
            case Direction.UP:
                for y in range(self.agent[0] - 1, -1, -1):
                    if self.board_data.board_data[y][self.agent[1]] == [
                        TileType.WUMPUS
                    ]:
                        self.board_data.board_data[y][self.agent[1]].remove(
                            TileType.WUMPUS
                        )
                        self._remove_stench_around(self.agent[1], y)
                        return True
            case Direction.DOWN:
                for y in range(self.agent[0] + 1, self.board_data.height):
                    if self.board_data.board_data[y][self.agent[1]] == [
                        TileType.WUMPUS
                    ]:
                        self.board_data.board_data[y][self.agent[1]].remove(
                            TileType.WUMPUS
                        )
                        self._remove_stench_around(self.agent[1], y)
                        return True
            case Direction.LEFT:
                for x in range(self.agent[1] - 1, -1, -1):
                    if self.board_data.board_data[self.agent[0]][x] == [
                        TileType.WUMPUS
                    ]:
                        self.board_data.board_data[self.agent[0]][x].remove(
                            TileType.WUMPUS
                        )
                        self._remove_stench_around(x, self.agent[0])
                        return True
            case Direction.RIGHT:
                for x in range(self.agent[1] + 1, self.board_data.width):
                    if self.board_data.board_data[self.agent[0]][x] == [
                        TileType.WUMPUS
                    ]:
                        self.board_data.board_data[self.agent[0]][x].remove(
                            TileType.WUMPUS
                        )
                        self._remove_stench_around(x, self.agent[0])
                        return True
        return False
