import json
import requests

def chat(model, messages):
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
	stream=True
    )
    r.raise_for_status()
    output = ""

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content
            # the response streams one token at a time, print that as we receive it
            print(content, end="", flush=True)

        if body.get("done", False):
            message["content"] = output
            return message


class Agent:
    def __init__(self, role) -> None:
        self.role = role

# TODO Past a certain context length, summarize
class Assembly:
    def __init__(self, model="llama3.2:1b") -> None:
        self.agents = []
        self.context = [
            {"role": "user", "content": "You are a bunch a tymio bots"}
        ]
        self.model = model

    def launch_round(self):
        for agent in self.agents:
            print(agent.role)
            self.context.append(
                {"role": "user",
                 "content": f"Your turn, {agent.role}. Start by identifying yourself, but keep it short"
                }
            )
            print()
            message = chat(self.model, self.context)
            self.context.append(message)
            print()

if __name__ == "__main__":
    assembly = Assembly()
    for i in range(3):
        agent = Agent(f"tymio_{i}")
        assembly.agents.append(agent)

    assembly.launch_round()
    assembly.launch_round()

            

