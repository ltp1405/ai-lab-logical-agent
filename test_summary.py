from lib.game.game import summary
from rich import print

if __name__ == "__main__":
    print(summary(file="tests/map1.txt", times=300))
