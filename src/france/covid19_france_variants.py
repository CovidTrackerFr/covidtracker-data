#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.covidtracker.fr
Mail : guillaume.rozier@telecomnancy.net

README:
This file contains scripts that download data from data.gouv.fr and then process it to build many graphes.
I'm currently cleaning the code, please ask me if something is not clear enough.

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[2]:


def nbWithSpaces(nb):
    str_nb = str(int(round(nb)))
    if(nb>100000):
        return str_nb[:3] + " " + str_nb[3:]
    elif(nb>10000):
        return str_nb[:2] + " " + str_nb[2:]
    elif(nb>1000):
        return str_nb[:1] + " " + str_nb[1:]
    else:
        return str_nb


# In[3]:


import pandas as pd
import numpy as np
import json
PATH = "../../"
PATH_STATS = "../../data/france/stats/"
import france_data_management as data
import plotly.graph_objects as go
import locale
from datetime import datetime
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()


# In[4]:


data.download_data()
df_tests =data.import_data_tests_sexe()
df_tests = df_tests[df_tests.cl_age90 == 0]
df_tests["P_rolling"] = df_tests["P"].rolling(window=7).mean()


# In[5]:


data.download_data_variants()
df_variants = data.import_data_variants()


# In[6]:


df_variants["jour"] = df_variants.semaine.apply(lambda x: x[11:]) 


# In[7]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=df_variants.tx_D1,
        name="Mutation D1 (" + str(df_variants.tx_C1.values[-1]).replace(".", ",") + " %)",
        showlegend=True,
    )
)

y=df_variants.tx_A0C0
fig.add_trace(
    go.Scatter(
        x=df_variants.jour,
        y=y,
        name="Mutations A0C0 (" + str(round(y.values[-1], 1)).replace(".", ",") + " %)",
        showlegend=True,
    )
)

fig.update_layout(
     title={
        'text': "Proportion de variants dans les tests positifs (en %)",
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
         'font': {'size': 30}
    },
    annotations = [
                    dict(
                        x=0.5,
                        y=1.1,
                        xref='paper',
                        yref='paper',
                        text='Mis à jour le {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(now.strftime('%d %B')),
                        showarrow = False
                    )]
)
fig.write_image(PATH+"images/charts/france/{}.jpeg".format("variants_pourcent"), scale=2, width=1000, height=600)


# In[8]:


fig = go.Figure()
n_days = 57 #len(df_variants)

pourcent=100-df_variants.tx_D1.values[-n_days:]
y2=df_tests["P_rolling"].values[-n_days:] * pourcent/100

fig.add_trace(
    go.Scatter(
        x=df_variants.jour[-n_days:],
        y=y2,
        name="<br>Autres,<br>dont <b>Delta </b><br>" + " (" + str(round(pourcent[-1], 1)).replace(".", ",") + " %) ",
        stackgroup='one',
        line=dict(width=0),
        fillcolor="rgba(153, 153, 153, 0.8)"
    )
)

pourcent= df_variants.tx_D1.values[-n_days:]
y1=df_tests["P_rolling"].values[-n_days:] * pourcent/100

fig.add_trace(
    go.Scatter(
        x=df_variants.jour[-n_days:],
        y=y1,
        name="<br>Mutations d'intérêts D1   *<br>dont <b>Omicron</b><br>" + " (" + str(round(pourcent[-1], 1)).replace(".", ",") + " %) ",
        stackgroup='one',
        line=dict(width=0),
        fillcolor="rgb(240, 31, 31)"
    )
)

pourcent=df_variants.tx_C1.values[-n_days:]
fig.add_trace(
    go.Scatter(
        x=df_variants.jour[-n_days:],
        y=y1+y2,
        name="Total cas positifs",
        line=dict(width=2, color="black")
    )
)


fig.update_yaxes(ticksuffix="")

