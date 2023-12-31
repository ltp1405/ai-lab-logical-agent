from lib.agent.agent import Agent
from lib.game.board_data import read_board_data
from lib.game.board_model import Action, Direction
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import CellValue
from lib.knowledge_base.knowledge_base import KnowledgeBase
from rich import print


def move(agent: Agent, direction: Direction):
    print(f"Moving {direction}")
    agent.take_action(Action.MOVE, direction)


def infer_then_move(agent: Agent, direction: Direction, alpha: tuple):
    if not agent.infer(alpha=alpha):
        move(agent, direction)
    else:
        print(f"Agent infers that there is no pit {alpha}")


if __name__ == "__main__":
    board_data = read_board_data("tests/map1.txt")
    board = BoardModelWithKB(board_data, KnowledgeBase())
    agent = Agent(board=board)
    # move(agent, (0, -1))
    stack = [(0, 0)]
    visited = {(0, 0)}
    print (agent.is_alive())
    is_alive = agent.is_alive()

