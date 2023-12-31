from copy import deepcopy
from enum import Enum
from lib.agent.agent import Agent
from lib.game.board_model import Action
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import CellValue

from lib.knowledge_base.knowledge_base import KnowledgeBase

from rich import print

class GameResult(Enum):
    WIN = 1
    LOSE = 2


def simulation(
        board: BoardModelWithKB,
    ) -> GameResult:
    agent = Agent(board=board)
    stack = [(0, 0)]
    visited = {(0, 0)}
    is_alive = agent.is_alive()

    while is_alive:
        adjacent_rooms = agent.find_adjacent_rooms()
        print(f"Adjacent rooms: {adjacent_rooms}")
        allowed_to_go = False
        has_updated_bound = False

        if not agent.has_found_gold():
            for room in adjacent_rooms:
                if room not in visited:
                    inspect = agent.inspect(room)
                    if inspect:
                        print(f"Room: {room} is inspected, safe")
                        allowed_to_go = True
                        percept = agent.take_action(Action.MOVE, room)
                        if percept["bump"]:
                            print(f"Agent bumps into a wall {room}")
                            has_updated_bound = True
                            break
                        stack.append(room)
                        visited.add(room)
                        print (f"Agent knowledge base:", agent.my_world())
                        break
                    infer_wumpus = (room[0], room[1], "is_wumpus", CellValue.FALSE)
                    infer_pit = (room[0], room[1], "is_pit", CellValue.FALSE)
                    
                    res_wumpus = agent.infer(alpha=infer_wumpus)
                    res_pit = agent.infer(alpha=infer_pit)
                    
                    if not res_wumpus:
                        print(f"Agent cannot infer that there is no wumpus at {room}")
                    if not res_pit:
                        print(f"Agent cannot infer that there is no pit at {room}")
                    if res_wumpus and res_pit:
                        print(f"Room: {room} is inferred, not wumpus and not pit")
                        allowed_to_go = True
                        percept = agent.take_action(Action.MOVE, room)
                        if percept["bump"]:
                            print(f"Agent bumps into a wall {room}")
                            has_updated_bound = True
                            break
                        stack.append(room)
                        visited.add(room)
                        print (f"Agent knowledge base:", agent.my_world())
                        break
                        

            if allowed_to_go and has_updated_bound:
                print("Updating bound, restart")
            if not allowed_to_go:
                # Backtrack
                print("Backtracking")
                stack.pop()
                if len(stack) == 0:
                    print("No way out")
                    break
                else:
                    print(f"Move to room: {stack[-1]}")
                    percept = agent.take_action(Action.MOVE, stack[-1])
        else:
            # Proritize climbing out over finding gold
            pass

    if agent.has_found_gold() and agent.is_alive():
        return GameResult.WIN
    return GameResult.LOSE