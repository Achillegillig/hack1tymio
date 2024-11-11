import json
import requests
from openai import Client, OpenAI

from typing import List
import ell
from ell import Message

MODEL = "llama3.2:1b"
ell.init(store="./logdir")

client = OpenAI(
	base_url = "http://localhost:11434/v1",
	api_key = "ollama",
)
ell.config.register_model(MODEL, client)


class Agent:
    def __init__(self, role) -> None:
        self.role = role

    
@ell.simple(model=MODEL, temperature=0.3)
def act(thymio_id: str, conversation_history: List[Message]) -> List[Message]:
    """
    You are controlling a tymio bot. Take control of the robot,
    taking into account inputs from the other bots.
    """
    return [
        ell.user(f"What is your next move?"),
    ] + conversation_history

# TODO Past a certain context length, summarize
class Assembly:
    def __init__(self, model=MODEL) -> None:
        self.agents = []
        self.model = model
        self.conversation_hist = []

    def launch_round(self):
        for agent in self.agents:
            print(agent.role)
            message = act(agent.role, self.conversation_hist)
            print(message)
            self.conversation_hist.append(ell.user(message))
            print()

if __name__ == "__main__":
    assembly = Assembly()
    for i in range(3):
        agent = Agent(f"tymio_{i}")
        assembly.agents.append(agent)

    assembly.launch_round()
    assembly.launch_round()
    print(assembly.conversation_hist)

