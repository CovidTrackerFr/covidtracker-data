#!/usr/bin/env python
# coding: utf-8

# In[7]:


"""

LICENSE MIT
2020
Guillaume Rozier
Website : http://www.covidtracker.fr
Mail : guillaume.rozier@telecomnancy.net

README:
This file contains scripts that download data from data.gouv.fr and then process it to build many graphes.

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[8]:


import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta
import france_data_management as data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import plotly.figure_factory as ff
import plotly
PATH = "../../"
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
now = datetime.now()


# In[9]:


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
    
def traitement_val(valeur, plus_sign=False, couleur=False):
    if (int(valeur) > 0) & plus_sign:
        valeur = "+" + str(abs(int(valeur)))
        if couleur:
            valeur = " ↗" + valeur
        
    if ("+" not in valeur):
        if(int(valeur)<0):
            valeur = "-" + str(abs(int(valeur)))
            
            if couleur:
                valeur = " ↘" + valeur
        
    if len(valeur)>3:
        valeur = valeur[:len(valeur)-3] + " " + valeur[-3:]

    return valeur


# In[10]:


data.download_data()


# In[11]:


df_tests_viros = data.download_and_import_fra_jour_cage() #data.import_data_tests_sexe()


# In[26]:





# In[61]:


df_tests_viros_france = df_tests_viros.groupby(['jour', 'cl_age90']).sum().reset_index()
df_tests_rolling = pd.DataFrame()

array_positif= []
array_taux= []
array_depistage=[]
array_incidence=[]
for age in [0] + sorted(list(dict.fromkeys(list(df_tests_viros_france['cl_age90'].values)))):
    if age != -1:
        df_temp = pd.DataFrame()
        
        df_tests_viros_france_temp = df_tests_viros_france[df_tests_viros_france['cl_age90'] == age]
        
        if age==0:
            df_tests_viros_france_temp = df_tests_viros_france.groupby(["jour"]).sum().reset_index()
            
        df_temp['jour'] = df_tests_viros_france_temp['jour']
        df_temp['cl_age90'] = df_tests_viros_france_temp['cl_age90']
        df_temp['P'] = (df_tests_viros_france_temp['P']).rolling(window=7).mean()
        df_temp['T'] = (df_tests_viros_france_temp['T']).rolling(window=7).mean()
        df_temp['P_taux'] = (df_temp['P']/df_temp['T']*100)

        df_tests_rolling = pd.concat([df_tests_rolling, df_temp])
        df_tests_rolling.index = pd.to_datetime(df_tests_rolling["jour"])
        
        tranche = df_tests_viros_france_temp #df_tests_viros_france[df_tests_viros_france["cl_age90"]==age]
        tranche.index = pd.to_datetime(tranche["jour"])
        
        tranche = tranche[tranche.index.max() - timedelta(days=7*32-1):].resample('7D').sum()
        array_positif += [tranche["P"].astype(int)]
        array_depistage += [np.round(tranche["T"]/tranche["pop"]*7*100000,0).astype(int)]
        array_taux += [np.round(tranche["P"]/tranche["T"]*100, 1)]
        array_incidence += [np.round(tranche["P"]/tranche["pop"]*7*100000,0).astype(int)]

        dates_heatmap = list(tranche.index.astype(str).values)
df_tests_rolling = df_tests_rolling[df_tests_rolling['jour'] > "2020-05-18"]
df_tests_rolling['cl_age90'] = df_tests_rolling['cl_age90'].replace(90,99)

dates_heatmap_firstday = tranche.index.values
dates_heatmap_lastday = tranche.index + timedelta(days=6)
dates_heatmap = [str(dates_heatmap_firstday[i])[8:10] + "/" + str(dates_heatmap_firstday[i])[5:7] + "<br>" + str(dates_heatmap_lastday[i])[8:10] + "/" + str(dates_heatmap_lastday[i])[5:7] for i, val in enumerate(dates_heatmap_firstday)]


# In[63]:


for (name, array, title, scale_txt, data_example, digits) in [("cas", array_positif, "Nombre de <b>tests positifs</b>", "", "", 0), ("depistage", array_depistage, "Taux de <b>dépistage</b>", "", "", 0), ("taux", array_taux, "Taux de <b>positivité</b>", "%", "%", 1), ("incidence", array_incidence, "Taux d'<b>incidence</b>", " cas", " cas", 1)]: #
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    
    labels = ["<b>Tous âges</b>"] + [str(x-9) + " à " + str(x)+" ans" if x!=99 else "Plus 90 ans" for x in range(9, 109, 10)]
    for (idx, label) in enumerate(labels):
        value_old = array[idx][len(array[0])-2]
        value_new = array[idx][len(array[0])-1]
        taux_evolution = traitement_val(str(int(round((value_new - value_old) / value_old * 100))), plus_sign=True, couleur=True)
        labels[idx] += "<br>" + taux_evolution + " %"
        
    fig = ff.create_annotated_heatmap(
            z=array,
            x=dates_heatmap,
            y=labels,
            showscale=True,
            coloraxis="coloraxis",
            font_colors=["white", "white"],
            annotation_text = array
            )
    
    annot = []

    fig.update_xaxes(side="bottom", tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))
    annots = annot + [
                    dict(
                        x=0.5,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=10),
                        text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à droite) et à une date donnée (à lire en bas).<br>Du rouge correspond à un {} élevé.  <i>Date : {} - Source : <b>@GuillaumeRozier</b> covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ]
    
    fig.update_layout(coloraxis_colorbar_x=-0.15)
    fig['layout']['yaxis'].update(side='right')
    
    for i in range(len(fig.layout.annotations)):
        if(len(fig.layout.annotations[i].text)>4):
            fig.layout.annotations[i].text = nbWithSpaces(int(fig.layout.annotations[i].text))
            fig.layout.annotations[i].font.size = 7
        else:
            fig.layout.annotations[i].font.size = 10
        
    for annot in annots:
        fig.add_annotation(annot)
        
    if name == "incidence":
        cmax = 800
    elif name == "cas":
        cmax = 28000
    elif name == "taux":
        cmax = 18
        
    fig.update_layout(
        title={
            'text': "{} du Covid19 en fonction de l\'âge".format(title.replace("<br>", " ")),
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=20),
        coloraxis=dict(
            cmin=0, cmax=cmax,
            colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]],
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=8,
                lenmode="pixels", len=200,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(scale_txt),
                )
        ),
        
    margin=dict(
                    r=100,
                    l=0,
                    b=80,
                    t=40,
                    pad=0
                ))

    name_fig = "heatmap_"+name
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1300, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# ## Niveaux scolaires

# In[65]:


df_niveaux_scolaires = data.download_and_import_data_niveaux_scolaires_fra()


# In[ ]:


df_tests_rolling = pd.DataFrame()

array_taux_niveaux_scolaires= []
array_taux_depistage_niveaux_scolaires= []
array_incidence_niveaux_scolaires=[]
sorted_tranches = sorted(list(dict.fromkeys(list(df_niveaux_scolaires['age_18ans'].astype(int).values))))
for age in sorted_tranches:
    if age != -1:
        df_temp = pd.DataFrame()
        df_niveaux_scolaires_temp = df_niveaux_scolaires[df_niveaux_scolaires['age_18ans'] == str(age)]
        tranche = df_niveaux_scolaires_temp
        tranche.index = pd.to_datetime(tranche["jour"])
        tranche = tranche[tranche.index.max() - timedelta(days=7*32-1):].resample('7D').last()
        array_taux_depistage_niveaux_scolaires += [np.round(tranche["Td"], 0)]
        array_taux_niveaux_scolaires += [np.round(tranche["Tp"], 1)]
        array_incidence_niveaux_scolaires += [np.round(tranche["Ti"], 0).astype(int)]
        dates_heatmap = list(tranche.index.astype(str).values)
        

dates_heatmap_firstday = tranche.index.values
dates_heatmap_lastday = tranche.index + timedelta(days=6)
dates_heatmap = [str(dates_heatmap_firstday[i])[8:10] + "/" + str(dates_heatmap_firstday[i])[5:7] + "<br>" + str(dates_heatmap_lastday[i])[8:10] + "/" + str(dates_heatmap_lastday[i])[5:7] for i, val in enumerate(dates_heatmap_firstday)]


# In[ ]:


for (name, array, title, scale_txt, data_example, digits) in [("depistage", array_taux_depistage_niveaux_scolaires, "Taux de <b>dépistage</b>", " tests", " tests", 1), ("taux", array_taux_niveaux_scolaires, "Taux de <b>positivité</b>", "%", "%", 1), ("incidence", array_incidence_niveaux_scolaires, "Taux d'<b>incidence</b>", " cas", " cas", 1)]: #
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    
    labels = [" <b>Tous âges</b>", " <b>0 - 2 ans</b>", " <b>3 - 5 ans</b>", " <b>6 - 10 ans</b>", " <b>11 - 14 ans</b>", " <b>15 - 17 ans</b>", " <b>Plus 18 ans</b>"]
    for (idx, label) in enumerate(labels):
        value_old = array[idx][len(array[0])-2]
        value_new = array[idx][len(array[0])-1]
        taux_evolution = traitement_val(str(int(round((value_new - value_old) / value_old * 100))), plus_sign=True, couleur=True)
        labels[idx] += "<br>" + taux_evolution + " %"
        
    fig = ff.create_annotated_heatmap(
            z=array,
            x=dates_heatmap,
            y=labels,
            showscale=True,
            coloraxis="coloraxis",
            font_colors=["white", "white"],
            annotation_text = array
            )
    
    annot = []

    fig.update_xaxes(side="bottom", tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))
    annots = annot + [
                    dict(
                        x=0.5,
                        y=-0.16,
                        xref='paper',
                        yref='paper',
                        xanchor='center',
                        opacity=0.6,
                        font=dict(color="black", size=10),
                        text='Lecture : une case correspond au {} pour une tranche d\'âge (à lire à droite) et à une date donnée (à lire en bas).<br>Du rouge correspond à un {} élevé.  <i>Date : {} - Source : <b>@GuillaumeRozier</b> covidtracker.fr - Données : Santé publique France</i>'.format(title.lower().replace("<br>", " "), title.lower().replace("<br>", " "), now.strftime('%d %B')),
                        showarrow = False
                    ),
                ]
    
    fig.update_layout(coloraxis_colorbar_x=-0.15)
    fig['layout']['yaxis'].update(side='right')
    
    for i in range(len(fig.layout.annotations)):
        if(len(fig.layout.annotations[i].text)>4):
            fig.layout.annotations[i].text = nbWithSpaces(float(fig.layout.annotations[i].text))
            fig.layout.annotations[i].font.size = 7
        else:
            fig.layout.annotations[i].font.size = 10
        
    for annot in annots:
        fig.add_annotation(annot)
        
    if name == "incidence":
        cmax = 800
    elif name == "cas":
        cmax = 28000
    elif name == "taux":
        cmax = 18
    elif name == "depistage":
        cmax = 10000
        
    fig.update_layout(
        title={
            'text': "{} du Covid19 en fonction de l\'âge".format(title.replace("<br>", " ")),
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            titlefont = dict(
            size=20),
        coloraxis=dict(
            cmin=0, cmax=cmax,
            colorscale = [[0, "green"], [0.08, "#ffcc66"], [0.25, "#f50000"], [0.5, "#b30000"], [1, "#3d0000"]],
            colorbar=dict(
                #title="{}<br>du Covid19<br> &#8205;".format(title),
                thicknessmode="pixels", thickness=8,
                lenmode="pixels", len=200,
                yanchor="middle", y=0.5,
                tickfont=dict(size=9),
                ticks="outside", ticksuffix="{}".format(scale_txt),
                )
        ),
        
    margin=dict(
                    r=100,
                    l=0,
                    b=80,
                    t=40,
                    pad=0
                ))

    name_fig = "heatmap_"+name+"_niveaux_scolaires"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=3, width=1300, height=550)
    #fig.show()
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)

