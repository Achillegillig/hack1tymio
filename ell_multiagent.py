import json
import requests
from openai import Client, OpenAI

from typing import List
import ell
from ell import Message

from pydantic import BaseModel, Field

MODEL = "llama3.2:3b"
ell.init(store="./logdir")

client = OpenAI(
	base_url = "http://localhost:11434/v1",
	api_key = "ollama",
)
ell.config.register_model(MODEL, client)

class Agent:
    def __init__(self, role) -> None:
        self.role = role


@ell.complex(model=MODEL, temperature=0.3)
def act(thymio_id: str, conversation_history: List[Message]) -> Message:
    sys_prompt = ell.system(f"""
    You are {thymio_id}, a thymio bot. You have two thymio bot
    friends with you. Your goal is to get out of a maze.
    Given the conversation history, you must return
    your thoughts on the situation and your mood on a scale from 0 to 10
    write what you want to communicate to the other LLMs beginning by 
    COMMUNICATE: 
    THOUGHTS:
    BOT COMMAND: 
    """)
    return [sys_prompt] + conversation_history

# TODO Past a certain context length, summarize
class Assembly:
    def __init__(self, model=MODEL) -> None:
        self.agents = []
        self.model = model
        self.conversation_hist = [
            ell.user("Fellow bots, we arrived at an intersection! Should we go left or right?")
        ]

    def launch_round(self):
        for i, agent in enumerate(self.agents):
            if i == 0:
                self.conversation_hist.append(ell.user(f"{agent.role}, you are the first to communicate!"))
                
            print(agent.role)
            message = act(agent.role, self.conversation_hist)
            print(message.text)
            self.conversation_hist.append(ell.user([f'{agent.role}:', message]))
            print()

if __name__ == "__main__":
    assembly = Assembly()
    for i in range(3):
        agent = Agent(f"tymio_{i}")
        assembly.agents.append(agent)

    assembly.launch_round()
    assembly.launch_round()
    print(assembly.conversation_hist)

