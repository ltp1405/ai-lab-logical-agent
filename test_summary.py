from lib.coord import DownwardCoord
from lib.game.game import summary

if __name__ == "__main__":
    times = 10
    result = summary(
        seed=52356,
        times=times,
        # seed=500,
        # file="tests/map6.txt",
        # initial_agent_pos=DownwardCoord(0, 0),
        wumpus_count=12,
        pit_count=12,
        gold_count=12,
    )
