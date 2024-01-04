from rich.table import Table
from lib.game.board_data import TileType
from lib.game.map_generator import generate_map
from rich import print
from lib.game.board_data import print_map_debug


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
