import pygame
from lib.agent.agent import Agent
from lib.agent.algorithms import simulation
from lib.game.board import Board, Direction
from lib.game.board_data import BoardData, read_board_data
from lib.game.board_model import Action, BoardModel
from lib.game.board_with_kb import BoardModelWithKB
from lib.game.map_generator import generate_map
from lib.knowledge_base.knowledge_base import KnowledgeBase
from rich import print

TILE_SIZE = 64

if __name__ == "__main__":
    pygame.init()
    board_data = read_board_data("tests/map1.txt")
    # map = generate_map(seed=539)
    # print(map)
    # board_data = map.board_data
    screen = pygame.display.set_mode()
    s_width, s_height = screen.get_size()
    middle = s_width // 2, s_height // 2
    board_x, board_y = (
        middle[0] - (board_data.initial_agent_pos.x + 1) * TILE_SIZE,
        middle[1] - (board_data.initial_agent_pos.y + 1) * TILE_SIZE,
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
    while running:
        dt = clock.tick(60) / 1000
        text, new_visited = simulation(agent, visited_rooms)
        board.update(dt)
        visited_rooms = new_visited
        if board_model.game_over:
            running = False
        screen.fill((0, 0, 0))
        board.draw(screen)
        text_rect = font.render(f"{text}", True, (255, 255, 255))
        screen.blit(text_rect, (0, 0))
        pygame.display.update()
        print(f"All safe rooms length: {len(set(agent.safe_rooms(find_all=True)))}")
    print(board_data)
    print(f"Agent visited {len(visited_rooms)} rooms")
    game_result = "WON" if agent.exit else "LOST"
    print(f"Game result: {game_result}")