fig.update_layout(
     title={
        'text': "Nombre de variants dans les cas détectés",
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
         'font': {'size': 30}
    },
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    annotations = [
                    dict(
                        x=0.57,
                        y=1.14,
                        xref='paper',
                        yref='paper',
                        text='Projection du taux de détection des mutations des tests de criblage sur les cas quotidiens.<br>Mis à jour : {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(now.strftime('%d %B')),
                        showarrow = False
                    ),
                    dict(
                        x=0.55,
                        y=-0.15,
                        xref='paper',
                        yref='paper',
                        text='(*) Mutations et délétions : DEL69/70, K417N, S371L-S373P et/ou Q493R',
                        showarrow = False
                    )]
)
fig.write_image(PATH+"images/charts/france/{}.jpeg".format("variants_nombre"), scale=2, width=1000, height=600)


# In[9]:


fig = go.Figure()
n_days = 57 #len(df_variants)

pourcent=100-df_variants.tx_A0C0.values[-n_days:]
y2=df_tests["P_rolling"].values[-n_days:] * pourcent/100

fig.add_trace(
    go.Scatter(
        x=df_variants.jour[-n_days:],
        y=y2,
        name="<br>Autres,<br>dont <b>Delta </b><br>" + " (" + str(round(pourcent[-1], 1)).replace(".", ",") + " %) ",
        stackgroup='one',
        line=dict(width=0),
        fillcolor="rgba(153, 153, 153, 0.8)"
    )
)

pourcent= df_variants.tx_A0C0.values[-n_days:]
y1=df_tests["P_rolling"].values[-n_days:] * pourcent/100

fig.add_trace(
    go.Scatter(
        x=df_variants.jour[-n_days:],
        y=y1,
        name="<br>Mutations d'intérêts A0C0*<br>dont <b>Omicron</b><br>" + " (" + str(round(pourcent[-1], 1)).replace(".", ",") + " %) ",
        stackgroup='one',
        line=dict(width=0),
        fillcolor="rgb(240, 31, 31)"
    )
)

fig.add_trace(
    go.Scatter(
        x=df_variants.jour[-n_days:],
        y=y1+y2,
        name="Total cas positifs",
        line=dict(width=2, color="black")
    )
)


fig.update_yaxes(ticksuffix="")

fig.update_layout(
     title={
        'text': "Nombre de variants dans les cas détectés",
        'y':0.99,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
         'font': {'size': 30}
    },
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    annotations = [
                    dict(
                        x=0.57,
                        y=1.14,
                        xref='paper',
                        yref='paper',
                        text='Projection du taux de détection des mutations des tests de criblage sur les cas quotidiens.<br>Mis à jour : {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(now.strftime('%d %B')),
                        showarrow = False
                    ),
                    dict(
                        x=0.55,
                        y=-0.15,
                        xref='paper',
                        yref='paper',
                        text='(*) Mutations A (E484K) et C (L452R) non présentes',
                        showarrow = False
                    )]
)
fig.write_image(PATH+"images/charts/france/{}.jpeg".format("variants_nombre_A0C0"), scale=2, width=1000, height=600)


# In[10]:


def export_data():
    n_days_export = 58
    dict_json = {}
    
    taux_d1 = df_variants.tx_D1.values[-n_days_export:]
    
    dict_json["jours"] = list(df_variants.jour[-n_days_export:])
    
    dict_json["cas_non_d1"] = list(np.round(df_tests["P_rolling"].values[-n_days_export:] * (100-taux_d1) / 100))
    dict_json["cas_d1"] = list(np.round(df_tests["P_rolling"].values[-n_days_export:] * (taux_d1) / 100))
    
    dict_json["taux_d1"] = taux_d1[-1]
    dict_json["cas"] = list(np.round(df_tests["P_rolling"].values[-n_days_export:]))
    
    with open(PATH_STATS + 'variants.json', 'w') as outfile:
        json.dump(dict_json, outfile)
        
export_data()

