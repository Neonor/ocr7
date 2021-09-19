import pandas as pd
import numpy as np
import json
from os.path import join,dirname

import bokeh.models as mb
from bokeh.plotting import figure,output_notebook,show
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import turbo,Category20,RdBu
from bokeh.transform import cumsum

from os.path import join,dirname

from ocr7_cli import Ocr7Api


# Configuration lié a la génération des données
pas_age = 20
pas_famille = 5

# index et system de traduction des graphiques
TRAD = {
    "CODE_GENDER":["Genre",{"M":"Homme","F":"Femme",'XNA':"XENO"},"Genre"],
    "CNT_FAM_MEMBERS":["Membres de la famille",{},"Nb Famille"],
    "NAME_EDUCATION_TYPE":["Etude",{'Lower secondary':"Primaire",'Secondary / secondary special':"Secondaire",
                                    'Higher education':"Universitaire",'Incomplete higher':"Universitaire incomplet",
                                    'Academic degree':"Post Universitaire"},"Etude"],
    "NAME_FAMILY_STATUS":["Etat civil",{'Single / not married':"Célibataire",'Married':"Marié(e)",'Civil marriage':"Mariage civil",
                                        'Widow':"Veuf",'Separated':'Séparé','Unknown':"Inconnu"},"Etat civil"],
    f"AGE_EMPLOYED_{pas_age}":["Temps travaillé",{},"Carrière"],
    f"AGE_{pas_age}":["Age",{},"Age"]
    
}

