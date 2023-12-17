import pygame
from lib.game.board import Action, Board, Direction
from lib.game.board_data import BoardData, read_board_data

TILE_SIZE = 64

if __name__ == "__main__":
    pygame.init()
    board_data = read_board_data("tests/map2.txt")
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    s_width, s_height = screen.get_size()
    middle = s_width // 2, s_height // 2
    board_x, board_y = (
        middle[0] - board_data.initial_agent_pos[0] * TILE_SIZE,
        middle[1] - board_data.initial_agent_pos[1] * TILE_SIZE,
    )
    board = Board(board_data, board_x, board_y, TILE_SIZE)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 32)
    text = board.current_percepts
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
                        board.change_agent_direction(Direction.UP)
                    else:
                        board.change_agent_direction(Direction.UP)
                        text = board.act(Action.MOVE)
                elif event.key == pygame.K_DOWN:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board.change_agent_direction(Direction.DOWN)
                    else:
                        board.change_agent_direction(Direction.DOWN)
                        text = board.act(Action.MOVE)
                elif event.key == pygame.K_LEFT:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board.change_agent_direction(Direction.LEFT)
                    else:
                        board.change_agent_direction(Direction.LEFT)
                        text = board.act(Action.MOVE)
                elif event.key == pygame.K_RIGHT:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        board.change_agent_direction(Direction.RIGHT)
                    else:
                        board.change_agent_direction(Direction.RIGHT)
                        text = board.act(Action.MOVE)
                elif event.key == pygame.K_SPACE:
                    board.act(Action.MOVE)
                elif event.key == pygame.K_RETURN:
                    board.act(Action.SHOOT)
                elif event.key == pygame.K_r:
                    board.act(Action.CLIMB)
        board.update(dt)
        if board.game_over:
            running = False
        screen.fill((0, 0, 0))
        board.draw(screen)
        text_rect = font.render(f"{text}", True, (255, 255, 255))
        screen.blit(text_rect, (0, 0))
        pygame.display.update()
    print(board_data)
