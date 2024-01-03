from lib.coord import DownwardCoord
from lib.game.game import summary
from rich import print

if __name__ == "__main__":
    times = 10
    result = summary(
        seed=502,
        times=times,
        initial_agent_pos=DownwardCoord(2, 3),
        wumpus_count=5,
        pit_count=5,
        gold_count=10,
    )
    winning_percentage = 0.0
    for r in result:
        if result[r][0] == "WON":
            winning_percentage += 1
    print(f"Winning percentage: {winning_percentage / times * 100}%")
    print(result)
