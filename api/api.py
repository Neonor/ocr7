from os.path import join,dirname
import pickle as pk
import pandas as pd
import gc

from subprocess import Popen,PIPE
from json import loads,load,dump

from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles

app = FastAPI()
try:
    with open("temp.json","r") as f_exp:
        temp = load(f_exp)
except:
    temp = {"compute":{},"explainer":{}}

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
    temp["compute"][int(idx)] = loads(a.decode())
    with open("temp.json","w") as f_exp:
        dump(temp,f_exp)

@app.post("/compute/")
async def compute_lite(ID:int,background_tasks: BackgroundTasks):
    """
    Fonction de calcul du model pour un client (ID exemple : 100002)
    fonction "lite" : executer en subprocess pour économiser de la memoire sur le serveur aws (1Go RAM) car une fois executé,
    les librairies chargées indépendament du modèle prennent 33% de la mémoire et si les models sont gardés chargés, l'occupation monte a 64%
    """
    if not ID in temp["compute"]:
#         del temp["compute"][ID]
        background_tasks.add_task(task_compute,idx=str(ID))
    return True

@app.get("/compute/")
async def compute_result(ID:int):
    """
    Affiche le résusltat du dernier calcul de score
    """
    return temp.get("compute",{}).get(ID,[])



"""
Block de calcul explainer low memory asynchrone
"""

def task_explainer(idx):
    a,_ = Popen(["python","api/explainer.py",str(idx)],stdout=PIPE).communicate()
    temp["explainer"][idx] = loads(a.decode())
    with open("temp.json","w") as f_exp:
        dump(temp,f_exp)

@app.post("/explainer/")
async def explainer_lite(ID:int,background_tasks: BackgroundTasks):
    """
    Fonction d'explanation du model pour un client (ID exemple : 100002)
    fonction "lite" : executer en subprocess pour économiser de la memoire sur le serveur aws (1Go RAM)
    """
    if not ID in temp["explainer"]:
#         del temp["explainer"][ID]
        background_tasks.add_task(task_explainer,idx=ID)
    return True

@app.get("/explainer/")
async def compute_result(ID:int):
    """
    Affiche le résusltat du dernier calcul d'interprétation
    """
    return temp.get("explainer",{}).get(ID,[])

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

