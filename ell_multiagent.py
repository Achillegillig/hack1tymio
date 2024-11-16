import json
import requests
from openai import Client, OpenAI

from typing import List
import ell
from ell import Message

from pydantic import BaseModel, Field

from agent import Agent

MODEL = "llama3.2:3b"
ell.init(store="./logdir")

client = OpenAI(
	base_url = "http://localhost:11434/v1",
	api_key = "ollama",
)
ell.config.register_model(MODEL, client)

class Agent:
    def __init__(self, name, role=None) -> None:
        self.name = name


@ell.complex(model=MODEL, temperature=0.3)
def act(agent: Agent, conversation_history: List[Message]) -> Message:
    sys_prompt = ell.system(f"""
    You are {agent.name}, a thymio bot. You have two thymio bot
    friends with you. Your goal is to get out of a maze. 
    The two other bots are nearby, ready to communicate.
    Given the conversation history, you must return
    your communication to the other bots, your thoughts on the situation and your mood on a scale from 0 to 10.

    Response format:

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
        self.conversation_hist = []

    def launch_round(self):
        for i, agent in enumerate(self.agents):
            if i == 0:
                self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))
                
            message = act(agent.name, self.conversation_hist)
            print(f'{agent.name}:', message.text)
            self.conversation_hist.append(ell.system())
            self.conversation_hist.append(ell.user([f'{agent.name}:', message]))
            # print()

if __name__ == "__main__":
    assembly = Assembly()
    for i in range(3):
        thymio_ids = ["thymiotée", "robob", "llamario"]
        agent = Agent(thymio_ids[i])
        assembly.agents.append(agent)

    assembly.launch_round()
    assembly.launch_round()
    print(assembly.conversation_hist)

