from lib.game.game import summary
from rich import print

if __name__ == "__main__":
    times = 30
    result = summary(times=times)
    winning_percentage = 0.0
    for r in result:
        if result[r][0] == "WON":
            winning_percentage += 1 / times if result[r][1] > 0 else 0
    print(f"Winning percentage: {winning_percentage}")
    print (result)
