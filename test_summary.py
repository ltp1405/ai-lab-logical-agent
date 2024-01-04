from lib.game.game import summary
from rich import print

if __name__ == "__main__":
    times = 100
    result = summary(
        times=times,
        # seed=500,
        file="tests/map6.txt",
        # initial_agent_pos=(2, 3),
        # wumpus_count=0,
        # pit_count=5,
        # gold_count=4,
    )
