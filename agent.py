import json
import requests
from openai import Client, OpenAI
import numpy as np
from typing import List
import ell
from ell import Message
from message_processing import get_response_item
from pydantic import BaseModel, Field
import os
import dotenv
from prompt import prompt_ally
from initial_prompt import initial_prompt
dotenv.load_dotenv()


# MODEL="llama3.2:3b"
#MODEL = "Qwen/Qwen2.5-72B-Instruct-AWQ"
#MODEL = os.getenv('MODEL')

class Agent:
    def __init__(self, role, id, name, pos, goal_pos, color=None) -> None:
        self.role = role
        self.id = id
        self.name = name
        self.pos = pos
        self.goal_pos = goal_pos
        self.color = color
        self.immobilised  = False
        self.goal_achieved = False
        self.traits = None
        self.vision = None
        self.allowed_move = None
        self.action = None
        self.direction = None
        self.orientation = "UP"

    @ell.complex(model=os.getenv('MODEL'), temperature=0.3)
    def act(self, conversation_history: list[Message]) -> Message:
        prompt = prompt_ally(self.name, self.color, conversation_history, self.pos, self.vision, self.allowed_move)
        sys_prompt = ell.system(prompt)
        return [sys_prompt] + conversation_history

    
    def detectNeighbour(self, matrice):
        x = self.pos[0]
        y = self.pos[1]
        self.neighbour = dict()
        
        p_neighbourg_x = np.array([x-1, x+1])
        p_neighbourg_y = np.array([y-1, y+1])

        for x_pos in p_neighbourg_x :
            for y_pos in p_neighbourg_y:
                if y>= 0 and y <10 and y>= 0 and y <10 : # 10 est une valeur arbitraire en fonction de la taille du quadrillage
                    if matrice[x_pos, y_pos] != False:
                        self.neighbour[matrice[x_pos, y_pos]]= np.array([x_pos, y_pos])

    def isgoalAchieved(self):
        if self.pos == self.goal_pos:
            self.goal_achieved = True

    def explore_environement(self, x, y, matrice):
        pass
        
    def update_pos_message(self, done=True):
        command = get_response_item(self.sys_prompt)
        if done==True :
            if command == "GO_DOWN":
                self.pos[1] = self.pos[1]-1
            elif command == "GO_UP":
                self.pos[1] = self.pos[1]+1
            elif command == "GO_RIGHT":
                self.pos[0] = self.pos[0]+1
            elif command == "GO_LEFT":
                self.pos[0] = self.pos[0]+1
            self.pos_message = f""""Vous avez bougé à la position {self.pos}"""
            if command == "STOP":
                self.pos_message = f""""Vous êtes toujours à la position {self.pos}"""
        else : 
            self.pos_message = f""""Vous n'avez pas réussit à bouger et êtes toujours à la position {self.pos}"""

    def link_thymio(self, node_id):
        self.node_id = node_id
        
    
    # def init_pos(self):
    #     return np.array([np.trunc(self.id/2), self.id%2])
    
    # def random_init_pos(self):
    #     return np.random.randint(0, 10, size=(2), dtype=int) # quadrillage 10x10
    
