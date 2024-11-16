from ell import Message
from typing import List



def get_response_item(response: Message, item: str) -> str:
    ["COMMUNICATE", "THOUGHTS", "BOT_COMMAND"]
    return response.text.split(item + ": ")[1].split("\n")[0]

def process_response_item(response: Message):
    seps = ["COMMUNICATE", "THOUGHTS", "BOT_COMMAND"]
    message = dict()
    
    message["THOUGHTS"] = response.text.split("COMMUNICATE" + ":")[0]
    #message["MOOD"] = response.text.split("MOOD" + ": ")[1].split("COMMUNICATE" + ": ")[0]
    message["COMMUNICATE"] = response.text.split("COMMUNICATE" + ":")[1].split("BOT_COMMAND" + ":")[0]
    message["BOT_COMMAND"] =  response.text.split("BOT_COMMAND"+ ":")[1]
    return message


def split_response(response: Message, items: List) -> dict:
    out = {}
    for item in items:
        out[item] = get_response_item(response, item)
    return out
