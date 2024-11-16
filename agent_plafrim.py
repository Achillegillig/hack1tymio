import json
import requests
from openai import Client, OpenAI
import numpy as np
from typing import List
import ell
from ell import Message
import os
import dotenv
from pydantic import BaseModel, Field
dotenv.load_dotenv()


class Agent:
    def __init__(self, role, id, name, pos, goal_pos) -> None:
        self.role = role
        self.id = id
        self.name = name
        self.pos = pos
        self.goal_pos = goal_pos

    @ell.complex(model=os.getenv('MODEL'), temperature=0.3)
    def act(self, conversation_history: list[Message]) -> Message:
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
        return [sys_prompt] + conversation_history
    
    
    # def init_pos(self):
    #     return np.array([np.trunc(self.id/2), self.id%2])
    
    # def random_init_pos(self):
    #     return np.random.randint(0, 10, size=(2), dtype=int) # quadrillage 10x10
    
