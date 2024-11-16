from ell import Message
from typing import List

def get_response_item(response: Message, item: str) -> str:
    return response.text.split(item + ": ")[1].split("\n")[0]


def split_response(response: Message, items: List(str)) -> dict:
    out = {}
    for item in items:
        out[item] = get_response_item(response, item)
    return out
