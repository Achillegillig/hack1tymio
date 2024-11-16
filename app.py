import streamlit as st
from openai import OpenAI
import ell
from ell import Message
from agent_plafrim import Agent
from assembly_plafrim import Assembly
import os
import dotenv
from styles import styles
dotenv.load_dotenv()

ell.init(store="./logdir")

# Configuration du client OpenAI
client = OpenAI(
	base_url = os.getenv('BASE_URL'),
	api_key = os.getenv('API_KEY'),
)
ell.config.register_model(os.getenv('MODEL'), client)

# Créer des agents
assembly = Assembly()
names = ['Thymio1', 'Thymio2', 'Thymio3', 'Thymio4', 'Thymio5']
for i, name in enumerate(names):
    agent = Agent(i, name)
    assembly.agents.append(agent)

# Ajouter des styles CSS pour les bulles de conversation
st.markdown(styles, unsafe_allow_html=True)

# Lancer une série de tours de conversation
st.title("Conversation entre agents LLM")
for _ in range(5):  # Nombre de tours de conversation
    assembly.launch_round()
