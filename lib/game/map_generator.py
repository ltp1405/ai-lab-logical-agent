from collections import namedtuple
import random
from typing import Tuple
from rich import print
from rich.box import Box
from rich.table import Table, box
from rich.panel import Panel

from lib.game.board_data import TileType


def _check_have_path_to_exit(map: list[list[set]], x: int, y: int) -> bool:
    if TileType.PIT in map[y][x]:
        return False
    queue = [(x, y)]
    visited = set()
    while len(queue) > 0:
        x, y = queue.pop(0)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if x == 0 and y == len(map) - 1:
            return True
        if x > 0 and TileType.PIT not in map[y][x - 1]:
            queue.append((x - 1, y))
        if x < len(map[0]) - 1 and TileType.PIT not in map[y][x + 1]:
            queue.append((x + 1, y))
        if y > 0 and TileType.PIT not in map[y - 1][x]:
            queue.append((x, y - 1))
        if y < len(map) - 1 and TileType.PIT not in map[y + 1][x]:
            queue.append((x, y + 1))
    return False


def _put_tiles(
    map: list[list[set]],
    wumpus_count: int,
    pit_count: int,
    gold_count: int,
    initial_agent_position: Tuple[int, int],
):
    current_wumpus_count = 0
    current_pit_count = 0
    current_gold_count = 0
    while True:
        choice = random.randint(0, 2)
        if current_wumpus_count < wumpus_count and choice == 0:
            while True:
                x = random.randint(0, len(map[0]) - 1)
                y = random.randint(0, len(map) - 1)
                if TileType.WUMPUS not in map[y][x]:
                    map[y][x].add(TileType.WUMPUS)
                    current_wumpus_count += 1
                    break
        if current_pit_count < pit_count and choice == 1:
            while True:
                x = random.randint(0, len(map[0]) - 1)
                y = random.randint(0, len(map) - 1)
                if TileType.PIT not in map[y][x]:
                    map[y][x].add(TileType.PIT)
                    if _check_have_path_to_exit(
                        map, initial_agent_position[0], initial_agent_position[1]
                    ) == False:
                        map[y][x].remove(TileType.PIT)
                        continue
                    current_pit_count += 1
                    break
        if current_gold_count < gold_count and choice == 2:
            while True:
                x = random.randint(0, len(map[0]) - 1)
                y = random.randint(0, len(map) - 1)
                if (
                    TileType.GOLD not in map[y][x]
                    and TileType.WUMPUS not in map[y][x]
                    and TileType.PIT not in map[y][x]
                ):
                    map[y][x].add(TileType.GOLD)
                    current_gold_count += 1
                    break
        if (
            current_wumpus_count == wumpus_count
            and current_pit_count == pit_count
            and current_gold_count == gold_count
        ):
            break


def generate_map(
    map_size: Tuple[int, int] | None = (4, 4),
    initial_agent_position: Tuple[int, int] | None = (0, 0),
    wumpus_count: None | int = 1,
    pit_count: None | int = 3,
    gold_count: None | int = 1,
    seed=1,
):
    previous_seed = random.getstate()
    random.seed(seed)

    if map_size is None:
        map_size = (random.randint(4, 10), random.randint(4, 10))

    map = [[set() for _ in range(map_size[0])] for _ in range(map_size[1])]

    if wumpus_count is None:
        wumpus_count = random.randint(1, int(map_size[0] * map_size[1] / 5))

    if pit_count is None:
        pit_count = random.randint(1, int(map_size[0] * map_size[1] / 5))

    if gold_count is None:
        gold_count = random.randint(1, int(map_size[0] * map_size[1] / 5))

    if initial_agent_position is None:
        initial_agent_position = (
            random.randint(0, map_size[0] - 1),
            random.randint(0, map_size[1] - 1),
        )

    _put_tiles(
        map,
        wumpus_count,
        pit_count,
        gold_count,
        initial_agent_position,
    )

    random.setstate(previous_seed)

    Result = namedtuple(
        "Map",
        [
            "map",
            "initial_agent_position",
            "wumpus_count",
            "pit_count",
            "gold_count",
        ],
    )
    return Result(
        map,
        initial_agent_position,
        wumpus_count,
        pit_count,
        gold_count,
    )