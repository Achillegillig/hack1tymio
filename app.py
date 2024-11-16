import streamlit as st
from openai import OpenAI
import ell
from ell import Message
from agent_plafrim import Agent
import os
import dotenv
dotenv.load_dotenv()

ell.init(store="./logdir")

# Configuration du client OpenAI
client = OpenAI(
	base_url = os.getenv('BASE_URL'),
	api_key = os.getenv('API_KEY'),
)
ell.config.register_model(os.getenv('MODEL'), client)

# @ell.complex(model=os.getenv('MODEL'), temperature=0.3)
# def act(self, conversation_history: List[Message]) -> Message:
#     sys_prompt = ell.system(f"""
#     You are {self.name}, a thymio bot who is {self.role}. You have two thymio bot
#     friends with you. Your goal is to get out of a maze.
#     Given the conversation history, you must return
#     your thoughts on the situation and your mood on a scale from 0 to 10
#     write what you want to communicate to the other LLMs beginning by 
#     COMMUNICATE: 
#     THOUGHTS:
#     BOT COMMAND: 
#     """)
#     self.conversation_history.append(conversation_history)
#     return [sys_prompt] + self.conversation_history

# @ell.complex(model=os.getenv('MODEL'), temperature=0.3)
# def act(thymio_id: str, conversation_history: list[Message]) -> Message:
#     sys_prompt = ell.system(f"""
#     You are {thymio_id}, a thymio bot. You have two thymio bot
#     friends with you. Your goal is to get out of a maze.
#     The two other bots are nearby, ready to communicate.
#     Given the conversation history, you must return
#     your thoughts on the situation and your mood on a scale from 0 to 10
#     write what you want to communicate to the other thymios beginning by "communicate".

#     Response format:

#     COMMUNICATE:
#     THOUGHTS:
#     BOT COMMAND:
#     """)
#     return [sys_prompt] + conversation_history

class Assembly:
    def __init__(self, model=os.getenv('MODEL')) -> None:
        self.agents = []
        self.model = model
        self.conversation_hist = []

    def launch_round(self):
        for i, agent in enumerate(self.agents):
            if i == 0:
                self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))

            message = agent.act(self.conversation_hist)
            st.write(f'{agent.name}: {message.text}')
            self.conversation_hist.append(ell.user([f'{agent.name}:', message]))

# Créer des agents
agent1 = Agent(0, "Thymio1")
agent2 = Agent(1, "Thymio2")

# Créer une assemblée d'agents
assembly = Assembly()
assembly.agents.append(agent1)
assembly.agents.append(agent2)

# Lancer une série de tours de conversation
st.title("Conversation entre agents LLM")
for _ in range(5):  # Nombre de tours de conversation
    assembly.launch_round()
