from typing import Dict, Tuple
from lib.game.board_data import BoardData
from lib.game.board_model import BoardModel, Direction, Position
from lib.knowledge_base.cell import Cell
from lib.knowledge_base.knowledge_base import KnowledgeBase
from rich import print


class BoardModelWithKB(BoardModel):
    def __init__(self, board_data: BoardData, kb: KnowledgeBase):
        super().__init__(board_data)
        self.kb = kb
        self.known_tiles: Dict[Tuple[int, int], Cell] = dict()
        self.known_tiles.update(
            self.kb.tell(
                self.virtual_agent_position().x,
                self.virtual_agent_position().y,
                self.current_percepts,
                None,
            )
        )

    def known_bounds(self):
        """
        Known bounds of the board
        """
        return (
            self.kb.top,
            self.kb.bottom,
            self.kb.left,
            self.kb.right,
        )

    def virtual_agent_position(self):
        """
        Agent position relative to the initial position
        """
        return Position(
            x=self._agent.x - self.initial_agent_pos.x,
            y=self._agent.y - self.initial_agent_pos.y,
        )
        
    def adjacent_rooms(self):
        """
        Adjacent rooms of the agent
        """
        x, y = self.virtual_agent_position().x, self.virtual_agent_position().y
        return [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]
        
    def identify_direction_to_modify(self, to_room: Tuple[int, int]) -> Direction:
        x, y = self.virtual_agent_position().x, self.virtual_agent_position().y
        if to_room == (x + 1, y):
            return Direction.RIGHT
        elif to_room == (x - 1, y):
            return Direction.LEFT
        elif to_room == (x, y + 1):
            return Direction.UP
        elif to_room == (x, y - 1):
            return Direction.DOWN
        else:
            raise ValueError("Invalid room")
        
    def act(self, action):
        """
        Act in the board
        """
        agent_direction = self.agent_direction
        percepts = super().act(action)
        virtual_agent_pos = self.virtual_agent_position()
        v_x, v_y = virtual_agent_pos.x, virtual_agent_pos.y
        self.known_tiles.update(
            self.kb.tell(v_x, v_y, percepts, action=(action, agent_direction))
        )
        # print (f"Points: {super().points}")
        # print(self.known_tiles)
        print(percepts)
        return percepts

    def get_known_tiles(self) -> Dict[Tuple[int, int], Cell]:
        """
        Known tiles in perspective of the agent (relative to the initial position)
        """
        return self.known_tiles

    def model_known_tiles(self):
        """
        Known tiles in perspective of the board
        """
        known_tiles = dict()
        for pos, cell in self.known_tiles.items():
            pos = (
                pos[0] + self.initial_agent_pos.x,
                pos[1] + self.initial_agent_pos.y,
            )
            known_tiles[pos] = cell
        return known_tiles

    def mapped_known_tiles(self):
        """
        Top-left corner is (0, 0), used to draw the board
        """
        mapped_tiles = dict()
        for pos, cell in self.known_tiles.items():
            pos = (
                pos[0] + self.initial_agent_pos.x,
                self.height - 1 - (pos[1] + self.initial_agent_pos.y),
            )
            mapped_tiles[pos] = cell
        return mapped_tiles

    def actual_agent_position(self):
        """
        Agent position in the board
        """
        return self._agent
