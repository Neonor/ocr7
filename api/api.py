import pandas as pd
import numpy as np
import gc

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold


from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder, MultiLabelBinarizer
from sklearn.compose import make_column_transformer

import lightgbm as lgb

from pickle import load,loads

from os.path import join,dirname


from fastapi import FastAPI
app = FastAPI()

@app.get('/') 
def home():
    return {"projet":'OCR7'}

@app.get('/compute/')
def compute():
    for data in pd.read_csv("srv/api/computed.xz",compression="xz",chunksize=100000):
        user = data[data.SK_ID_CURR == idc].copy()
        if len(user):
            with open(join(dirname(__file__),"std.pk"),"rb") as f_std:
                standardize = load(f_std)

            with open(join(dirname(__file__),"model.pk"),"rb") as f_model:
                model = load(f_model)
            user.pop("TARGET")
            idc = int(request.args.get('ID'))
            return list(model.predict_proba(standardize.transform(user))[0])
        del data
        gc.collect()
