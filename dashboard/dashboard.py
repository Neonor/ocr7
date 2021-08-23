import pandas as pd
import numpy as np
import json
from os.path import join,dirname

import bokeh.models as mb
from bokeh.plotting import figure,output_notebook,show
from bokeh.layouts import column, row, layout
from bokeh.palettes import turbo,Category20,RdBu
from bokeh.transform import cumsum


import json

from os.path import join,dirname


pas_age = 20
pas_famille = 5

class Presentation(object):
    def __init__(self,main):
        self.main = main
        self.graph = figure(width=400,height=400,
                            x_range=(-420, 420),
                            y_range=(-420, 420))
        self.make_graph()

    def render(self):
        heading = mb.Div(text="""Représentation clientèle""",height=80, sizing_mode="stretch_width")
        return mb.Panel(child=column(heading,self.graph,self.main.footing, sizing_mode="stretch_width"), title="Représentation")
    
    def update(self,attr, old, new):
        self.make_graph()
    
    def make_graph(self):
        self.graph.renderers.clear()
        cols = ["P1_10","CODE_GENDER",f"CNT_FAM_MEMBERS","NAME_EDUCATION_TYPE","NAME_FAMILY_STATUS",f"AGE_{pas_age}",f"AGE_EMPLOYED_{pas_age}"]
        g_data = pd.read_csv("dashboard/cible.csv").set_index(cols)
        
        select = {}
        for name,ctrl in self.main.ctrls.items():
            if isinstance(ctrl.value,tuple):
                select[name] = list(range(*ctrl.value))
            elif isinstance(ctrl.value,list):
                if ctrl.value:
                    select[name] = list(ctrl.value)
        
        alpha = np.full(len(g_data),True)
        for col in cols:
        #     print(g_data.index.get_level_values(level=cols.index(col))==select[col])
            if col in select:
                if not isinstance(select[col],list):
                    select[col] = [select[col]]
                alpha = alpha & (g_data.index.get_level_values(level=cols.index(col)).isin(select[col]))
            g_data[f"a_{col}"] = alpha.astype(float)#*0.8+0.2


        g_data["alpha"] = alpha.astype(float)#*0.8+0.2
        g_data[f"c_{cols[0]}"] = [["#55DD55","#DD5555"][val] for val in g_data.index.get_level_values(level=0)]

        inner_radius = 90
        outer_radius = inner_radius+20

        colors = turbo(256)
        colors_pas = np.arange(0,2*np.pi,2*np.pi/256)
        for idx,col in enumerate(cols[1:]):
            self.graph.annular_wedge(
                0, 0,
                idx*41+70, idx*40+105,#outer_radius,
                start_angle=colors_pas, end_angle=colors_pas+2*np.pi/256,
                color="#000000",#turbo(256),
                alpha=0.2,
                line_alpha=0
            )
        for idx,col in enumerate(cols[1:]+[cols[0]]):
            self.graph.annular_wedge(
                0, 0,
                idx*41+70, idx*40+105,#outer_radius,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                source=g_data,#.groupby(level=cols.index(col)).agg({"angle":"sum",f"c_{col}":"first",f"a_{col}":"first"}),
                color=f"c_{col}",
                alpha=f"a_{col}",
            )

        self.graph.axis.axis_label=None
        self.graph.axis.visible=False
        self.graph.grid.grid_line_color = None
    
class interpretabilite(object):
    def __init__(self,main):
        self.main = main

    def render(self):
        self.out = mb.Div(text="")
        button = mb.Button(label="Calcul", button_type="success")
        
        heading = mb.Div(text="""interprétabilité""",height=80, sizing_mode="stretch_width")
        return mb.Panel(child=column(heading,row([column([button]),self.out]),self.main.footing, sizing_mode="stretch_width"), title="interpretabilité")
    
    def update(self,attr, old, new):
        pass
    
class Dashboard(object):
    def __init__(self,doc):
        sex = mb.MultiSelect(title="Sex :", value=[], options=[("H","Homme"),("F","Femme"),('XNA',"XENO")])
        study = mb.MultiSelect(title="Etude :",value=[],options=[('Lower secondary',"Primaire"),('Secondary / secondary special',"Secondaire"), ('Higher education',"Universitaire"),('Incomplete higher',"Universitaire incomplet"), ('Academic degree',"Post Universitaire")])
        family_status = mb.MultiSelect(title="Sex :", value=[], options=[('Single / not married',"Célibataire"), ('Married',"Marié"), ('Civil marriage',"Mariage civil"), ('Widow',"Veuf"), ('Separated','Séparé'), ('Unknown',"Inconnu")])
        family = mb.RangeSlider(start=1, end=21, value=(1,21), step=1, title="Membres de la famille :")
        age = mb.RangeSlider(start=15, end=90, value=(15,90), step=5, title="Age :")
        age_travail = mb.RangeSlider(start=0, end=50, value=(0,50), step=5, title="Temp de travail :")
        
        ids = mb.Select(title="Ids:", value="", options=[""],disabled=True)
        
        self.ctrls = {
            "CODE_GENDER":sex,
            f"CNT_FAM_MEMBERS":family,
            "NAME_EDUCATION_TYPE":study,
            "NAME_FAMILY_STATUS":family_status,
            f"AGE_{pas_age}":age,
            f"AGE_EMPLOYED_{pas_age}":age_travail
        }
        
#         self.ctrls = [sex,study,family_status,family,age,age_travail,ids]
       
        self.tabs = [Presentation(self),interpretabilite(self)]
        
        for enter in self.ctrls.values():
            enter.on_change("value",self.update)
        
        heading = mb.Div(text="""<h2 title="by rloriot">OCR Data Scientist V2, Projet 7 : Implémentez un modèle de scoring</h2>""", sizing_mode="stretch_width")
        self.footing = mb.Div(text="""<i style="right=0">by rloriot</i>""", sizing_mode="stretch_width")
        doc.add_root(column(heading,row(list(self.ctrls.values())),mb.Tabs(tabs=[enter.render() for enter in self.tabs]),sizing_mode="stretch_width"))

    def update(self,attr, old, new):
        for tab in self.tabs:
            tab.update(attr, old, new)
        
                            