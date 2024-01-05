from collections import namedtuple
from lib.coord import DownwardCoord
from lib.game.game import summary


def parse_args():
    # parse arguments using argparse
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed",
        type=int,
        default=100,
        help="random seed",
    )
    parser.add_argument(
        "--times",
        type=int,
        default=1,
        help="number of times to run the game",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="map file",
    )
    parser.add_argument(
        "--wumpus",
        type=int,
        help="number of wumpus",
    )
    parser.add_argument(
        "--pit",
        type=int,
        help="number of pit",
    )
    parser.add_argument(
        "--gold",
        type=int,
        help="number of gold",
    )
    parser.add_argument(
        "--ax",
        type=int,
        help="initial agent x position",
    )
    parser.add_argument(
        "--ay",
        type=int,
        help="initial agent y position",
    )
    parser.add_argument(
        "--width",
        type=int,
        help="map width",
    )
    parser.add_argument(
        "--height",
        type=int,
        help="map height",
    )
    args = parser.parse_args()
    return args


def extract_args(args):
    # extract arguments
    seed = args.seed
    times = args.times
    file = args.file
    wumpus_count = args.wumpus
    pit_count = args.pit
    gold_count = args.gold
    initial_agent_pos = None
    if args.ax is not None and args.ay is not None:
        initial_agent_pos = DownwardCoord(args.ax, args.ay)
    else:
        initial_agent_pos = None
    if args.width is not None and args.height is not None:
        map_size = (args.width, args.height)
    else:
        map_size = None
    MapConfig = namedtuple(
        "MapConfig",
        [
            "seed",
            "times",
            "file",
            "wumpus_count",
            "pit_count",
            "gold_count",
            "map_size",
            "initial_agent_pos",
        ],
    )
    return MapConfig(
        seed,
        times,
        file,
        wumpus_count,
        pit_count,
        gold_count,
        map_size,
        initial_agent_pos,
    )


if __name__ == "__main__":
    args = parse_args()
    config = extract_args(args)
    print(config)
    result = summary(
        seed=config.seed,
        times=config.times,
        file=config.file,
        wumpus_count=config.wumpus_count,
        pit_count=config.pit_count,
        gold_count=config.gold_count,
        map_size=config.map_size,
        initial_agent_pos=config.initial_agent_pos,
    )
