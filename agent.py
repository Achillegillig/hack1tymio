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
dotenv.load_dotenv()


# MODEL="llama3.2:3b"
#MODEL = "Qwen/Qwen2.5-72B-Instruct-AWQ"
#MODEL = os.getenv('MODEL')

class Agent:
    def __init__(self, id, name, color=None,  role=None) -> None:
        self.role = role
        self.name = name
        self.id = id
        self.pos = self.init_pos()
        self.conversation_history = []
        self.immobilised  = False
        self.goal_achieved = False

    @ell.complex(model=MODEL, temperature=0.3)
    def act(self, conversation_history: List[Message]) -> Message:
        self.sys_prompt = ell.system(f"""
        You are {self.name}, a thymio bot who is {self.role}. You have two thymio bot
        friends with you. Your goal is to get out of a maze. 
        Given the conversation history, you must return
        your thoughts on the situation and your mood on a scale from 0 to 10
        write what you want to communicate to the other LLMs beginning by 
        COMMUNICATE: 
        THOUGHTS:
        BOT COMMAND: 
        """)
        self.conversation_history.append(ell.system(f"""{self.name}, you are in position {self.pos}
                                        your current traits / their evolution since last round: {self.traits}

                                        information on other bots nearby: """))
        
                                        # {supervisor.trigger_event(pos)}
        self.conversation_history.append(conversation_history)
        return [self.sys_prompt] + self.conversation_history
    
    def detectNeighbour(self, matrice):
        x = self.pos[0]
        y = self.pos[1]
        self.neighbour = set()
        
        p_neighbourg_x = np.array([x-1, x+1])
        p_neighbourg_y = np.array([y-1, y+1])

        for x_pos in p_neighbourg_x :
            for y_pos in p_neighbourg_y:
                if y>= 0 and y <10 and y>= 0 and y <10 : # 10 est une valeur arbitraire en fonction de la taille du quadrillage
                    if matrice[x_pos, y_pos] != False:
                        self.neighbour[matrice[x_pos, y_pos]]= np.array([x_pos, y_pos])

    def isgoalAchieved(self):
        if self.pos == self.final_pos :
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
        
    
    def init_pos(self):
        return np.array([np.trunc(self.id/2), self.id%2])
    
    def random_init_pos(self):
        return np.random.randint(0, 10, size=(2), dtype=int) # quadrillage 10x10
    
