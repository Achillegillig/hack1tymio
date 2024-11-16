import json
import requests
from openai import Client, OpenAI

from typing import List
import ell
from ell import Message

from pydantic import BaseModel, Field

from agent import Agent

from assembly import Assembly

MODEL = "llama3.2:3b"
ell.init(store="./logdir")

client = OpenAI(
	base_url = "http://localhost:11434/v1",
	api_key = "ollama",
)
ell.config.register_model(MODEL, client)


if __name__ == "__main__":
    assembly = Assembly()
    for i in range(3):
        thymio_ids = ["thymiotée", "robob", "llamario"]
        agent = Agent(i, thymio_ids[i])
        assembly.agents.append(agent)


    assembly.launch_round()
    assembly.launch_round()
    print(assembly.conversation_hist)

