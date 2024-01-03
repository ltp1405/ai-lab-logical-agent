from copy import deepcopy
from enum import Enum
import random
from typing import Callable, List, Optional, Set, Tuple
from lib.agent.agent import Agent, AgentState, Decision
from lib.game.board_model import Action, Direction
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import CellValue

from lib.knowledge_base.knowledge_base import KnowledgeBase

from rich import print

from lib.percepts import Percepts


### PLANNING PHASE ###
# Step 1: Get the safe rooms, wumpus rooms, pit rooms
# Step 2: If the agent is in the exit room, then
#   the agent should take the action CLIMB to (left, bottom)
# Step 3: Initialize prioritzed_direction: Set[Direction] = {Direction.RIGHT, Direction.UP}
# Step 4: Do the following guidelines:
#   - If all safe rooms are visited, then go to step 5 (All safe rooms are visited if len(all_safe_rooms) == len(visited_rooms))
#   - If there is no safe room adjacent to the agent, then:
#       - The agent now should decide to either move back to the previous room or go to step 5
#       ** If the agent decides to move back to the previous room**
#       - Calling backtrack() to remove, then receive the result of the function call
#       - If the result is None, then the agent is in the initial room, then go to step 5
#         Else:
#            - Get the last room in the stack
#            - Add the current room to the visited_rooms
#            - Take_action MOVE to that the previous room, then go to step 6
#   - Else:
#       - Select a safe room which is not visited yet, then take_action MOVE to that room
# Step 5:
#   - If there are some rooms that may contain wumpus, then:
#       - Either select a room that has a wumpus or randomly choose a room
#         that may contain wumpus, then take_action SHOOT to that room, then go to step 6
#   - If there are some rooms that may contain pit, then:
#       - Randomly choose a room, then take_action MOVE to that room, then go to step 6
#   - If the agent is trying to find the gold, then:
#       - Decide to backtrack to the previous room or go to step 6
# Step 6: Add the rooms that the agent has visited to the list visited_rooms,
#         then return the tuple (percepts, visited_rooms), where percepts is the percepts
#         of the action that the agent has taken
### END OF PLANNING PHASE ###

### EXECUTION PHASE ###


def simulation(
    agent: Agent,
    visited_rooms: Set[Tuple[int, int]],
) -> Tuple[Percepts, Set[Tuple[int, int]]]:
    print("=====================================")
    # Step 1
    c_visited_rooms = deepcopy(visited_rooms)
    safe_rooms = agent.safe_rooms()
    percepts = agent.board.current_percepts
    # Step 2
    if agent.state == AgentState.TRY_TO_EXIT:
        try:  # Try to climb out of the cave
            room = agent.latest_room()
            if room is not None:
                percepts = agent.take_action(Action.CLIMB, (room[0], room[1]))
                print(
                    f"Agent is trying to climb out of the cave. Take action CLIMB to {room}"
                )
                return (percepts, c_visited_rooms)
        except Exception as e:
            print(f"Cannot climb out of the cave")
    # Step 4
    all_safe_rooms = agent.safe_rooms(find_all=True)
    print(f"Agent stack: {agent.stack}")
    print(f"Safe rooms has {len(safe_rooms)} rooms: {safe_rooms}")
    print(f"All safe rooms has {len(set(all_safe_rooms))} rooms")
    print(f"Visited rooms has {len(c_visited_rooms)} rooms: {c_visited_rooms}")
    if (
        set(all_safe_rooms).issubset(c_visited_rooms)
        and agent.state != AgentState.TRY_TO_EXIT
    ):
        print("All safe rooms are visited")
        return _restart_to_exit(agent, c_visited_rooms)
    else:
        print("Checkpoint 1")
        room = _select_room(
            agent,
            visited_rooms,
            safe_rooms,
        )
        if room is None:
            print("Checkpoint 2")
            result = _agent_make_desicion(
                agent,
                c_visited_rooms=c_visited_rooms,
            )
            percepts, new_visited_rooms = result
            print(f"Result: {result}")
            c_visited_rooms = new_visited_rooms
        else:
            print("Checkpoint 3")
            percepts = agent.take_action(Action.MOVE, room)
            if percepts["glitter"]:
                print(f"FIND GOLD at room: {room}")
            if not percepts["bump"]:
                c_visited_rooms.add(room)
                print(f"Move to room: {room}")
            else:
                agent.backtrack()  # Remove the wall from the stack
                print(f"Bumped into the wall at {room}")
    print(f"Visited rooms: {c_visited_rooms}")
    return (percepts, c_visited_rooms)


def _select_room(
    agent: Agent,
    visited_rooms: Set[Tuple[int, int]],
    safe_rooms: List[Tuple[int, int]],
) -> Tuple[int, int] | None:
    """Select a room that is not visited yet, and is safe to move to
    If there is no room that is not visited yet, then return None

    Args:
        agent (Agent): Agent
        visited_rooms (Set[Tuple[int, int]]): Visited rooms
        safe_rooms (List[Tuple[int, int]]): Safe rooms
        deprioritized_direction (Set[Direction]): Deprioritized direction, avoid selecting a room
            that is in this direction

    Returns:
        Tuple[int, int] | None: None if there is no room that is not visited yet
    """
    not_visited_rooms = [room for room in safe_rooms if room not in visited_rooms]
    if not not_visited_rooms:
        return None
    print(f"Not visited rooms: {not_visited_rooms}")
    room = agent.random_select_room(not_visited_rooms)
    return room


