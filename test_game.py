import pygame
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
    board_data = read_board_data("tests/map2.txt")
    map = generate_map(seed=539)
    print(map)
    board_data = map.board_data
    screen = pygame.display.set_mode()
    s_width, s_height = screen.get_size()
    middle = s_width // 2, s_height // 2
    board_x, board_y = (
        middle[0] - board_data.initial_agent_pos[0] * TILE_SIZE,
        middle[1] - board_data.initial_agent_pos[1] * TILE_SIZE,
    )
    kb = KnowledgeBase()
    board_model = BoardModelWithKB(board_data, kb)
    board = Board(board_model, board_x, board_y, TILE_SIZE)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 32)
    text = board.model.current_percepts
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board_model.change_agent_direction(Direction.UP)
                    else:
                        board_model.change_agent_direction(Direction.UP)
                        text = board_model.act(Action.MOVE)
                elif event.key == pygame.K_DOWN:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board_model.change_agent_direction(Direction.DOWN)
                    else:
                        board_model.change_agent_direction(Direction.DOWN)
                        text = board_model.act(Action.MOVE)
                elif event.key == pygame.K_LEFT:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board_model.change_agent_direction(Direction.LEFT)
                    else:
                        board_model.change_agent_direction(Direction.LEFT)
                        text = board_model.act(Action.MOVE)
                elif event.key == pygame.K_RIGHT:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board_model.change_agent_direction(Direction.RIGHT)
                    else:
                        board_model.change_agent_direction(Direction.RIGHT)
                        text = board_model.act(Action.MOVE)
                elif event.key == pygame.K_SPACE:
                    board_model.act(Action.MOVE)
                elif event.key == pygame.K_RETURN:
                    board_model.act(Action.SHOOT)
                elif event.key == pygame.K_r:
                    board_model.act(Action.CLIMB)
        board.update(dt)
        if board_model.game_over:
            running = False
        screen.fill((0, 0, 0))
        board.draw(screen)
        text_rect = font.render(f"{text}", True, (255, 255, 255))
        screen.blit(text_rect, (0, 0))
        pygame.display.update()
    print(board_data)
