import pygame
from lib.game.board import Action, Board, Direction
from lib.game.board_data import BoardData, read_board_data

if __name__ == "__main__":
    pygame.init()
    board_data = read_board_data("tests/map1.txt")
    board = Board(board_data, 500, 500, 32)
    screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 32)
    text = ""
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
        screen.fill((255, 255, 255))
        text_rect = font.render(f"Percepts: {text}", True, (0, 0, 0))
        screen.blit(text_rect, (0, 0))
        board.draw(screen)
        pygame.display.update()
    print(board_data)
