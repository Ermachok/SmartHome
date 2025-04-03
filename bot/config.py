import json

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ALLOWED_USERS = config["ALLOWED_USERS"]
DJANGO_SERVER = config["DJANGO_SERVER"]
