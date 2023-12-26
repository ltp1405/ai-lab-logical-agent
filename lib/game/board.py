from lib.game.board_model import BoardModel, Direction
import pygame

from lib.game.board_data import BoardData, TileType
from lib.game.board_with_kb import BoardModelWithKB
from lib.knowledge_base.cell import CellValue


class Board:
    def __init__(self, board_model: BoardModelWithKB, x: int, y: int, tile_size: int):
        self.model = board_model
        self.tile_size = tile_size
        self.x = x
        self.y = y
        self.height = self.model.height * self.tile_size
        self.width = self.model.width * self.tile_size
        self.board_surface = pygame.Surface((self.width, self.height))
        self.grid_color = (255, 255, 255)
        self.revealed = [
            [False for _ in range(self.model.width)] for _ in range(self.model.height)
        ]
        # y, x
        self.font = pygame.font.SysFont("Mono", 20)

    def draw(self, surface: pygame.Surface):
        self.board_surface.fill((255, 255, 255))
        self._draw_tiles()
        self._draw_kb()
        self._draw_agent()
        # self._draw_grid()
        # self._draw_border()
        surface.blit(self.board_surface, (self.x, self.y))

    def _draw_tiles(self):
        for y, row in enumerate(self.model.board):
            for x, _ in enumerate(row):
                if self.revealed[y][x]:
                    self._draw_tile(x, y)

    def _draw_kb_tile(self, x, y):
        font = self.font
        cell = self.model.mapped_known_tiles()[(x, y)]
        text = ""
        color = (255, 255, 255)
        if cell.is_safe:
            color = (0, 255, 0)
            text += "Safe"
        else:
            if cell.is_wumpus == CellValue.MAYBE:
                color = "#b76014"
                text += "W?"
            if cell.is_wumpus == CellValue.TRUE:
                color = (255, 0, 0)
                text += "W"
            if cell.is_pit == CellValue.MAYBE:
                color = "#b76014"
                text += "P?"
            if cell.is_pit == CellValue.TRUE:
                color = "#b76014"
                text += "P"
        pygame.draw.rect(
            self.board_surface,
            color,
            (
                x * self.tile_size,
                y * self.tile_size,
                self.tile_size,
                self.tile_size,
            ),
        )
        text_surface = font.render(text, True, (0, 0, 0))
        self.board_surface.blit(
            text_surface,
            (
                x * self.tile_size + self.tile_size / 2 - text_surface.get_width() / 2,
                y * self.tile_size + self.tile_size / 2 - text_surface.get_height() / 2,
            ),
        )

    def _draw_kb(self):
        for pos, _ in self.model.mapped_known_tiles().items():
            self._draw_kb_tile(*pos)

    def _draw_tile(self, x, y):
        font = self.font
        tile_type = self.model.board[y][x]
        if (y, x) == (self.model.height - 1, 0):
            color = (0, 255, 0)
            text = "D"
        elif tile_type == [TileType.WUMPUS]:
            color = (255, 0, 0)
            text = "W"
        elif tile_type == [TileType.PIT]:
            color = "#b76014"
            text = "P"
        elif tile_type == [TileType.GOLD]:
            color = (255, 255, 0)
            text = "G"
        elif tile_type == [TileType.BREEZE]:
            color = (0, 255, 255)
            text = "B"
        elif tile_type == [TileType.STENCH]:
            color = (255, 0, 255)
            text = "S"
        elif set(tile_type) == set([TileType.BREEZE, TileType.STENCH]):
            color = (255, 255, 255)
            text = "BS"
        elif set(tile_type) == set([TileType.BREEZE, TileType.GOLD]):
            color = (255, 255, 255)
            text = "BG"
        elif set(tile_type) == set([TileType.STENCH, TileType.GOLD]):
            color = (255, 255, 255)
            text = "SG"
        elif set(tile_type) == set([TileType.BREEZE, TileType.STENCH, TileType.GOLD]):
            color = (255, 255, 255)
            text = "BSG"
        else:
            color = (100, 100, 100)
            text = ""
        pygame.draw.rect(
            self.board_surface,
            color,
            (
                x * self.tile_size,
                y * self.tile_size,
                self.tile_size,
                self.tile_size,
            ),
        )
        text_surface = font.render(text, True, (0, 0, 0))
        self.board_surface.blit(
            text_surface,
            (
                x * self.tile_size + self.tile_size / 2 - text_surface.get_width() / 2,
                y * self.tile_size + self.tile_size / 2 - text_surface.get_height() / 2,
            ),
        )

    def _draw_agent(self):
        y, x = self.model.tl_agent_position().y, self.model.tl_agent_position().x
        pygame.draw.rect(
            self.board_surface,
            (0, 255, 0),
            (
                x * self.tile_size,
                y * self.tile_size,
                self.tile_size,
                self.tile_size,
            ),
        )
        match self.model.agent_direction:
            case Direction.UP:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size + self.tile_size / 4,
                        y * self.tile_size,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )
            case Direction.DOWN:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size + self.tile_size / 4,
                        y * self.tile_size + self.tile_size / 2,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )
            case Direction.LEFT:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size,
                        y * self.tile_size + self.tile_size / 4,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )
            case Direction.RIGHT:
                pygame.draw.rect(
                    self.board_surface,
                    (0, 0, 255),
                    (
                        x * self.tile_size + self.tile_size / 2,
                        y * self.tile_size + self.tile_size / 4,
                        self.tile_size / 2,
                        self.tile_size / 2,
                    ),
                )

    def _draw_border(self):
        pygame.draw.rect(
            self.board_surface, self.grid_color, (0, 0, self.width, self.height), 1
        )

    def _draw_grid(self):
        # draw vertical lines
        for x in range(0, self.width, self.tile_size):
            pygame.draw.line(
                self.board_surface, self.grid_color, (x, 0), (x, self.height)
            )

        # draw horizontal lines
        for y in range(0, self.height, self.tile_size):
            pygame.draw.line(
                self.board_surface, self.grid_color, (0, y), (self.width, y)
            )

    def update(self, dt):
        pass

    def handle_event(self, event):
        pass
