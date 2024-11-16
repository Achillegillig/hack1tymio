import json
import requests
from openai import Client, OpenAI
import numpy as np
from typing import List
import ell
from ell import Message

from pydantic import BaseModel, Field

MODEL = "llama3.2:3b"

class Agent:
    def __init__(self, id, name, role=None) -> None:
        self.role = role
        self.name = name
        self.id = id
        self.pos = self.init_pos()
        self.conversation_history = []
        self.MODEL = "llama3.2:3b"

    @ell.complex(model=self.MODEL, temperature=0.3)
    def act(self, conversation_history: List[Message]) -> Message:
        sys_prompt = ell.system(f"""
        You are {self.name}, a thymio bot who is {self.role}. You have two thymio bot
        friends with you. Your goal is to get out of a maze.
        Given the conversation history, you must return
        your thoughts on the situation and your mood on a scale from 0 to 10
        write what you want to communicate to the other LLMs beginning by 
        COMMUNICATE: 
        THOUGHTS:
        BOT COMMAND: 
        """)
        self.conversation_history.append(conversation_history)
        return [sys_prompt] + self.conversation_history
    
    
    def init_pos(self):
        return np.array([np.trunc(self.id/2), self.id%2])
    
    def random_init_pos(self):
        return np.random.randint(0, 10, size=(2), dtype=int) # quadrillage 10x10
    
    def set_model(self, model):
        self.MODEL = model
