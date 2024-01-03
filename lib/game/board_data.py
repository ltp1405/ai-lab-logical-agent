from dataclasses import dataclass
from enum import Enum

from lib.coord import CartesianCoord, DownwardCoord


class TileType(Enum):
    WUMPUS = 1
    PIT = 2
    GOLD = 3
    BREEZE = 4
    STENCH = 5

    def __repr__(self) -> str:
        return self.name[0]

    def __str__(self) -> str:
        match self:
            case TileType.WUMPUS:
                return "W"
            case TileType.PIT:
                return "P"
            case TileType.GOLD:
                return "G"
            case TileType.BREEZE:
                return "B"
            case TileType.STENCH:
                return "S"


@dataclass
class BoardData:
    height: int
    width: int
    board_data: list[list[set[TileType]]]
    initial_agent_pos: DownwardCoord


def read_board_data(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        height = int(lines[0])
        lines = lines[1:]
        width = len(lines[0].split("."))
        board_data = [[set() for _ in range(width)] for _ in range(height)]
        agent_pos = None
        no_wumpus = True

        for y, line in enumerate(lines):
            for x, tiles in enumerate(line.split(".")):
                tiles = tiles.upper()
                for tile in tiles:
                    if tile == "W":
                        board_data[y][x].add(TileType.WUMPUS)
                        no_wumpus = False
                    elif tile == "P":
                        board_data[y][x].add(TileType.PIT)
                    elif tile == "G":
                        board_data[y][x].add(TileType.GOLD)
                    elif tile == "A":
                        agent_pos = (y, x)

        if agent_pos is None:
            raise ValueError("No agent position found in map file")
        if no_wumpus:
            raise ValueError("No wumpus found in map file")
        if height > 10 or width > 10:
            raise ValueError("Map too big")

        agent_pos = DownwardCoord(agent_pos[0], agent_pos[1])
        put_enviroment(board_data)
        print(board_data)
        return BoardData(height, width, board_data, agent_pos)


def put_enviroment(board_data):
    height = len(board_data)
    width = len(board_data[0])
    for y in range(len(board_data)):
        for x in range(len(board_data[y])):
            if TileType.WUMPUS in board_data[y][x]:
                if y > 0:
                    board_data[y - 1][x].add(TileType.STENCH)
                if y < height - 1:
                    board_data[y + 1][x].add(TileType.STENCH)
                if x > 0:
                    board_data[y][x - 1].add(TileType.STENCH)
                if x < width - 1:
                    board_data[y][x + 1].add(TileType.STENCH)
            if TileType.PIT in board_data[y][x]:
                if y > 0:
                    board_data[y - 1][x].add(TileType.BREEZE)
                if y < height - 1:
                    board_data[y + 1][x].add(TileType.BREEZE)
                if x > 0:
                    board_data[y][x - 1].add(TileType.BREEZE)
                if x < width - 1:
                    board_data[y][x + 1].add(TileType.BREEZE)
