from copy import deepcopy
from enum import Enum
from typing import Callable, List, Optional, Set, Tuple
from lib.agent.agent import Agent, Decision
from lib.game.board_model import Action, Direction
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import CellValue

from lib.knowledge_base.knowledge_base import KnowledgeBase

from rich import print

from lib.percepts import Percepts


### PLANNING PHASE ###
# Step 1: Get the safe rooms, wumpus rooms, pit rooms
# Step 2: If the agent is trying to exit the room, then:
#   - Get the exit room
#   - If the agent is in the exit room, which is the bottom left room, then
#     the agent should take the action CLIMB to (left, bottom - 1)
#   - Else try to move to left until the agent bumps into the wall, then move
#     to bottom until the agent bumps into the wall
# Step 3: If the agent is trying to find the gold, then:
#   - If all safe rooms are visited, then go to step 4
#   - If there is no safe room adjacent to the agent, then:
#       - If all safe rooms are visited, then go to step 4
#       - Else:
#           - Pop the stack of the agent
#           - If the stack is empty, then go to step 4
#           - Else:
#               - Get the last room in the stack
#               - Add the current room to the visited_rooms
#               - Take_action MOVE to that room, then go to step 5
#   - Else:
#       - If there is no safe room that is not visited yet, then go to step 4
#       - Select a safe room which is not visited yet, then take_action MOVE to that room
# Step 4:
#   - If there are some rooms that may contain wumpus, then:
#       - Either select a room that has a wumpus or randomly choose a room
#     that may contain wumpus, then take_action SHOOT to that room, then go to step 5
#   - If there are some rooms that may contain pit, then:
#       - Randomly choose a room, then take_action MOVE to that room, then go to step 5
# Step 5: Add the rooms that the agent has visited to the list visited_rooms,
#         then return the tuple (percepts, visited_rooms)
### END OF PLANNING PHASE ###

### EXECUTION PHASE ###


def simulation(
    agent: Agent,
    visited_rooms: Set[Tuple[int, int]],
) -> Tuple[Percepts, Set[Tuple[int, int]]]:
    """Simulate the game, return the percepts of the action

    Args:
        agent (Agent): Agent

    Returns:
        Percepts: Percepts of the function call agent.take_action
    """
    print("=====================================")
    c_visited_rooms = deepcopy(visited_rooms)
    safe_rooms, wumpus_rooms, pit_rooms = (
        agent.safe_rooms(),
        agent.wumpus_rooms(),
        agent.pit_rooms(),
    )
    percepts = agent.board.current_percepts
    if agent.exiting():
        # Step 2
        print("On the exiting phase")
        if agent.latest_room() == agent.exit_room():
            # The agent is in the exit room
            print("Agent is in the exit room")
            percepts = agent.take_action(
                Action.CLIMB, (agent.exit_room()[0], agent.exit_room()[1] - 1)
            )
            print("Agent climbs out of the cave")
            agent.board.game_over = True
        else:
            room = _select_room(
                agent,
                c_visited_rooms,
                safe_rooms,
                deprioritized_direction={Direction.UP, Direction.RIGHT},
            )
            if room is None:
                # Decide to either move back to the previous room or kill the wumpus
                decision = _agent_make_desicion(
                    agent,
                    _either_move_or_shoot,
                    visited_rooms=c_visited_rooms,
                )
            else:
                percepts = agent.take_action(Action.MOVE, room)
                if not percepts["bump"]:
                    c_visited_rooms.add(room)
                    print(f"Move to room: {room}")
                else:
                    agent.backtrack()
        return (percepts, c_visited_rooms)
    all_safe_rooms = agent.safe_rooms(find_all=True)
    print(f"Agent stack: {agent.stack}")
    print(f"Safe rooms has {len(safe_rooms)} rooms: {safe_rooms}")
    print(f"Visited rooms has {len(c_visited_rooms)} rooms: {c_visited_rooms}")
    if len(all_safe_rooms) == len(c_visited_rooms):
        # Step 4, require decision making
        print("All safe rooms are visited")
        decision = _agent_make_desicion(agent, _find_wumpus_and_shoot_arrow)
        if decision is None:
            print("Agent decides to exit. Start exiting phase")
        else:
            percepts = decision
    else:
        # Step 3
        ## Moving back to the previous room
        room = _select_room(
            agent,
            visited_rooms,
            safe_rooms,
            deprioritized_direction={
                Direction.DOWN,
            },
        )
        if room is None:
            # Throw the dice to see if the agent should move back to the previous room
            # or kill the wumpus if exists
            decision = _agent_make_desicion(
                agent,
                _either_move_or_shoot,
                visited_rooms=c_visited_rooms,
            )
            if decision is None:
                print("Agent decides to exit. Start exiting phase")
                # Clear the visited rooms and backtrack stack
                c_visited_rooms.clear()
                current_room = agent.latest_room()
                agent.stack.clear()
                agent.stack.append(current_room)
        else:
            percepts = agent.take_action(Action.MOVE, room)
            if percepts["glitter"]:
                print(f"FIND GOLD at room: {room}")
            if not percepts["bump"]:
                c_visited_rooms.add(room)
                print(f"Move to room: {room}")
            else:
                agent.backtrack()  # Remove the wall from the stack
                print(f"Bumped into the wall at {room}")
    return (percepts, c_visited_rooms)


