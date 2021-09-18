from json import load
from api_rest_cli import ApiRestCli

with open("./config.json","r") as f_conf:
    CONFIG = load(f_conf)

class Ocr7Api(ApiRestCli):
    def __init__(self,*args,**kwargs):
        ApiRestCli.__init__(self,f'http://{CONFIG["host"]}:{CONFIG["port_api"]}',*args,**kwargs)
    
    def compute(self,idx):
        return self._get("/compute/",paras={"ID":idx}).data
    
    def compute_launch(self,idx):
        return self._post("/compute/",paras={"ID":idx}).data

    def explainer(self,idx):
        return self._get("/explainer/",paras={"ID":idx}).data
    
    def explainer_launch(self,idx):
        return self._post("/explainer/",paras={"ID":idx}).data
    
    