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
                print(self.conversation_hist)
            message = agent.act(self.conversation_hist)
            message = split_response(message, ["COMMUNICATE", "THOUGHTS", "BOT_COMMAND"])

            print(message)
            self.conversation_hist.append(ell.user([f'{agent.name}:', message]))

    # def init_pos(self, Lis) -> None:
        # for agent in self.agents:
        #     agent.pos = agent.random_init_pos()
        # pass