def _agent_make_desicion(
    agent: Agent,
    c_visited_rooms: Set[Tuple[int, int]],
) -> Tuple[Percepts, Set[Tuple[int, int]]]:
    """Agent makes a decision sequentially:
    1. Looking for the wumpus and shoot the arrow
    2. Decide to backtrack to the previous room or go to step 3
    3. The agent must decide to either restart at the current room or move to the room that may contain pit

    Args:
        agent (Agent): Agent
        visited_rooms (Optional[Set[Tuple[int, int]]], optional): Visited rooms.

    Returns:
        Percepts: Percepts of the function call agent.take_action
    """
    # Step 1:
    if (
        percepts := _find_wumpus_and_shoot_arrow(
            agent,
        )
    ) is not None:
        return (percepts, c_visited_rooms)
    if (percepts := _move_back_to_previous_room(agent, c_visited_rooms)) is not None:
        return percepts
    if (
        agent.state == AgentState.TRY_TO_EXIT
        and (percepts := _go_to_undecidable_pit(agent, c_visited_rooms)) is not None
        and len(agent.safe_rooms()) == 0
    ):
        return percepts
    return _restart_to_exit(agent, c_visited_rooms)


def _go_to_undecidable_pit(
    agent: Agent,
    c_visited_rooms: Set[Tuple[int, int]],
) -> Percepts | None:
    """Go to a room that may contain pit

    Args:
        agent (Agent): Agent

    Returns:
        Percepts | None: Percepts of the function call agent.take_action if there is a room
    """
    rooms: List[Tuple[int, int]] = agent.pit_rooms(target=CellValue.MAYBE)
    if len(rooms) == 0:
        return None
    choice = agent.random_select_room(rooms)
    print(f"Move to room that may contain pit: {choice}")
    percepts = agent.take_action(Action.MOVE, choice)
    print(f"Percepts: {percepts}")
    if not percepts["bump"]:
        c_visited_rooms.add(choice)
    else:
        print(f"Bump into the wall at room {choice}")
    return (percepts, c_visited_rooms)


def _find_wumpus_and_shoot_arrow(
    agent: Agent,
) -> Percepts | None:
    """Find the wumpus and shoot the arrow
    Finding all the rooms that contain wumpus. If empty, then randomly choose a room
    that may contain wumpus.
    Finally, shoot the arrow to that room, then return the percepts of the action

    Args:
        agent (Agent): Agent
    Returns:
        Percepts | None: Percepts of the function call agent.take_action if there is a room
    """
    rooms: List[Tuple[int, int]] = agent.wumpus_rooms(target=CellValue.TRUE)
    pit_rooms: List[Tuple[int, int]] = agent.pit_rooms(target=CellValue.MAYBE)
    if len(rooms) == 0:
        # If there is no room that has a wumpus, then randomly choose a room
        # that may contain wumpus
        rooms = agent.wumpus_rooms(target=CellValue.MAYBE)
    rooms = [room for room in rooms if room not in pit_rooms]
    if len(rooms) == 0:
        return None
    choice = agent.random_select_room(rooms)
    print(f"Shoot arrow to room: {choice}")
    percepts = agent.take_action(Action.SHOOT, choice)
    if not percepts["scream"]:
        print("Shoot arrow but no scream perceived")
    return percepts


def _move_back_to_previous_room(
    agent: Agent, c_visited_rooms: Set[Tuple[int, int]]
) -> Tuple[Percepts, Set[Tuple[int, int]]] | None:
    """Move back to the previous room

    Args:
        agent (Agent): Agent
        c_visited_rooms (Set[Tuple[int, int]]): Visited rooms

    Returns:
        Percepts | None: Percepts of the function call agent.take_action if there is a room
    """
    last_room = agent.backtrack()
    if last_room is None:
        return None
    c_visited_rooms.add(agent.latest_room())
    print(f"Move back to room: {last_room}")
    percepts = agent.take_action(Action.MOVE, last_room)
    return (percepts, c_visited_rooms)


def _restart_to_exit(
    agent: Agent, visited_rooms: Set[Tuple[int, int]]
) -> Tuple[Percepts, Set[Tuple[int, int]]]:
    print(f"Start to exit at the current room: {agent.latest_room()}")
    current_room = agent.latest_room()
    agent.stack.clear()
    agent.stack.append(current_room)
    agent.state = AgentState.TRY_TO_EXIT
    return (agent.board.current_percepts, {current_room})


# def _decide_to_exit(
#     agent: Agent, visited_rooms: Set[Tuple[int, int]]
# ) -> Tuple[Percepts, Set[Tuple[int, int]]]:
#     c_visited_rooms = deepcopy(visited_rooms)
#     safe_rooms = agent.safe_rooms()
#     agent.set_exit(True)
#     c_visited_rooms.clear()
#     current_room = agent.latest_room()
#     agent.stack.clear()
#     if len(safe_rooms) > 0:
#         agent.stack.append(current_room)
#     c_visited_rooms.add(current_room)
#     print(f"Agent decides to exit. Start exiting phase at cell {current_room}")
#     return (agent.board.current_percepts, c_visited_rooms)
