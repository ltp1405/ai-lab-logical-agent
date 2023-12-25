from typing import Dict, Tuple
from lib.game.board_data import BoardData
from lib.game.board_model import BoardModel, Position
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
        print(self.mapped_known_tiles())

    def virtual_agent_position(self):
        """
        Agent position relative to the initial position
        """
        return Position(
            x=self._agent.x - self.initial_agent_pos.x,
            y=self._agent.y - self.initial_agent_pos.y,
        )

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
        print(self.mapped_known_tiles())
        return self.current_percepts

    def get_known_tiles(self) -> Dict[Tuple[int, int], Cell]:
        """
        Known tiles in perspective of the agent (relative to the initial position)
        """
        return self.known_tiles

    def mapped_known_tiles(self):
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