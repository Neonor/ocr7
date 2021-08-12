from os.path import join,dirname
from pickle import load
import pandas as pd
import gc
from sys import argv,exit

ID = int(argv[-1])

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
        del f_std
        gc.collect()

        with open(join(dirname(__file__),"model.pk"),"rb") as f_model:
            model = load(f_model)
            extract = model.predict_proba(std)
        del model
        del f_model
        gc.collect()

        print(list(extract[0]),end="")
        exit()

