from typing import List
import ell

from agent import Agent

from message_processing import split_response

class Assembly:
    def __init__(self) -> None:
        self.agents = []
        self.conversation_hist = []

    def launch_round(self):
        for i, agent in enumerate(self.agents):
            if i == 0:
                self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))
                
            message = agent.act(agent.name, self.conversation_hist)
            message = split_response(message, ["COMMUNICATE", "THOUGHTS", "BOT_COMMAND"])

            print(f'{agent.name}:', message.THOUGHTS)
            self.conversation_hist.append(ell.system)
            self.conversation_hist.append(ell.user([f'{agent.name}:', message]))

    def init_pos(self, List[Agent]) -> None:
        for agent in self.agents:
            agent.pos = agent.random_init_pos()