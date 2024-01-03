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
from typing import Dict, Tuple

TILE_SIZE = 64


def run(
    map_path: str | None = None,
    seed: int | None = 500,
) -> Tuple[str, int]:
    pygame.init()
    map = generate_map(seed=seed)
    print(map)
    board_data = map.board_data
    if map_path is not None:
        board_data = read_board_data(map_path)
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
    board = Board(board_model, board_x, board_y, TILE_SIZE)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 32)
    text = board.model.current_percepts
    try:
        while running:
            dt = clock.tick(60) / 1000
            text, new_visited = simulation(agent, visited_rooms)
            board.update(dt)
            visited_rooms = new_visited
            if board_model.game_over == GameState.WON or board_model.game_over == GameState.LOST:
                running = False
            screen.fill((0, 0, 0))
            board.draw(screen)
            text_rect = font.render(f"{text}", True, (255, 255, 255))
            screen.blit(text_rect, (0, 0))
            pygame.display.update()
            print(f"All safe rooms length: {len(set(agent.safe_rooms(find_all=True)))}")
    except Exception as e:
        board_model.game_over = GameState.LOST
    print(board_data)
    print(f"Agent visited {len(visited_rooms)} rooms")
    game_result = "WON" if agent.board.game_over == GameState.WON else "LOST"
    print(f"Game result: {game_result}")
    print(f"Agent picks {agent.golds} golds")
    return (game_result, board_model.points)


def summary(
    times: int = 10,
    seed: int = 500,
    file: str | None = None,
) -> Dict[int, Tuple[str, int]]:
    """Run the simulation multiple times and return the summary of the results.

    Args:
        times (int, optional): Number of times to run the simulation. Defaults to 10.
        seed (int, optional): Seed to set for the map generator. Defaults to 500.

    Returns:
        Dict[int, Tuple[str, int]]: Summary of the results.
    """
    result: Dict[int, Tuple[str, int]] = {}
    for i in range(times):
        game_result = run(
            seed=seed,
            map_path=file,
        )
        result[i + 1] = game_result
    return result
