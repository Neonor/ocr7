from os.path import join,dirname
import pickle as pk
import dill
import pandas as pd
import gc
from json import dumps
from sys import argv,exit#,stdin,stdout
# stdin.reconfigure(encoding='utf-8')
# stdout.reconfigure(encoding='utf-8')
ID = int(argv[-1])

for data in pd.read_csv(join(dirname(__file__),"pre_computed.xz"),index_col=0,compression="xz",chunksize=100000):
    user = data[data.index == ID].copy()
    user.pop("TARGET")
    del data
    gc.collect()
    if len(user):
        with open(join(dirname(__file__),"std.pk"),"rb") as f_std:
            standardize = pk.load(f_std)
            std = standardize.transform(user)
        del standardize
        del f_std
        gc.collect()
        
        with open(join(dirname(__file__),"model.pk"),"rb") as f_model:
            model = pk.load(f_model)
        del f_model
        gc.collect()
        
        with open(join(dirname(__file__),"explainer.pk"),"rb") as f_exp:
            explainer = dill.load(f_exp)
        
        explanation = explainer.explain_instance(
            std[0],
            model.predict_proba,
            num_features=20
        )
        print(dumps([list(explanation.predict_proba),explanation.as_list()]),end="")
        exit()

