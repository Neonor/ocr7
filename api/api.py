from os.path import join,dirname
from pickle import load
import pandas as pd
import gc

# from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
# from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder, MultiLabelBinarizer
# from sklearn.compose import make_column_transformer

# import lightgbm as lgb


from fastapi import FastAPI
app = FastAPI()

@app.get('/') 
def home():
    return {"projet":'OCR7'}

@app.get('/compute/')
def compute(ID:int):
#     idc = int(request.args.get('ID'))
    for data in pd.read_csv(join(dirname(__file__),"computed.xz"),index_col=0,compression="xz",chunksize=100000):
        user = data[data.SK_ID_CURR == ID].copy()
        user.pop("TARGET")
        del data
        gc.collect()
        if len(user):
            with open(join(dirname(__file__),"std.pk"),"rb") as f_std:
                standardize = load(f_std)
                std = standardize.transform(user)
                del standardize
                gc.collect()

            with open(join(dirname(__file__),"model.pk"),"rb") as f_model:
                model = load(f_model)
                extract = model.predict_proba(std)
                del model
                gc.collect()
                
            return list(extract[0])

