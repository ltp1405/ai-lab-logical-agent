from lib.agent.algorithms import simulation
from lib.game.board_data import read_board_data
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.knowledge_base import KnowledgeBase

from rich import print


if __name__ == "__main__":
    board_data = read_board_data("tests/map1.txt")
    board = BoardModelWithKB(board_data, KnowledgeBase())
    result = simulation(board)
    
    print (result)