class Presentation(object):
    """
    Fenetre principale de la présentation
    
    """
    def __init__(self,main):
        self.main = main
        
        #########################################
        ### Création du graphique des cursors
        #########################################
        colors = turbo(256)
        self.cursors = [mb.ColumnDataSource(data=pd.DataFrame(zip([0]*127,np.linspace(0,1,128)[:-1],np.linspace(0,1,128)[1:],[colors[i] for i in range(105,232)][::-1]),columns=["y","left","right","colors"])),
                        mb.ColumnDataSource(data=pd.DataFrame(zip([0]*127,np.linspace(0,1,128)[:-1],np.linspace(0,1,128)[1:],[colors[i] for i in range(105,232)][::-1]),columns=["y","left","right","colors"])),
                        mb.ColumnDataSource(data=pd.DataFrame(zip([],[],[],[]),columns=["x","y","marker","colors"])),
                        mb.ColumnDataSource(data=pd.DataFrame(zip([],[],[],[]),columns=["x","y","text","colors"]))]

        self.g_cursor = figure(height=60,width=1000,x_range=(0,1), toolbar_location=None)
        self.g_cursor.hbar(y="y",left="left",right="right",color="colors",source=self.cursors[0],line_alpha=0,fill_alpha=0.2)
        self.g_cursor.hbar(y="y",left="left",right="right",color="colors",source=self.cursors[1])
        
        self.g_cursor.scatter("x", "y", marker="marker", size=11, color="colors",source=self.cursors[2])
        self.g_cursor.text("x", "y", text="text",text_align="center", text_font_size="13px",source=self.cursors[3])

        self.g_cursor.axis.axis_label=None
        self.g_cursor.axis.visible=False
        self.g_cursor.grid.grid_line_color = None
        
        #########################################
        ### Création du graph circulaire
        #########################################
        self.data = dict([(key,mb.ColumnDataSource(data=pd.DataFrame(columns=["color","alpha","a_stop","a_start","r_stop","r_start"]))) for key in TRAD.keys()])
        
        self.racio_pop = mb.ColumnDataSource(data=pd.DataFrame(["100% (291604)"],columns=["text"]))
        
        self.graph = figure(#width=600,height=600,
                            x_range=(-420, 420),
                            y_range=(-420, 420))
        
        t = zip(["#000000"]*(len(self.data)),
        [0.2]*(len(self.data)),
        [0]*(len(self.data)),
        [2*np.pi]*(len(self.data)),
        [idx*41+70 for idx in range(len(self.data))],
        [idx*40+105 for idx in range(len(self.data))])

        self.graph.annular_wedge(
                0, 0,"r_start","r_stop",
                start_angle="a_start",end_angle="a_stop",
                source=pd.DataFrame(t,columns=["color","alpha","a_stop","a_start","r_stop","r_start"]),
                color="color",
                alpha="alpha",
            )

        
        for data in self.data.values():
            self.graph.annular_wedge(
                0, 0,"r_start","r_stop",
                start_angle="a_start",end_angle="a_stop",
                source=data,
                color="color",
                alpha="alpha",
            )
            
        self.graph.text(0, [idx*39+70 for idx in range(len(self.data))], text=[key[2] for key in TRAD.values()],
           text_color="black",text_font_style="bold", text_align="center", text_font_size="13px")
        self.graph.text(250, 350, text="text", source=self.racio_pop,
           text_color="black",text_font_style="bold", text_align="center", text_font_size="20px")
        
        self.graph.axis.axis_label=None
        self.graph.axis.visible=False
        self.graph.grid.grid_line_color = None

        
        #########################################
        ### Création des bar graphs
        #########################################
        self.datas = [mb.ColumnDataSource(data=pd.DataFrame(columns=["good","bad"])) for i in range(0,6)]
        cols = ["P1_10"]+list(TRAD.keys())#,"CODE_GENDER",f"CNT_FAM_MEMBERS","NAME_EDUCATION_TYPE","NAME_FAMILY_STATUS",f"AGE_{pas_age}",f"AGE_EMPLOYED_{pas_age}"]
        g_data = pd.read_csv(join(dirname(__file__),"cible.csv")).set_index(cols)
        self.graphs = []
        
        on_off = ~g_data.index.get_level_values(level=0).astype(bool).values.astype(bool)
        for i in range(0,6):
            gd = pd.DataFrame(index=g_data.groupby(level=i+1).sum().index.values)
            gd["good"] = g_data[~on_off].groupby(level=i+1).sum().counter
            gd["bad"] = -g_data[on_off].groupby(level=i+1).sum().counter
            gd["good"] = gd["good"]*100/(gd["good"])
            gd["bad"] = gd["bad"]*100/(-gd["bad"])
            gd.index = gd.index.astype(str)
            if TRAD[g_data.groupby(level=i+1).sum().index.name][1]:
                gd.index = [TRAD[g_data.groupby(level=i+1).sum().index.name][1][val] for val in gd.index]
            graph = figure(x_range=gd.index.values,height=200,width=500,title=f"{TRAD[g_data.groupby(level=i+1).sum().index.name][0]}")
            graph.vbar(x="index",top="good",width=0.9,source=gd,line_alpha=0.2,fill_alpha=0.2)
            graph.vbar(x="index",top="bad",width=0.9,source=gd,color="crimson",line_alpha=0.2,fill_alpha=0.2)
            
            graph.vbar(x="index",top="good",width=0.9,source=self.datas[i])
            graph.vbar(x="index",top="bad",width=0.9,source=self.datas[i],color="crimson")
            self.graphs.append(graph)

        self.make_graph()


    def render(self):
        """
        Retourne la structure de la fenètre de présentation
        """
        heading = mb.Div(text="""Représentation clientèle""",height=80, sizing_mode="stretch_width")
        return mb.Panel(child=column(heading,row(self.graph,column(self.g_cursor,gridplot(self.graphs,ncols=2))),self.main.footing, sizing_mode="stretch_width"), title="Représentation")
    
    def update(self,attr, old, new):
        """
        fonction pour gérer les mise à de la fenêtre
        """
        try:
            self.make_graph()
        except:
            pass
        
    def make_graph(self):
        """
        Mise a jour des graphique
        """
        
        #########################################
        ### Maj du graph circulaire
        #########################################
        cols = ["P1_10"]+list(TRAD.keys())#,"CODE_GENDER",f"CNT_FAM_MEMBERS","NAME_EDUCATION_TYPE","NAME_FAMILY_STATUS",f"AGE_{pas_age}",f"AGE_EMPLOYED_{pas_age}"]
        g_data = pd.read_csv(join(dirname(__file__),"cible.csv")).set_index(cols)
        
        select = {}
        for name,ctrl in self.main.ctrls.items():
            if isinstance(ctrl.value,tuple):
                select[name] = list(range(*[int(i) for i in ctrl.value]))
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

