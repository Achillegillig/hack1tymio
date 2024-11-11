from openai import Client, OpenAI


import ell

MODEL = "llama3.2:3b"

client = OpenAI(
	base_url = "http://localhost:11434/v1",
	api_key = "ollama",
)


ell.config.register_model(MODEL, client)