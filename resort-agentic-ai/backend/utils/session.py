import re


def extract_room_number(message: str):
    match = re.search(r"\b(10[1-9]|110)\b", message)
    if match:
        return int(match.group())
    return None
