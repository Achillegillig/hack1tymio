import streamlit as st
from openai import OpenAI
import ell
from ell import Message
from agent import Agent
from Supervisor import Supervisor
import os
import dotenv

# Initialisation
dotenv.load_dotenv()
ell.init(store="./logdir")

# Configuration du client OpenAI
client = OpenAI(
	base_url = os.getenv('BASE_URL'),
	api_key = os.getenv('API_KEY'),
)
ell.config.register_model(os.getenv('MODEL'), client)

# Create & Run the Supervisor
supervisor = Supervisor(n_agents=2, size=(4, 4))

