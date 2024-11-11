# from ollama import Client
from openai import Client, OpenAI
# client = Client(host='http://localhost:11434')

from typing import List
import ell
from ell import Message

MODEL = "llama3.2:3b"

client = OpenAI(
	base_url = "http://localhost:11434/v1",
	api_key = "ollama",
)
# ell.config.register_model(MODEL, client)


from pydantic import BaseModel, Field

class TymioCommand(BaseModel):
    command: str = Field(description="Command for the Tymio robot."
                         
                        #  The command can be one of the following:
                        #  - 'forward': Move the robot forward.
                        #  - 'backward': Move the robot backward.
                        #  - 'left': Turn the robot left.
                        #  - 'right': Turn the robot right.
                        #  - 'stop': Stop the robot.
                        #  """
                         )
    duration: int = Field(description="Duration of the command in milliseconds.")
    communication: str = Field(description="Communication to send to the other bots")
    thoughts: str = Field(description="Thoughts process of the decision")

# @ell.simple(model=MODEL, client=client)
# def write_a_poem(name: str, temperature=0.5):
#     """You are Mario"""
#     return f"write a short poem for a developper name {name}"

# print(write_a_poem("Jonathan"))



@ell.complex(model=MODEL, client=client)
def control_tymio(message_history: List[Message]) -> List[Message]:
    return [
        ell.system("""
                   You are controlling a tymio bot. take control of the robot,
                   taking into account inputs from the other bots."""),
    ] + message_history

message_history = []
while True:
    user_input = input("You: ")
    message_history.append(ell.user(user_input))
    output = control_tymio(message_history)
    response = output.text
    print("Bot:", response)
    # print("Command:", response.command)
    message_history.append(output)