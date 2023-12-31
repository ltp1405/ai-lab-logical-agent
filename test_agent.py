from lib.agent.agent import Agent
from lib.game.board_data import read_board_data
from lib.game.board_model import Action, Direction
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import CellValue
from lib.knowledge_base.knowledge_base import KnowledgeBase
from rich import print


if __name__ == "__main__":
    board_data = read_board_data("tests/map1.txt")
    board = BoardModelWithKB(board_data, KnowledgeBase())
    agent = Agent(board=board)
    # move(agent, (0, -1))
    print ("Safe cells: ", agent.safe_rooms())
    print ("Wumpus cells: ", agent.wumpus_rooms())
    print ("Pit cells: ", agent.pit_rooms())
    
    agent.take_action(Action.MOVE, (1, 0))
    
    print ("Safe cells: ", agent.safe_rooms())
    print ("Wumpus cells: ", agent.wumpus_rooms())
    print ("Pit cells: ", agent.pit_rooms())
    
    agent.take_action(Action.MOVE, (0, 0))
    agent.take_action(Action.MOVE, (0, 1))
    
    print ("Safe cells: ", agent.safe_rooms())
    print ("Wumpus cells: ", agent.wumpus_rooms())
    print ("Pit cells: ", agent.pit_rooms())
    
    

