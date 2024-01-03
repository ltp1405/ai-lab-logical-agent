from rich.table import Table
from lib.game.board_data import TileType
from lib.game.map_generator import generate_map
from rich import print

def print_map_debug(map: list[list[set[TileType]]], initial_agent_position):
    table = Table(show_header=False, show_lines=True)
    str_map = [[str() for _ in range(len(map[0]))] for _ in range(len(map))]
    for y in range(len(map)):
        for x in range(len(map[0])):
            tile_str = str()
            tile_str += "W" if TileType.WUMPUS in map[y][x] else " "
            tile_str += "P" if TileType.PIT in map[y][x] else " "
            tile_str += "G" if TileType.GOLD in map[y][x] else " "
            tile_str += "A" if (x, y) == initial_agent_position else " "
            str_map[y][x] = tile_str

    for y in range(len(map)):
        table.add_row(*str_map[y])
    print(table)


def main():
    map = generate_map(
        map_size=None,
        initial_agent_position=None,
        wumpus_count=None,
        pit_count=None,
        gold_count=None,
        seed=5,
    )
    print_map_debug(map.board_data, map.board_data.initial_agent_pos)


if __name__ == "__main__":
    main()
