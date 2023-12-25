from lib.game.board import Board
from lib.game.board_data import BoardData
from lib.game.board_model import BoardModel
from lib.knowledge_base.knowledge_base import KnowledgeBase
from rich import print


class BoardModelWithKB(BoardModel):
    def __init__(self, board_data: BoardData, kb: KnowledgeBase):
        super().__init__(board_data)
        self.kb = kb
        print(self.virtual_agent_position())
        print(
            self.kb.tell(
                self.virtual_agent_position()[1],
                self.virtual_agent_position()[0],
                self.current_percepts,
                None,
            )
        )

    def virtual_agent_position(self):
        """
        Agent position relative to the initial position
        """
        return (
            self.agent[1] - self.initial_agent_pos[1],
            self.agent[0] - self.initial_agent_pos[0],
        )

    def act(self, action):
        """
        Act in the board
        """
        agent_direction = self.agent_direction
        percepts = super().act(action)
        virtual_agent_pos = self.virtual_agent_position()
        v_x, v_y = virtual_agent_pos
        print(self.virtual_agent_position())
        print(self.kb.tell(v_x, v_y, percepts, action=(action, agent_direction)))
        return self.current_percepts

    def actual_agent_position(self):
        """
        Agent position in the board
        """
        return self.agent
