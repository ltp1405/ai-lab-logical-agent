import pygame
from lib.agent.agent import Agent, AgentState
from lib.agent.algorithms import simulation
from lib.game.board import Board, Direction
from lib.game.board_data import BoardData, read_board_data
from lib.game.board_model import Action, BoardModel, GameState
from lib.game.board_with_kb import BoardModelWithKB
from lib.game.map_generator import generate_map
from lib.knowledge_base.knowledge_base import KnowledgeBase
from rich import print
from rich.table import Table
from typing import Dict, Tuple

from test_map_generator import print_map_debug

TILE_SIZE = 64

# When the agent picks the same safe room for 10 times, it will take risk
# to find way to exit the cave, avoid being stuck in the cave forever
THRES_HOLD = 10 


def run(
    map_path: str | None = None,
    seed: int | None = 500,
    wumpus_count: int | None = None,
    pit_count: int | None = None,
    gold_count: int | None = None,
    initial_agent_pos: Tuple[int, int] | None = None,
) -> Tuple[str, int, int]:
    pygame.init()
    map = generate_map(
        seed=seed,
        wumpus_count=wumpus_count,
        pit_count=pit_count,
        gold_count=gold_count,
        initial_agent_position=initial_agent_pos,
    )
    board_data = map.board_data
    if map_path is not None:
        board_data = read_board_data(map_path)
    x, y = board_data.initial_agent_pos
    print_map_debug(board_data.board_data, (y, x))
    # assert False
    screen = pygame.display.set_mode()
    s_width, s_height = screen.get_size()
    middle = s_width // 2, s_height // 2
    board_x, board_y = (
        middle[0] - (board_data.initial_agent_pos[1] + 1) * TILE_SIZE,
        middle[1] - (board_data.initial_agent_pos[0] + 1) * TILE_SIZE,
    )
    kb = KnowledgeBase()
    board_model = BoardModelWithKB(board_data, kb)
    agent = Agent(board=board_model)
    visited_rooms = {(0, 0)}
    repeated = 0
    previous_all_safe_rooms = set()
    take_risk = False
    board = Board(board_model, board_x, board_y, TILE_SIZE)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 32)
    text = board.model.current_percepts
    try:
        while running:
            dt = clock.tick(60) / 1000
            text, new_visited = simulation(
                agent,
                visited_rooms,
                take_risk,
            )
            board.update(dt)
            visited_rooms = new_visited
            if (
                board_model.game_over == GameState.WON
                or board_model.game_over == GameState.LOST_WUMPUS
                or board_model.game_over == GameState.LOST_PIT
            ):
                running = False
            if agent.safe_rooms(find_all=True) == previous_all_safe_rooms:
                repeated += 1
                if repeated >= THRES_HOLD:
                    take_risk = True
            else:
                repeated = 0
                take_risk = False
                previous_all_safe_rooms = agent.safe_rooms(find_all=True)
            screen.fill((0, 0, 0))
            board.draw(screen)
            text_rect = font.render(f"{text}", True, (255, 255, 255))
            screen.blit(text_rect, (0, 0))
            pygame.display.update()
    except Exception as e:
        board_model.game_over = GameState.LOST_UNKNOWN
    print(board_data)
    game_result = (
        "WON"
        if agent.board.game_over == GameState.WON
        else "EATEN BY WUMPUS"
        if agent.board.game_over == GameState.LOST_WUMPUS
        else "FELL INTO PIT"
        if agent.board.game_over == GameState.LOST_PIT
        else "LOST BY UNKNOWN REASON"
    )
    print(f"Game result: {game_result}")
    print(f"Agent picks {agent.golds} golds")
    return (game_result, board_model.points, agent.golds)


def _print_summary_table(
    iteration: int,
    summary: Dict[int, Tuple[str, int, int]],
) -> None:
    table = Table(show_header=True, header_style="bold magenta")
    s_table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ITERATION")
    table.add_column("WIN PERCENTAGE")
    table.add_column("POINTS AVG")
    table.add_column("MAX POINTS")
    s_table.add_column("MIN POINTS")
    s_table.add_column("GOLD AVG")
    s_table.add_column("MAX GOLD")
    s_table.add_column("LOSE BY PIT (times)")
    # Calculate the summary
    win_count = 0
    gold_count = 0
    max_gold = 0
    lose_by_pit_count = 0
    points_sum = 0
    max_points = 0
    min_points = float("inf")
    for i in summary:
        if summary[i][0] == "WON":
            win_count += 1
        elif summary[i][0] == "FELL INTO PIT":
            lose_by_pit_count += 1
        gold_count += summary[i][2]
        points_sum += summary[i][1]
        max_points = max(max_points, summary[i][1])
        min_points = min(min_points, summary[i][1])
        max_gold = max(max_gold, summary[i][2])
    win_percentage = win_count / len(summary) * 100
    points_avg = points_sum / len(summary)
    gold_avg = gold_count / len(summary)

    table.add_row(
        f"{iteration}",
        f"{win_percentage:.2f}%",
        f"{points_avg:.2f}",
        f"{max_points}",
    )
    s_table.add_row(
        f"{min_points}",
        f"{gold_avg:.2f}",
        f"{max_gold}",
        f"{lose_by_pit_count}",
    )
    print(table)
    print(s_table)


def summary(
    times: int = 10,
    seed: int = 500,
    wumpus_count: int | None = None,
    pit_count: int | None = None,
    gold_count: int | None = None,
    initial_agent_pos: Tuple[int, int] | None = None,
    file: str | None = None,
) -> None:
    """Run the simulation multiple times and return the summary of the results.

    Args:
        times (int, optional): Number of times to run the simulation. Defaults to 10.
        seed (int, optional): Seed to set for the map generator. Defaults to 500.

    Returns:
        Dict[int, Tuple[str, int]]: Summary of the results.
    """
    result: Dict[int, Tuple[str, int, int]] = {}
    for i in range(times):
        game_result = run(
            seed=seed,
            map_path=file,
            wumpus_count=wumpus_count,
            pit_count=pit_count,
            gold_count=gold_count,
            initial_agent_pos=initial_agent_pos,
        )
        result[i + 1] = game_result
    _print_summary_table(times, result)
