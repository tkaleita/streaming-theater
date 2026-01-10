import json

from core.config import *

def set_field(field, value):
    update_file(field, value)
    return

def change_field(field, value: int):
    field_value = read_field(field)
    update_file(field, int(field_value) + value)
    return

def update_file(field, value):
    data = read_file()
    data[field] = value

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"{field} is now: {data[field]}")
    return

def read_field(field):
    data = read_file()
    return data.get(field, 0)

def read_file():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data