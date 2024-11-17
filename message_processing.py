from ell import Message
from typing import List



def get_response_item(response: Message, item: str) -> str:
    ["COMMUNICATE", "THOUGHTS", "BOT_COMMAND"]
    return response.text.split(item + ": ")[1].split("\n")[0]

def process_response_item(response: Message):
    seps = ["THOUGHTS", "MESSAGE" "ACTION"]
    message = dict()
    
    message["THOUGHTS"] = response.text.split("MESSAGE" + ":")[0]
    #message["MOOD"] = response.text.split("MOOD" + ": ")[1].split("COMMUNICATE" + ": ")[0]
    message["MESSAGE"] = response.text.split("MESSAGE" + ":")[1].split("ACTION" + ":")[0]
    message["ACTION"] =  response.text.split("ACTION"+ ":")[1]
    return message


def split_response(response: Message, items: List) -> dict:
    out = {}
    for item in items:
        out[item] = get_response_item(response, item)
    return out
