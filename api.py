import uvicorn
from json import load
from api import app

with open("config.json","r") as f_conf:
    config = load(f_conf)

uvicorn.run(app, host=config["host"], port=config["port_api"], log_level="info")