def _select_room(
    agent: Agent,
    visited_rooms: Set[Tuple[int, int]],
    safe_rooms: List[Tuple[int, int]],
    deprioritized_direction: Set[Direction],
) -> Tuple[int, int] | None:
    not_visited_rooms = list(filter(lambda x: x not in visited_rooms, safe_rooms))
    if len(not_visited_rooms) == 0:
        return None
    # Prioritize going UP, LEFT, RIGHT to DOWN
    print(f"Not visited rooms: {not_visited_rooms}")
    room = agent.random_select_room(not_visited_rooms)
    while (
        len(not_visited_rooms) > 1
        and agent.identify_direction(room) in deprioritized_direction
    ):
        room = agent.random_select_room(not_visited_rooms)
    return room


def _agent_make_desicion(
    agent: Agent,
    func: Callable[[Agent, Optional[Set[Tuple[int, int]]]], Percepts],
    visited_rooms: Optional[Set[Tuple[int, int]]] = None,
) -> Percepts | None:
    decision = agent.decide_game_state()
    match decision:
        case Decision.EXIT:
            return agent.set_exit(True)
        case Decision.CONTINUE:
            return func(agent) if visited_rooms is None else func(agent, visited_rooms)


def _find_wumpus_and_shoot_arrow(agent: Agent) -> Percepts:
    rooms: List[Tuple[int, int]] = agent.wumpus_rooms(target=CellValue.TRUE)
    choice = None
    if len(rooms) == 0:
        # If there is no room that has a wumpus, then randomly choose a room
        # that may contain wumpus
        rooms = agent.wumpus_rooms(target=CellValue.MAYBE)
        choice = agent.random_select_room(rooms)
    else:
        choice = agent.random_select_room(rooms)  # Select a room that has a wumpus
    return agent.take_action(Action.SHOOT, choice)


def _either_move_or_shoot(
    agent: Agent, c_visited_rooms: Set[Tuple[int, int]]
) -> Percepts:
    decision = agent.decide_action()  # Either move or shoot
    if decision == Action.MOVE:
        print("Agent decides to move back to the previous room")
        c_visited_rooms.add(agent.latest_room())
        last_room = agent.backtrack()
        if last_room is None:
            agent.board.game_over = True
            raise Exception("Agent stack is empty")
        else:
            percepts = agent.take_action(Action.MOVE, last_room)
            print(f"Move back to room: {last_room}")
    else:
        print("Agent decides to kill the wumpus")
        percepts = _find_wumpus_and_shoot_arrow(agent)
    return percepts
