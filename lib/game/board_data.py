from dataclasses import dataclass
from enum import Enum


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
    board_data: list[list[list[TileType]]]


def read_board_data(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        height = int(lines[0])
        lines = lines[1:]
        width = len(lines[0].split("."))
        board_data = [[[] for _ in range(width)] for _ in range(height)]
        for y, line in enumerate(lines):
            for x, tiles in enumerate(line.split(".")):
                tiles = tiles.upper()
                for tile in tiles:
                    if tile == "W":
                        board_data[y][x].append(TileType.WUMPUS)
                    elif tile == "P":
                        board_data[y][x].append(TileType.PIT)
                    elif tile == "G":
                        board_data[y][x].append(TileType.GOLD)
                    elif tile == "B":
                        board_data[y][x].append(TileType.BREEZE)
                    elif tile == "S":
                        board_data[y][x].append(TileType.STENCH)
        return BoardData(height, width, board_data)