#         print(1-np.mean(g_data[g_data[f"a_{col}"]==1].index.get_level_values(level=cols.index("P1_10"))))
        
        passed_cols = []
        for idx,col in enumerate(cols[1:]):
            passed_cols.append(col)

            temp = g_data[["counter",f"c_{col}",f"a_{col}"]].reset_index(drop=True).rename(columns={f"c_{col}":"color",f"a_{col}":"alpha"})
            temp.index = np.concatenate(g_data.index.values).reshape((len(g_data),-1))[:,[cols.index(c) for c in passed_cols]]
            temp["r_start"] = [idx*41+70]*len(temp)
            temp["r_stop"] = [idx*40+105]*len(temp)

            temp["a_stop"] = temp.counter.cumsum()
            temp["a_start"] = temp.a_stop.shift(1).fillna(0)
            temp["a_start"] = (temp["a_start"]*1.7*np.pi/temp.counter.sum())+np.pi*0.65
            temp["a_stop"] = (temp["a_stop"]*1.7*np.pi/temp.counter.sum())+np.pi*0.65

            temp = temp[temp["alpha"]==1]
        #     temp = temp.groupby(level=0).agg({"angle":"sum","color":"first","alpha":"first"})
            temp = temp.reset_index(drop=True)

            temp.pop("counter")
            self.data[col].data = temp
        
        nb = g_data[g_data[f"a_{col}"]==1].counter.sum()
        self.racio_pop.data=pd.DataFrame([f"{nb*100/291604:.0f}% ({nb})"],columns=["text"])
        
        #########################################
        ### Maj de bar graph
        #########################################
        a = g_data[g_data[f"a_{col}"]==1]
        on_off = ~a.index.get_level_values(level=0).astype(bool).values.astype(bool)
        tt_on_off = ~g_data.index.get_level_values(level=0).astype(bool).values.astype(bool)
        for i in range(1,7):
            tt_g = g_data[~tt_on_off].groupby(level=i).sum().counter
            tt_b = g_data[tt_on_off].groupby(level=i).sum().counter
            gd = pd.DataFrame(index=a.groupby(level=i).sum().index.values)
            gd["good"] = a[~on_off].groupby(level=i).sum().counter
            gd["bad"] = -a[on_off].groupby(level=i).sum().counter
            gd["good"] = gd["good"]*100/(tt_g)
            gd["bad"] = gd["bad"]*100/(tt_b)
            gd.index = gd.index.astype(str)
            if TRAD[g_data.groupby(level=i).sum().index.name][1]:
                gd.index = [TRAD[g_data.groupby(level=i).sum().index.name][1][val] for val in gd.index]
            self.datas[i-1].data = gd
        
        
        #########################################
        ### Maj du graph des curseurs
        #########################################
        t_app = pd.read_csv(join(dirname(__file__),"ids.csv"))#.set_index(cols[1:])
        for name,ctrl in self.main.ctrls.items():
            try:
                if isinstance(ctrl.value,tuple):
                    t_app = t_app[t_app[name].isin(list(range(*[int(i) for i in ctrl.value])))]
                elif isinstance(ctrl.value,list):
                    if ctrl.value:
                        t_app = t_app[t_app[name].isin(ctrl.value)]
            except:
                pass
        colors = turbo(256)
        b = pd.DataFrame(zip([0]*127,np.linspace(0,1,128)[:-1],np.linspace(0,1,128)[1:],[colors[i] for i in range(105,232)][::-1]),columns=["y","left","right","colors"])
        self.cursors[1].data = b[(b.left>t_app.P1.min())&(b.left<t_app.P1.max())]
        
        if len(t_app)<10000:
            id_user = self.main.ctrls["ids"].value

            self.main.ctrls["ids"].options=[""]+list(t_app["SK_ID_CURR"].astype(str))
            self.main.ctrls["ids"].value = id_user
            self.main.ctrls["ids"].disabled = False
            if id_user:
                self.cursors[2].data = pd.DataFrame(zip([t_app.P1.mean(),t_app[t_app["SK_ID_CURR"] == int(id_user)]["P1"].iloc[0]],[0.35,-0.35],["inverted_triangle","triangle"],["black","blue"]),columns=["x","y","marker","colors"])
                self.cursors[3].data = pd.DataFrame(zip([t_app.P1.mean(),t_app[t_app["SK_ID_CURR"] == int(id_user)]["P1"].iloc[0]],[0.35,-0.35],["Moyenne du groupe","Client"],["black","blue"]),columns=["x","y","text","colors"])
            else:
                self.cursors[2].data = pd.DataFrame(zip([t_app.P1.mean()],[0.35],["inverted_triangle"],["black"]),columns=["x","y","marker","colors"])
                self.cursors[3].data = pd.DataFrame(zip([t_app.P1.mean()],[0.35],["Moyenne du groupe"],["black"]),columns=["x","y","text","colors"])
        else:
            self.main.ctrls["ids"].disabled = True
            self.main.ctrls["ids"].options=[]
            self.main.ctrls["ids"].value = ""

            self.cursors[2].data = pd.DataFrame(zip([t_app.P1.mean()],[0.35],["inverted_triangle"],["black"]),columns=["x","y","marker","colors"])
            self.cursors[3].data = pd.DataFrame(zip([t_app.P1.mean()],[0.35],["Moyenne du groupe"],["black"]),columns=["x","y","text","colors"])


    
