from os.path import join,dirname
from pickle import load
import pandas as pd
import gc

from subprocess import Popen,PIPE
from json import loads

from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles

app = FastAPI()
temp = {}

try:
    app.mount("/static", StaticFiles(directory="/mnt/neonor.org"), name="static")
except:
    pass

@app.get('/') 
async def home():
    """ fonction d'accueil de l'API """
    return {"projet":'OCR7'}



"""
Block de calcul model low memory asynchrone
"""

def task_compute(idx):
    a,_ = Popen(["python","api/compute.py",idx],stdout=PIPE).communicate()
    temp["compute"] = loads(a.decode())

@app.post("/compute/")
async def compute_lite(ID:int,background_tasks: BackgroundTasks):
    """
    Fonction de calcul du model pour un client
    fonction "lite" : executer en subprocess pour économiser de la memoire sur le serveur aws (1Go RAM) car une fois executé,
    les librairies chargées indépendament du modèle prennent 33% de la mémoire et si les models sont gardés chargés, l'occupation monte a 64%
    """
    if "compute" in temp:
        del temp["compute"]
    background_tasks.add_task(task_compute,idx=str(ID))
    return True

@app.get("/compute/")
async def compute_result():
    """
    Fonction de calcul du model pour un client
    fonction "lite" : executer en subprocess pour économiser de la memoire sur le serveur aws (1Go RAM) car une fois executé,
    les librairies chargées indépendament du modèle prennent 33% de la mémoire et si les models sont gardés chargés, l'occupation monte a 64%
    """
    return temp.get("compute",[])



"""
Block de calcul explainer low memory asynchrone
"""

def task_explainer(idx):
    a,_ = Popen(["python","api/explainer.py",idx],stdout=PIPE).communicate()
    temp["explainer"] = loads(a.decode())

@app.post("/explainer/")
async def explainer_lite(ID:int,background_tasks: BackgroundTasks):
    """
    Fonction d'explanation du model pour un client
    fonction "lite" : executer en subprocess pour économiser de la memoire sur le serveur aws (1Go RAM)
    """
    if "explainer" in temp:
        del temp["explainer"]
    background_tasks.add_task(task_explainer,idx=str(ID))
    return True

@app.get("/explainer/")
async def compute_result():
    """
    Fonction d'explanation du model pour un client
    fonction "lite" : executer en subprocess pour économiser de la memoire sur le serveur aws (1Go RAM)
    """
    return temp.get("explainer",[])

# @app.get('/compute/')
# async def compute(ID:int):
#     """
#     Fonction de calcul du model pour un client
#     """
#     for data in pd.read_csv(join(dirname(__file__),"computed.xz"),index_col=0,compression="xz",chunksize=100000):
#         user = data[data.SK_ID_CURR == ID].copy()
#         user.pop("TARGET")
#         del data
#         gc.collect()
#         if len(user):
#             with open(join(dirname(__file__),"std.pk"),"rb") as f_std:
#                 standardize = load(f_std)
#                 std = standardize.transform(user)
#             del standardize
#             del f_std
#             gc.collect()

#             with open(join(dirname(__file__),"model.pk"),"rb") as f_model:
#                 model = load(f_model)
#                 extract = model.predict_proba(std)
#             del model
#             del f_model
#             gc.collect()
                
#             return list(extract[0])

