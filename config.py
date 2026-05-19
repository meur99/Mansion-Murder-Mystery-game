import os
import json

# Data Blueprint File Path Maps
DATA_DIR = "data"
WORLD_DATA_PATH = os.path.join(DATA_DIR, "mansion_data.json")
PROMPTS_DATA_PATH = os.path.join(DATA_DIR, "prompts.json")
KEYS_DATA_PATH = os.path.join(DATA_DIR, "keys.json")

# AI Model Configuration Setup
global API_KEY
if os.path.exists(KEYS_DATA_PATH):
    with open(KEYS_DATA_PATH, 'r') as file:
        data = json.load(file)
        API_KEY = data.get("NPC_JSON")

MODEL_NAME = "gemma-4-31b-it"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