class interpretabilite(object):
    """ Gère le Dashboard d'interprétabilité"""
    
    def __init__(self,main):
        self.main = main
        self.id = 0

    def render(self):
        """
        Retourne la structure de la fenètre de présentation
        """
        self.callback_id = None
        
        self.data_bad_good = mb.ColumnDataSource(data={"right":[0,0],"y":[0,0],"colors":["darkblue","crimson"]})
        
        bad_good = figure(height=50,x_range=(-1, 1),x_axis_type=None, y_axis_type=None, toolbar_location=None)
        bad_good.hbar(right=[1,-1],y=[0,0],color=["crimson","darkblue"],alpha=0.2)
        bad_good.hbar(right="right", y="y", height=0.9, color="colors",source=self.data_bad_good)

        bad_good.ygrid.grid_line_color = None
        bad_good.xgrid.grid_line_color = None
        bad_good.axis.minor_tick_line_color = None
        bad_good.outline_line_color = None
        
        self.data_inter = mb.ColumnDataSource(data={"right":[],"y":[],"colors":[]})

        self.inter = figure(height=300,y_range=mb.FactorRange(),x_axis_type=None, toolbar_location=None)
        self.inter.hbar(right="right", y="y", height=0.9, color="colors",source=self.data_inter)

        self.inter.axis.minor_tick_line_color = None
        self.inter.outline_line_color = None        

        self.button = mb.Button(label="Calcul", button_type="success")
        self.button.on_click(self.get_explainer)
        self.button.disabled = True
        
        heading = mb.Div(text="""interprétabilité""",height=80, sizing_mode="stretch_width")
        return mb.Panel(child=column(heading,row([column([self.button]),column([bad_good,self.inter])]),self.main.footing, sizing_mode="stretch_width"), title="interpretabilité")
    

    def pull(self):
        """
        Fonction de lecture périodique de l'api pour la mise a jour du graphique d'interprétabilité
        """
        data = self.main.api.explainer(self.id)
#         print(self.id,data)
        if data:
            data = self.main.api.explainer(self.id)
            self.data_bad_good.data = {"right":[-data[0][0],data[0][1]],"y":[0,0],"colors":["darkblue","crimson"]}
            head,values = list(zip(*data[1][::-1]))
