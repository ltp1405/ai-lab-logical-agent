from dataclasses import dataclass
from ..percepts import Percepts
import enum
from typing import List, Tuple
import pygame
import copy
import random

from lib.game.board_data import BoardData, TileType

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


class Board:
    def __init__(self, board_data: BoardData, x: int, y: int, tile_size: int):
        self.tile_size = tile_size
        self.board_data = board_data
        self.x = x
        self.y = y
        self.height = self.board_data.height * self.tile_size
        self.width = self.board_data.width * self.tile_size
        self.board_surface = pygame.Surface((self.width, self.height))
        self.grid_color = (255, 255, 255)
        self.revealed = [
            [False for _ in range(self.board_data.width)]
            for _ in range(self.board_data.height)
        ]
        # y, x
        self.agent = board_data.initial_agent_pos
        self.agent_direction = Direction.RIGHT
        self.points = 0
        self.game_over = False
        self.current_percepts = Percepts()
        self._update_percepts()
        self.revealed[self.agent[0]][self.agent[1]] = True

    def _current_agent_tiles(self) -> List[TileType]:
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

    def draw(self, surface: pygame.Surface):
        self.board_surface.fill((0, 0, 0))
        self._draw_tiles()
        self._draw_agent()
        # self._draw_grid()
        # self._draw_border()
        surface.blit(self.board_surface, (self.x, self.y))

    def _draw_tiles(self):
        for y, row in enumerate(self.board_data.board_data):
            for x, _ in enumerate(row):
                if self.revealed[y][x]:
                    self._draw_tile(x, y)

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

    def _draw_tile(self, x, y):
        tile_type = self.board_data.board_data[y][x]
        if (y, x) == (self.board_data.height - 1, 0):
            color = (0, 255, 0)
            text = "D"
        elif tile_type == [TileType.WUMPUS]:
            color = (255, 0, 0)
            text = "W"
        elif tile_type == [TileType.PIT]:
            color = "#b76014"
            text = "P"
        elif tile_type == [TileType.GOLD]:
            color = (255, 255, 0)
            text = "G"
        elif tile_type == [TileType.BREEZE]:
            color = (0, 255, 255)
            text = "B"
        elif tile_type == [TileType.STENCH]:
            color = (255, 0, 255)
            text = "S"
        elif set(tile_type) == set([TileType.BREEZE, TileType.STENCH]):
            color = (255, 255, 255)
            text = "BS"
        elif set(tile_type) == set([TileType.BREEZE, TileType.GOLD]):
            color = (255, 255, 255)
            text = "BG"
        elif set(tile_type) == set([TileType.STENCH, TileType.GOLD]):
            color = (255, 255, 255)
            text = "SG"
        elif set(tile_type) == set([TileType.BREEZE, TileType.STENCH, TileType.GOLD]):
            color = (255, 255, 255)
            text = "BSG"
        else:
            color = (100, 100, 100)
            text = ""
        font = pygame.font.SysFont("Mono", 20)
        pygame.draw.rect(
            self.board_surface,
            color,
            (
                x * self.tile_size,
                y * self.tile_size,
                self.tile_size,
                self.tile_size,
            ),
        )
        text_surface = font.render(text, True, (0, 0, 0))
        self.board_surface.blit(
            text_surface,
            (
                x * self.tile_size + self.tile_size / 2 - text_surface.get_width() / 2,
                y * self.tile_size + self.tile_size / 2 - text_surface.get_height() / 2,
            ),
        )

    def _draw_agent(self):
        y, x = self.agent
        pygame.draw.rect(
            self.board_surface,
            (0, 255, 0),
            (
                x * self.tile_size,
                y * self.tile_size,
                self.tile_size,
                self.tile_size,
            ),
        )
        match self.agent_direction:
            case Direction.UP:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size + self.tile_size / 4,
                        y * self.tile_size,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )
            case Direction.DOWN:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size + self.tile_size / 4,
                        y * self.tile_size + self.tile_size / 2,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )
            case Direction.LEFT:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size,
                        y * self.tile_size + self.tile_size / 4,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )
            case Direction.RIGHT:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size + self.tile_size / 2,
                        y * self.tile_size + self.tile_size / 4,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )

    def _draw_border(self):
        pygame.draw.rect(
            self.board_surface, self.grid_color, (0, 0, self.width, self.height), 1
        )

    def _draw_grid(self):
        # draw vertical lines
        for x in range(0, self.width, self.tile_size):
            pygame.draw.line(
                self.board_surface, self.grid_color, (x, 0), (x, self.height)
            )

        # draw horizontal lines
        for y in range(0, self.height, self.tile_size):
            pygame.draw.line(
                self.board_surface, self.grid_color, (0, y), (self.width, y)
            )

    def update(self, dt):
        pass

    def handle_event(self, event):
        pass
