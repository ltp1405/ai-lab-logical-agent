from lib.coord import DownwardCoord
from lib.game.game import summary
from rich import print

if __name__ == "__main__":
    times = 100
    result = summary(
        seed=502,
        times=times,
        # seed=500,
        file="tests/map6.txt",
        initial_agent_pos=DownwardCoord(0, 0),
        # wumpus_count=0,
        # pit_count=5,
        # gold_count=4,
    )