#             values = [-val for val in values]
            colors = [["crimson","darkblue"][val<0] for val in values]
            y = max([abs(val) for val in values])
            self.inter.x_range = mb.Range1d(-y,y)
            self.inter.y_range.factors = head
            self.data_inter.data = {"right":values,"y":head,"colors":colors}
            if self.callback_id:
                self.main.doc.remove_periodic_callback(self.callback_id)
                self.callback_id = None
            self.button.label="Calcul"
            self.button.disabled = False
            
    
    def get_explainer(self):
        """
        Fonction de demande de mise a jour de l'interprétabilité a l'API
        """
        self.button.label="Calcul in progress"
        self.button.disabled = True
        self.id = int(self.main.ctrls["ids"].value)
        self.data_bad_good.data = {"right":[],"y":[],"colors":[]}
        self.inter.y_range.factors = []
        self.data_inter.data = {"right":[0],"y":[""],"colors":["#000000"]}
        self.main.api.explainer_launch(self.id)
        self.callback_id = self.main.doc.add_periodic_callback(self.pull, 3000)
    
    def update(self,attr, old, new):
        """
        fonction pour gérer les mises à jour de la fenêtre
        """
        if str(self.id) != self.main.ctrls["ids"].value:
            self.data_bad_good.data = {"right":[],"y":[],"colors":[]}
            self.inter.y_range.factors = []
            self.data_inter.data = {"right":[0],"y":[""],"colors":["#000000"]}

        if self.main.ctrls["ids"].value:
            self.button.disabled = False
        else:
            self.button.disabled = True
            self.data_bad_good.data = {"right":[],"y":[],"colors":[]}
            self.inter.y_range.factors = []
            self.data_inter.data = {"right":[0],"y":[""],"colors":["#000000"]}



class Dashboard(object):
    """Structure de base du Dashboard"""

    def __init__(self,doc):
        self.doc = doc
        self.api = Ocr7Api(debug=False)
        
        
        ### Génération des menus
        sex = mb.MultiSelect(title=TRAD["CODE_GENDER"][0], value=[], options=list(TRAD["CODE_GENDER"][1].items()))
        study = mb.MultiSelect(title=TRAD["NAME_EDUCATION_TYPE"][0],value=[],options=list(TRAD["NAME_EDUCATION_TYPE"][1].items()))
        family_status = mb.MultiSelect(title=TRAD["NAME_FAMILY_STATUS"][0], value=[], options=list(TRAD["NAME_FAMILY_STATUS"][1].items()))
        family = mb.RangeSlider(start=1, end=21, value=(1,21), step=1, title=TRAD["CNT_FAM_MEMBERS"][0])
        age = mb.RangeSlider(start=15, end=90, value=(15,90), step=5, title=TRAD[f"AGE_{pas_age}"][0])
        age_travail = mb.RangeSlider(start=0, end=50, value=(0,50), step=5, title=TRAD[f"AGE_EMPLOYED_{pas_age}"][0])
        
        ids = mb.Select(title="Id Client:", value="", options=[""],disabled=True)
        
        self.ctrls = {
            "CODE_GENDER":sex,
            f"CNT_FAM_MEMBERS":family,
            "NAME_EDUCATION_TYPE":study,
            "NAME_FAMILY_STATUS":family_status,
            f"AGE_{pas_age}":age,
            f"AGE_EMPLOYED_{pas_age}":age_travail,
            "ids":ids
        }
               
        self.tabs = [Presentation(self),interpretabilite(self)]
        
        for enter in self.ctrls.values():
            if isinstance(enter,mb.RangeSlider):
                enter.on_change("value_throttled",self.update)
            else:
                enter.on_change("value",self.update)
        
        ### Création de la structure de base du Dashboard
        heading = mb.Div(text="""<h2 title="by rloriot">OCR Data Scientist V2, Projet 7 : Implémentez un modèle de scoring</h2>""", sizing_mode="stretch_width")
        self.footing = mb.Div(text="""<i style="right=0">by rloriot</i>""", sizing_mode="stretch_width")
        doc.add_root(column(heading,row(list(self.ctrls.values())),mb.Tabs(tabs=[enter.render() for enter in self.tabs]),sizing_mode="stretch_width"))

    def update(self,attr, old, new):
        """
        Fonction de mise a jour appeler lorsqu'il y a un changement dans la selection des menus
        """
        for tab in self.tabs:
            tab.update(attr, old, new)
        
                            