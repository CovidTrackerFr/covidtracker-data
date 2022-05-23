#!/usr/bin/env python
# coding: utf-8

# """
# 
# LICENSE MIT
# 2020
# Guillaume Rozier
# Website : http://www.covidtracker.fr
# Mail : guillaume.rozier@telecomnancy.net
# 
# README:
# This file contains scripts that download data from data.gouv.fr and then process it to build many graphes.
# 
# The charts are exported to 'charts/images/france'.
# Data is download to/imported from 'data/france'.
# Requirements: please see the imports below (use pip3 to install them).
# 
# """

# In[1]:


import pandas as pd
import plotly.express as px
from datetime import timedelta
import france_data_management as data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import plotly
import cv2
import numpy as np
PATH = "../../"
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[2]:


COULEUR_NON_VACCINES = "#C65102"
COULEUR_COMPLETEMENT_VACCINES = "#00308F"
COULEUR_COMPLETEMENT_VACCINES_RAPPEL = "black"
COULEUR_PARTIELLEMENT_VACCINES = "#4777d6"


# In[3]:


df_drees = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-issus-des-appariements-entre-si-vic-si-dep-et-vac-si/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
#df_drees = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-anciens-resultats-nationaux-issus-des-appariements-entre-si-vic-si-dep-/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
#df_drees = df_drees[df_drees["date"]<="2021-09-26"] #TODO SUPPR

df_drees = df_drees.sort_values(by="date")
df_drees = df_drees[df_drees["vac_statut"]!="Ensemble"]


# In[4]:


df_drees_age = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-par-age-issus-des-appariements-entre-si-vic-si-dep-et-vac-si/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")

df_drees_age_all = df_drees_age.groupby(["date", "vac_statut", "age"]).sum().reset_index()
df_drees_age = df_drees_age.sort_values(by="date")
df_drees_age = df_drees_age[df_drees_age["vac_statut"]!="Ensemble"]
df_drees_age_lastday = df_drees_age[df_drees_age["date"] == df_drees_age["date"].max()]

df_drees_age["HC_PCR+_Omicron"] = df_drees_age["HC_PCR+"] * df_drees_age["HC_pourcent_omicron"]/100
df_drees_age["HC_PCR+_Delta"] = df_drees_age["HC_PCR+"] * (100-df_drees_age["HC_pourcent_omicron"])/100

df_drees_age["SC_PCR+_Omicron"] = df_drees_age["SC_PCR+"] * df_drees_age["SC_pourcent_omicron"]/100
df_drees_age["SC_PCR+_Delta"] = df_drees_age["SC_PCR+"] * (100-df_drees_age["SC_pourcent_omicron"])/100

df_drees_age["DC_PCR+_Omicron"] = df_drees_age["DC_PCR+"] * df_drees_age["DC_pourcent_omicron"]/100
df_drees_age["DC_PCR+_Delta"] = df_drees_age["DC_PCR+"] * (100-df_drees_age["DC_pourcent_omicron"])/100


# In[5]:


df_drees_non_vaccines = df_drees[df_drees["vac_statut"]=="Non-vaccinés"]
df_drees_non_vaccines["effectif"] = df_drees_non_vaccines["effectif"].rolling(window=7).mean()

df_drees_completement_vaccines = df_drees[df_drees["vac_statut"].isin(["Complet de moins de 3 mois - sans rappel", "Complet entre 3 mois et 6 mois - sans rappel", "Complet de 6 mois et plus - sans rappel"])].groupby("date").sum().reset_index()
df_drees_completement_vaccines["effectif"] = df_drees_completement_vaccines["effectif"].rolling(window=7).mean()

df_drees_completement_vaccines_rappel = df_drees[df_drees["vac_statut"].isin(["Complet - avec rappel de moins de 3 mois", "Complet - avec rappel entre 3 mois et 6 mois", "Complet - avec rappel de 6 mois ou plus"])].groupby("date").sum().reset_index()
df_drees_completement_vaccines_rappel["effectif"] = df_drees_completement_vaccines_rappel["effectif"].rolling(window=7).mean()

df_drees_partiellement_vaccines = df_drees[df_drees["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
df_drees_partiellement_vaccines["effectif"] = df_drees_partiellement_vaccines["effectif"].rolling(window=7).mean()

#df_drees_ensemble = df_drees[df_drees["vac_statut"]=="Ensemble"]
df_drees_ensemble = df_drees.groupby("date").sum().reset_index()


# In[33]:


def get_df_by_vaccine_status(df):
    df_drees_non_vaccines = df[df["vac_statut"]=="Non-vaccinés"]
    df_drees_non_vaccines["effectif"] = df_drees_non_vaccines["effectif"].rolling(window=7).mean()

    df_drees_completement_vaccines = df[df["vac_statut"].isin(["Complet de moins de 3 mois - sans rappel", "Complet entre 3 mois et 6 mois - sans rappel", "Complet de 6 mois et plus - sans rappel"])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines["effectif"] = df_drees_completement_vaccines["effectif"].rolling(window=7).mean()

    df_drees_completement_vaccines_rappel = df[df["vac_statut"].isin(["Complet - avec rappel de moins de 3 mois", "Complet - avec rappel entre 3 mois et 6 mois", "Complet - avec rappel de 6 mois ou plus"])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines_rappel["effectif"] = df_drees_completement_vaccines_rappel["effectif"].rolling(window=7).mean()

    df_drees_partiellement_vaccines = df[df["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
    df_drees_partiellement_vaccines["effectif"] = df_drees_partiellement_vaccines["effectif"].rolling(window=7).mean()

    df_drees_ensemble = df.groupby("date").sum().reset_index()
    
    return df_drees_non_vaccines, df_drees_completement_vaccines, df_drees_completement_vaccines_rappel, df_drees_partiellement_vaccines, df_drees_ensemble

def get_df_by_vaccine_status_detailed(df):
    
    df_drees_completement_vaccines_rappel_moins_3_mois = df[df["vac_statut"]=="Complet - avec rappel de moins de 3 mois"].groupby("date").sum().reset_index()
    df_drees_completement_vaccines_rappel_moins_3_mois["effectif"] = df_drees_completement_vaccines_rappel_moins_3_mois["effectif"].rolling(window=7).mean()
    
    df_drees_completement_vaccines_rappel_3_6_mois = df[df["vac_statut"]=="Complet - avec rappel entre 3 mois et 6 mois"].groupby("date").sum().reset_index()
    df_drees_completement_vaccines_rappel_3_6_mois["effectif"] = df_drees_completement_vaccines_rappel_3_6_mois["effectif"].rolling(window=7).mean()
    
    df_drees_completement_vaccines_rappel_moins_plus_6_mois = df[df["vac_statut"]=="Complet - avec rappel de 6 mois ou plus"].groupby("date").sum().reset_index()
    df_drees_completement_vaccines_rappel_moins_plus_6_mois["effectif"] = df_drees_completement_vaccines_rappel_moins_plus_6_mois["effectif"].rolling(window=7).mean()
    
    return df_drees_completement_vaccines_rappel_moins_3_mois, df_drees_completement_vaccines_rappel_3_6_mois, df_drees_completement_vaccines_rappel_moins_plus_6_mois
    


# In[34]:


df_drees_20plus = df_drees_age[df_drees_age["age"]!="[0,19]"].groupby(["date", "vac_statut"]).sum().reset_index()
df_drees_non_vaccines_20plus, df_drees_completement_vaccines_20plus, df_drees_completement_vaccines_rappel_20plus, df_drees_partiellement_vaccines_20plus, _ = get_df_by_vaccine_status(df_drees_20plus)
df_drees_completement_vaccines_rappel_20plus_moins_3_mois, df_drees_completement_vaccines_rappel_20plus_3_6_mois, df_drees_completement_vaccines_rappel_20plus_plus_6_mois = get_df_by_vaccine_status_detailed(df_drees_20plus)


# In[35]:


fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages = np.delete(ages, np.where(ages == '[0,19]'))

ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]
    
y_non_vaccines=[]
y_non_vaccines_up=[]
y_non_vaccines_down=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["HC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["HC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_non_vaccines_up += [error]
    y_non_vaccines_down += [error]
    
y_partiellement_vaccines=[]
y_partiellement_vaccines_up=[]
y_partiellement_vaccines_down=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["HC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["HC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_partiellement_vaccines_up += [error]
    y_partiellement_vaccines_down += [error]
    
y_completement_vaccines=[]
y_completement_vaccines_up=[]
y_completement_vaccines_down=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["HC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["HC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_completement_vaccines_up += [error]
    y_completement_vaccines_down += [error]
    
y_vaccines_rappel=[]
y_vaccines_rappel_up=[]
y_vaccines_rappel_down=[]
for age in ages:
    _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_vaccines_rappel+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["HC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["HC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_vaccines_rappel_up += [error]
    y_vaccines_rappel_down += [error]
    
text_non_vaccines = []
text_completement_vaccines = []
text_partiellement_vaccines=[]
text_vaccines_rappel = []
for idx, age in enumerate(ages):
    text_non_vaccines += ["<b>" + str(int(round(y_non_vaccines[idx]))) + "</b><br>(x" + str(round(y_non_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
    text_completement_vaccines += ["<b>" + str(int(round(y_completement_vaccines[idx]))) + "</b><br>(x" + str(round(y_completement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
    text_partiellement_vaccines += ["<b>" + str(int(round(y_partiellement_vaccines[idx]))) + "</b><br>(x" + str(round(y_partiellement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
    text_vaccines_rappel += ["<b>" + str(int(round(y_vaccines_rappel[idx]))) + "</b><br>(x" + str(round(y_vaccines_rappel[idx] / y_vaccines_rappel[idx])) + ")"]


fig.add_trace(go.Bar(
    x=ages_str,
    y=y_non_vaccines,
    marker=dict(color=COULEUR_NON_VACCINES),
    error_y=dict(type='data', symmetric=False, array=y_non_vaccines_up, arrayminus=y_non_vaccines_down, thickness=0.7, color="grey"),
    text=text_non_vaccines,
    textposition='outside',
    name="Non vaccinés"
))

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_partiellement_vaccines,
    marker=dict(color=COULEUR_PARTIELLEMENT_VACCINES),
    error_y=dict(type='data', symmetric=False, array=y_partiellement_vaccines_up, arrayminus=y_partiellement_vaccines_down, thickness=0.7, color="grey"),
    text=text_partiellement_vaccines,
    textposition='outside',
    name="Partiellement vaccinés")
             )

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_completement_vaccines,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    error_y=dict(type='data', symmetric=False, array=y_completement_vaccines_up, arrayminus=y_completement_vaccines_down, thickness=0.7, color="grey"),
    text=text_completement_vaccines,
    textposition='outside',
    name="Totalement vaccinés"
))

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_vaccines_rappel,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
    error_y=dict(type='data', symmetric=False, array=y_vaccines_rappel_up, arrayminus=y_vaccines_rappel_down, thickness=0.7, color="grey"),
    text=text_vaccines_rappel,
    textposition='outside',
    name="Totalement vaccinés (avec rappel)"
))
    
fig.update_layout(
    barmode="group", bargroupgap=0,
    title={
                        'text': "<b>Admissions à l'hôpital</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal et l'âge, pour 10 Mio hab. de chaque groupe - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                 )

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Admissions à l'hôpital pour 10 Mio", range=[0, max(y_non_vaccines)*1.1])
fig.update_xaxes(title="Âge")
name_fig = "hc_statut_vaccinal_age"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[36]:


for variant in ["Delta", "Omicron"]:
    fig = go.Figure()
    ages=df_drees_age_lastday.age.sort_values().unique()
    ages = np.delete(ages, np.where(ages == '[0,19]'))

    ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

    y_non_vaccines=[]
    for age in ages:
        data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_non_vaccines+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]/data["effectif"].fillna(1).values[-1]*10000000]

    y_partiellement_vaccines=[]
    for age in ages:
        _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_partiellement_vaccines+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]/data["effectif"].fillna(1).values[-1]*10000000]

    y_completement_vaccines=[]
    for age in ages:
        _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_completement_vaccines+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]/data["effectif"].fillna(1).values[-1]*10000000]

    y_vaccines_rappel=[]
    for age in ages:
        _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_vaccines_rappel+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]/data["effectif"].fillna(1).values[-1]*10000000]

    text_non_vaccines = []
    text_completement_vaccines = []
    text_partiellement_vaccines=[]
    text_vaccines_rappel = []
    for idx, age in enumerate(ages):
        text_non_vaccines += ["<b>" + str(int(round(y_non_vaccines[idx]))) + "</b><br>(x" + str(round(y_non_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_completement_vaccines += ["<b>" + str(int(round(y_completement_vaccines[idx]))) + "</b><br>(x" + str(round(y_completement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_partiellement_vaccines += ["<b>" + str(int(round(y_partiellement_vaccines[idx]))) + "</b><br>(x" + str(round(y_partiellement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_vaccines_rappel += ["<b>" + str(int(round(y_vaccines_rappel[idx]))) + "</b><br>(x" + str(round(y_vaccines_rappel[idx] / y_vaccines_rappel[idx])) + ")"]


    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_non_vaccines,
        marker=dict(color=COULEUR_NON_VACCINES),
        text=text_non_vaccines,
        textposition='outside',
        name="Non vaccinés"
    ))

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_completement_vaccines,
        marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        text=text_completement_vaccines,
        textposition='outside',
        name="Totalement vaccinés"
    ))

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_vaccines_rappel,
        marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
        text=text_vaccines_rappel,
        textposition='outside',
        name="Totalement vaccinés (avec rappel)"
    ))

    fig.update_layout(
        barmode="group", bargroupgap=0,
        title={
                            'text': f"<b>Admissions à l'hôpital</b> Covid [{variant} uniquement]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.5,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal et l'âge, pour 10 Mio hab. de chaque groupe - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
                     )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions pour suspicion Covid19.</i>",
        font=dict(size=9),
        showarrow=False,
        yshift=30,
        xshift=0
    )

    fig.update_yaxes(title="Admissions à l'hôpital pour 10 Mio", range=[0, max(y_non_vaccines)*1.1])
    fig.update_xaxes(title="Âge")
    name_fig = f"hc_statut_vaccinal_age_{variant}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[37]:


"""for variant in ["Delta", "Omicron"]:
    fig = go.Figure()
    ages=df_drees_age_lastday.age.sort_values().unique()
    ages = np.delete(ages, np.where(ages == '[0,19]'))

    ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

    y_non_vaccines=[]
    for age in ages:
        data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_non_vaccines+=[data[f"SC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]/data["effectif"].values[-1]*10000000]

    y_partiellement_vaccines=[]
    for age in ages:
        _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_partiellement_vaccines+=[data[f"SC_PCR+_{variant}"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

    y_completement_vaccines=[]
    for age in ages:
        _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_completement_vaccines+=[data[f"SC_PCR+_{variant}"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

    y_vaccines_rappel=[]
    for age in ages:
        _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_vaccines_rappel+=[data[f"SC_PCR+_{variant}"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

    text_non_vaccines = []
    text_completement_vaccines = []
    text_partiellement_vaccines=[]
    text_vaccines_rappel = []
    for idx, age in enumerate(ages):
        text_non_vaccines += ["<b>" + str(int(round(y_non_vaccines[idx]))) + "</b><br>(x" + str(round(y_non_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_completement_vaccines += ["<b>" + str(int(round(y_completement_vaccines[idx]))) + "</b><br>(x" + str(round(y_completement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_partiellement_vaccines += ["<b>" + str(int(round(y_partiellement_vaccines[idx]))) + "</b><br>(x" + str(round(y_partiellement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_vaccines_rappel += ["<b>" + str(int(round(y_vaccines_rappel[idx]))) + "</b><br>(x" + str(round(y_vaccines_rappel[idx] / y_vaccines_rappel[idx])) + ")"]


    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_non_vaccines,
        marker=dict(color=COULEUR_NON_VACCINES),
        text=text_non_vaccines,
        textposition='outside',
        name="Non vaccinés"
    ))

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_completement_vaccines,
        marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        text=text_completement_vaccines,
        textposition='outside',
        name="Totalement vaccinés"
    ))

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_vaccines_rappel,
        marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
        text=text_vaccines_rappel,
        textposition='outside',
        name="Totalement vaccinés (avec rappel)"
    ))

    fig.update_layout(
        barmode="group", bargroupgap=0,
        title={
                            'text': f"<b>Admissions en soins critiques</b> Covid [{variant} uniquement]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.5,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal et l'âge, pour 10 Mio hab. de chaque groupe - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
                     )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions en soins critiques avec test positif Covid19.</i>",
        font=dict(size=9),
        showarrow=False,
        yshift=30,
        xshift=0
    )

    fig.update_yaxes(title="Admissions en soins critiques pour 10 Mio", range=[0, 300])
    fig.update_xaxes(title="Âge")
    name_fig = f"sc_statut_vaccinal_age_{variant}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)"""


# In[38]:


import cv2
import numpy as np
PATH = "../../"

im1 = cv2.imread(PATH+'images/charts/france/sc_statut_vaccinal_age_Delta.jpeg')
im2 = cv2.imread(PATH+'images/charts/france/sc_statut_vaccinal_age_Omicron.jpeg')

imc = cv2.vconcat([im1, im2])
cv2.imwrite(PATH+'images/charts/france/sc_statut_vaccinal_age_Delta_Omicron.jpeg', imc)


# In[39]:


df_temp = df_drees_age[["date", "age", "vac_statut", "HC_PCR+", "HC_pourcent_omicron", "HC_PCR+_Omicron", "effectif"]]
df_temp = df_temp[df_temp["age"]==ages[-1]]
df_temp = df_temp[df_temp["date"]==df_drees_age["date"].max()]
df_temp


# In[40]:


for variant in ["Delta", "Omicron"]:
    fig = go.Figure()
    ages=df_drees_age_lastday.age.sort_values().unique()
    ages = np.delete(ages, np.where(ages == '[0,19]'))

    ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

    y_non_vaccines=[]
    for age in ages:
        data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_non_vaccines+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]]

    y_partiellement_vaccines=[]
    for age in ages:
        _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_partiellement_vaccines+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]]

    y_completement_vaccines=[]
    for age in ages:
        _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_completement_vaccines+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]]

    y_vaccines_rappel=[]
    for age in ages:
        _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
        y_vaccines_rappel+=[data[f"HC_PCR+_{variant}"].rolling(window=7).mean().fillna(0).values[-1]]

    text_non_vaccines = []
    text_completement_vaccines = []
    text_partiellement_vaccines=[]
    text_vaccines_rappel = []
    for idx, age in enumerate(ages):
        text_non_vaccines += ["<b>" + str(int(round(y_non_vaccines[idx]))) + "</b><br>(x" + str(round(y_non_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_completement_vaccines += ["<b>" + str(int(round(y_completement_vaccines[idx]))) + "</b><br>(x" + str(round(y_completement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_partiellement_vaccines += ["<b>" + str(int(round(y_partiellement_vaccines[idx]))) + "</b><br>(x" + str(round(y_partiellement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
        text_vaccines_rappel += ["<b>" + str(int(round(y_vaccines_rappel[idx]))) + "</b><br>(x" + str(round(y_vaccines_rappel[idx] / y_vaccines_rappel[idx])) + ")"]


    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_non_vaccines,
        marker=dict(color=COULEUR_NON_VACCINES),
        text=text_non_vaccines,
        textposition='outside',
        name="Non vaccinés"
    ))

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_partiellement_vaccines,
        marker=dict(color=COULEUR_PARTIELLEMENT_VACCINES),
        text=text_partiellement_vaccines,
        textposition='outside',
        name="Partiellement vaccinés")
                 )

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_completement_vaccines,
        marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        text=text_completement_vaccines,
        textposition='outside',
        name="Totalement vaccinés"
    ))

    fig.add_trace(go.Bar(
        x=ages_str,
        y=y_vaccines_rappel,
        marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
        text=text_vaccines_rappel,
        textposition='outside',
        name="Totalement vaccinés (avec rappel)"
    ))

    fig.update_layout(
        barmode="group", bargroupgap=0,
        title={
                            'text': f"<b>Admissions à l'hôpital</b> Covid [{variant} uniquement]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.5,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal et l'âge, pour 10 Mio hab. de chaque groupe - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
                     )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions pour suspicion Covid19.</i>",
        font=dict(size=9),
        showarrow=False,
        yshift=30,
        xshift=0
    )

    fig.update_yaxes(title="Admissions à l'hôpital pour 10 Mio", range=[0, max(y_non_vaccines)*1.1])
    fig.update_xaxes(title="Âge")
    name_fig = f"hc_statut_vaccinal_age_{variant}_absolu"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[41]:


import numpy as np

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y_non_vaccines=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_partiellement_vaccines=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_completement_vaccines=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["HC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y=(np.array(y_non_vaccines)-np.array(y_completement_vaccines))/np.array(y_non_vaccines)
fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    text=[str(int(round(val*100)))+" %" for val in y],
    textposition='inside',
    textfont=dict(size=16),
    name="Totalement vaccinés",
    showlegend=False
))
y=(np.array(y_non_vaccines)-np.array(y_completement_vaccines))/np.array(y_non_vaccines)
fig.add_trace(go.Bar(
    x=ages_str,
    y=1-y,
    marker=dict(color="grey"),
    showlegend=False
   
))
    
fig.update_layout(
    barmode="stack", bargroupgap=0,
    title={
                        'text': "<b>Réduction du taux d'admissions à l'hôpital</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="chez les vaccinés par rapport aux non vaccinés, selon l'âge - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                 )

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Réduction du taux d'admissions à l'hôpital", tickformat="%", range=[0,1])
fig.update_xaxes(title="Âge", tickfont=dict(size=16))
name_fig = "hc_statut_vaccinal_age_diminution_risque"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[42]:


import numpy as np

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y_non_vaccines=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_partiellement_vaccines=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_completement_vaccines=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y=(np.array(y_non_vaccines)-np.array(y_completement_vaccines))/np.array(y_non_vaccines)
fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    text=[str(int(round(val*100)))+" %" for val in y],
    textposition='inside',
    textfont=dict(size=16),
    name="Totalement vaccinés",
    showlegend=False
))
y=(np.array(y_non_vaccines)-np.array(y_completement_vaccines))/np.array(y_non_vaccines)
fig.add_trace(go.Bar(
    x=ages_str,
    y=1-y,
    marker=dict(color="grey"),
    showlegend=False
   
))
    
fig.update_layout(
    barmode="stack", bargroupgap=0,
    title={
                        'text': "<b>Réduction du taux d'admissions en soins critiques</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="chez les vaccinés par rapport aux non vaccinés, selon l'âge - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                 )

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Réduction du taux d'admissions en soins critiques", tickformat="%", range=[0,1])
fig.update_xaxes(title="Âge", tickfont=dict(size=16))
name_fig = "sc_statut_vaccinal_age_diminution_risque"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[43]:


import ast 

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages = np.delete(ages, np.where(ages == '[0,19]'))
ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y_vaccines_rappel=[]
y_vaccines_rappel_up=[]
y_vaccines_rappel_down=[]
for age in ages:
    _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_vaccines_rappel+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["SC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["SC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_vaccines_rappel_up += [error]
    y_vaccines_rappel_down += [error]
    
y_non_vaccines=[]
y_non_vaccines_up=[]
y_non_vaccines_down=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["SC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["SC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    y_non_vaccines_up += [error]
    y_non_vaccines_down += [error]
    
    
y_partiellement_vaccines=[]
y_partiellement_vaccines_up=[]
y_partiellement_vaccines_down=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
    sigma = (data["SC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["SC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_partiellement_vaccines_up += [error]
    y_partiellement_vaccines_down += [error]
    
y_completement_vaccines=[]
y_completement_vaccines_up=[]
y_completement_vaccines_down=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["SC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
   
    sigma = (data["SC_PCR+"]/data["effectif"].values[-1]*10000000).rolling(window=7).std().values[-1]
    cum = data["SC_PCR+"].rolling(window=7).sum().values[-1]
    error = 1.96 * sigma / (cum)**(1/2)
    
    y_completement_vaccines_up += [error]
    y_completement_vaccines_down += [error]
    
text_non_vaccines = []
text_completement_vaccines = []
text_partiellement_vaccines=[]
text_vaccines_rappel = []
for idx, age in enumerate(ages):
    text_non_vaccines += ["<b>" + str(int(round(y_non_vaccines[idx]))) + "</b><br>(x" + str(round(y_non_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
    text_completement_vaccines += ["<b>" + str(int(round(y_completement_vaccines[idx]))) + "</b><br>(x" + str(round(y_completement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
    text_partiellement_vaccines += ["<b>" + str(int(round(y_partiellement_vaccines[idx]))) + "</b><br>(x" + str(round(y_partiellement_vaccines[idx] / y_vaccines_rappel[idx])) + ")"]
    text_vaccines_rappel += ["<b>" + str(int(round(y_vaccines_rappel[idx]))) + "</b><br>(x" + str(round(y_vaccines_rappel[idx] / y_vaccines_rappel[idx])) + ")"]

    
fig.add_trace(go.Bar(
    x=ages_str,
    y=y_non_vaccines,
    error_y=dict(type='data', symmetric=False, array=y_non_vaccines_up, arrayminus=y_non_vaccines_down, thickness=0.7, color="grey"),
    marker=dict(color=COULEUR_NON_VACCINES),
    text=text_non_vaccines,
    textposition='outside',
    name="Non vaccinés"
))

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_partiellement_vaccines,
    marker=dict(color=COULEUR_PARTIELLEMENT_VACCINES),
    error_y=dict(type='data', symmetric=False, array=y_partiellement_vaccines_up, arrayminus=y_partiellement_vaccines_down, thickness=0.7, color="grey"),
    text=text_partiellement_vaccines,
    textposition='outside',
    name="Partiellement vaccinés")
             )

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_completement_vaccines,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    error_y=dict(type='data', symmetric=False, array=y_completement_vaccines_up, arrayminus=y_completement_vaccines_down, thickness=0.7, color="grey"),
    text= text_completement_vaccines,
    textposition='outside',
    name="Totalement vaccinés"
))



fig.add_trace(go.Bar(
    x=ages_str,
    y=y_vaccines_rappel,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
    error_y=dict(type='data', symmetric=False, array=y_vaccines_rappel_up, arrayminus=y_vaccines_rappel_down, thickness=0.7, color="grey"),
    text=text_vaccines_rappel,
    textposition='outside',
    name="Totalement vaccinés (avec rappel)"
))
    
fig.update_layout(
    barmode="group", bargroupgap=0,
    title={
                        'text': "<b>Admissions en soins critiques</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal et l'âge, pour 10 Mio hab. de chaque groupe - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                 )

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Admissions en soins critiques pour 10 Mio", range=[0, max(y_non_vaccines)*1.1])
fig.update_xaxes(title="Âge")
name_fig = "sc_statut_vaccinal_age"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#fig.show()


# In[44]:


import ast 

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages = np.delete(ages, np.where(ages == '[0,19]'))
ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y_non_vaccines=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["DC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
y_partiellement_vaccines=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["DC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
y_completement_vaccines=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["DC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
y_vaccines_rappel=[]
for age in ages:
    _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_vaccines_rappel+=[data["DC_PCR+"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]
    
text_non_vaccines = []
text_completement_vaccines = []
text_partiellement_vaccines=[]
text_vaccines_rappel = []
for idx, age in enumerate(ages):
    y_vaccines_rappel_idx=y_vaccines_rappel[idx]
    if y_vaccines_rappel_idx == 0:
        y_vaccines_rappel_idx = 1
    
    text_non_vaccines += ["<b>" + str(int(round(y_non_vaccines[idx]))) + "</b><br>(x" + str(round(y_non_vaccines[idx] / y_vaccines_rappel_idx)) + ")"]
    text_completement_vaccines += ["<b>" + str(int(round(y_completement_vaccines[idx]))) + "</b><br>(x" + str(round(y_completement_vaccines[idx] / y_vaccines_rappel_idx)) + ")"]
    text_partiellement_vaccines += ["<b>" + str(int(round(y_partiellement_vaccines[idx]))) + "</b><br>(x" + str(round(y_partiellement_vaccines[idx] / y_vaccines_rappel_idx)) + ")"]
    text_vaccines_rappel += ["<b>" + str(int(round(y_vaccines_rappel[idx]))) + "</b><br>(x" + str(round(y_vaccines_rappel[idx] / y_vaccines_rappel_idx)) + ")"]


fig.add_trace(go.Bar(
    x=ages_str,
    y=y_non_vaccines,
    marker=dict(color=COULEUR_NON_VACCINES),
    text=text_non_vaccines,
    textposition='outside',
    name="Non vaccinés"
))

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_partiellement_vaccines,
    marker=dict(color=COULEUR_PARTIELLEMENT_VACCINES),
    text=text_partiellement_vaccines,
    textposition='outside',
    name="Partiellement vaccinés")
             )

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_completement_vaccines,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    text=text_completement_vaccines,
    textposition='outside',
    name="Totalement vaccinés"
))

fig.add_trace(go.Bar(
    x=ages_str,
    y=y_vaccines_rappel,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
    text=text_vaccines_rappel,
    textposition='outside',
    name="Totalement vaccinés (avec rappel)"
))

fig.update_layout(
    barmode="group", bargroupgap=0,
    title={
                        'text': "<b>Décès hospitaliers</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal et l'âge, pour 10 Mio hab. de chaque groupe - {} (moyenne semaine)<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                 )

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Décès avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Décès hospitaliers pour 10 Mio", range=[0, max(y_non_vaccines) * 1.1])
fig.update_xaxes(title="Âge")
name_fig = "dc_statut_vaccinal_age"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#fig.show()


# In[45]:


locale.setlocale(locale.LC_TIME, 'fr_FR')
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)
fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "<b>Cas positifs</b> Covid symptomatiques",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_drees_non_vaccines["nb_PCR+_sympt"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas sympto.<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    align="left",
    xshift=95,
    yshift=100
)
y=df_drees_completement_vaccines["nb_PCR+_sympt"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas sympto.<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=50,
    xshift=95
)

y=df_drees_completement_vaccines_rappel["nb_PCR+_sympt"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas sympto.<br>vaccinés (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=105
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Cas pos. sympt. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "pcr_plus_sympt_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[46]:


locale.setlocale(locale.LC_TIME, 'fr_FR')
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "<b>Cas positifs</b> Covid",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000
text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} cas positifs<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} cas positifs<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} cas positifs<br>vaccinés (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)


fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Cas positifs / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "pcr_plus_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[47]:


locale.setlocale(locale.LC_TIME, 'fr_FR')
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["nb_PCR"].rolling(window=7).mean() * 100,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["nb_PCR"].rolling(window=7).mean()).values[-1]  * 100],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["nb_PCR"].rolling(window=7).mean() * 100,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["nb_PCR"].rolling(window=7).mean()).values[-1] * 100],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["nb_PCR"].rolling(window=7).mean() * 100,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["nb_PCR"].rolling(window=7).mean()).values[-1] * 100],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)

fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "<b>Taux de positivité des tests</b> Covid",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="proportion de cas positifs, selon le statut vaccinal - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["nb_PCR"].rolling(window=7).mean().values[-1]*100
y_vaccines=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["nb_PCR"].rolling(window=7).mean().values[-1]*100
y_vaccines_rappel=df_drees_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["nb_PCR"].rolling(window=7).mean().values[-1]*100
text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str((round(y_non_vaccines,1)))} % PCR positifs<br>non vaccinés</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str((round(y_vaccines,1)))} % PCR positifs<br>vaccinés</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str((round(y_vaccines_rappel,1)))} % PCR positifs<br>vaccinés (rappel)</b></span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)


fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Cas positifs / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "taux_pcr_plus_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[48]:


locale.setlocale(locale.LC_TIME, 'fr_FR')
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines_20plus["date"].values,
        y=df_drees_non_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["nb_PCR"].rolling(window=7).mean() * 100,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_non_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["nb_PCR"].rolling(window=7).mean()).values[-1]  * 100],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_20plus["date"].values,
        y=df_drees_completement_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["nb_PCR"].rolling(window=7).mean() * 100,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["nb_PCR"].rolling(window=7).mean()).values[-1] * 100],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel_20plus["date"].values,
        y=df_drees_completement_vaccines_rappel_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["nb_PCR"].rolling(window=7).mean() * 100,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["nb_PCR"].rolling(window=7).mean()).values[-1] * 100],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)

fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "<b>Taux de positivité des tests</b> Covid [20+ ans]",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="proportion de cas positifs, selon le statut vaccinal - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines_20plus["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines_20plus["nb_PCR"].rolling(window=7).mean().values[-1]*100
y_vaccines=df_drees_completement_vaccines_20plus["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_20plus["nb_PCR"].rolling(window=7).mean().values[-1]*100
y_vaccines_rappel=df_drees_completement_vaccines_rappel_20plus["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel_20plus["nb_PCR"].rolling(window=7).mean().values[-1]*100
text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str((round(y_non_vaccines,1)))} % PCR positifs<br>non vaccinés</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str((round(y_vaccines,1)))} % PCR positifs<br>vaccinés</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str((round(y_vaccines_rappel,1)))} % PCR positifs<br>vaccinés (rappel)</b></span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)


fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Cas positifs / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "taux_pcr_plus_proportion_selon_statut_vaccinal_20plus"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[49]:


locale.setlocale(locale.LC_TIME, 'fr_FR')
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines_20plus["date"].values,
        y=df_drees_non_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_non_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_20plus["date"].values,
        y=df_drees_completement_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel_20plus["date"].values,
        y=df_drees_completement_vaccines_rappel_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel_20plus["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)

fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "<b>Cas positifs</b> Covid [+ 20 ans]",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines_20plus["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines_20plus["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines_20plus["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_20plus["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel_20plus["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel_20plus["effectif"].values[-1] * 10000000
text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} cas positifs<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} cas positifs<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} cas positifs<br>vaccinés (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

fig.add_annotation(
    x=df_drees_20plus.date.max(),
    y=y_vaccines,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)


fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Cas positifs / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "pcr_plus_proportion_selon_statut_vaccinal_20plus"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[50]:


ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]
ages=df_drees_age_lastday.age.sort_values().unique()

for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, data_partiellement_vaccines, _  = get_df_by_vaccine_status(df_drees_age[(df_drees_age.age==age)])
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=data_non_vaccines["nb_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["nb_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_partiellement_vaccines["date"].values,
            y=data_partiellement_vaccines["nb_PCR+"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_partiellement_vaccines["date"].values[-1]],
            y=[(data_partiellement_vaccines["nb_PCR+"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="black",
            marker_size=10,
            showlegend=False
        )
    )

    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(256,256,256,0.8)"
        ),
         margin=dict(
            r=160
        ),
        title={
                            'text': f"<b>Cas positifs</b> Covid [{ages_str[idx]}]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.55,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    y_non_vaccines=data_non_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000

    y_vaccines=data_completement_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    
    y_vaccines_rappel=data_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000
    
    text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} cas positifs<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} cas positifs<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} cas positifs<br>vaccinés (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

    fig.add_annotation(
        x=df_drees.date.max(),
        y=y_vaccines,
        text=text,
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=100,
    )
    
    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations pour suspicion Covid19.</i>",
        font=dict(size=9),
        showarrow=False,
        xshift=0,
        yshift=30
    )
    if age=='[0,19]':
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            text="⚠️ Données de vaccination trop faibles, graphique non interprétable",
            font=dict(size=20, color="red"),
            bgcolor="rgba(255, 255, 255, 0.5)",
            showarrow=False,
            xshift=0,
            yshift=30
        )
        
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"pcr_plus_proportion_selon_statut_vaccinal_{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[51]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["HC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["HC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    margin=dict(
            r=160
        ),
    title={
                        'text': "Taux d'<b>admission à l'hôpital</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines_rappel,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "hc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[52]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines_20plus["date"].values,
        y=df_drees_non_vaccines_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_non_vaccines_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines_20plus["date"].values,
        y=df_drees_partiellement_vaccines_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines_20plus["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_20plus["date"].values,
        y=df_drees_completement_vaccines_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel_20plus["date"].values,
        y=df_drees_completement_vaccines_rappel_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel_20plus["HC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    margin=dict(
            r=160
        ),
    title={
                        'text': "Taux d'<b>admission à l'hôpital</b> Covid [+ 20 ans]",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines_20plus["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines_20plus["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines_20plus["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_20plus["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel_20plus["HC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel_20plus["effectif"].values[-1] * 10000000

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_non_vaccines-170,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe", range=[0, 1200])
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "hc_proportion_selon_statut_vaccinal_plus20"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[53]:


fig = go.Figure()
# df_drees_completement_vaccines_rappel_20plus_moins_3_mois, df_drees_completement_vaccines_rappel_20plus_3_6_mois, df_drees_completement_vaccines_rappel_20plus_plus_6_mois
fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines_20plus["date"].values,
        y=df_drees_non_vaccines_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_non_vaccines_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines_20plus["date"].values,
        y=df_drees_partiellement_vaccines_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines_20plus["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_20plus["date"].values,
        y=df_drees_completement_vaccines_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_20plus["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel_20plus["date"].values,
        y=df_drees_completement_vaccines_rappel_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel_20plus["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel_20plus["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel_20plus["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    margin=dict(
            r=160
        ),
    title={
                        'text': "Taux d'<b>admission en soins critiques</b> Covid [+ 20 ans]",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines_20plus["SC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines_20plus["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines_20plus["SC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_20plus["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel_20plus["SC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel_20plus["effectif"].values[-1] * 10000000

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_non_vaccines-170,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Admissions en soins critiques avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe", range=[0, 370])
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "sc_proportion_selon_statut_vaccinal_plus20"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[54]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["HC_PCR+"].rolling(window=7).mean(),
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["HC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["HC_PCR+"].rolling(window=7).mean(),
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["HC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean(),
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean(),
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
    margin=dict(
            r=160
        ),
    title={
                        'text': "<b>Admissions à l'hôpital</b> Covid",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal- {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1]
y_vaccines=df_drees_completement_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1]
y_vaccines_rappel=df_drees_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean().values[-1]

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b></span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines_rappel,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)

fig.add_annotation(
    x=0.5,
    y=0.5,
    xref='paper',
    yref='paper',
    text="⚠️ Chiffres absolus. Pour évaluer l'efficacité de la vaccination,<br>il faut les rapporter aux effectifs de chaque groupe.",
    bgcolor="rgba(255, 255, 255, 0.7)",
    font=dict(size=15),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. absolues")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "hc_proportion_selon_statut_vaccinal_absolu"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[55]:


ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, data_partiellement_vaccines, _  = get_df_by_vaccine_status(df_drees_age[(df_drees_age.age==age)])
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=data_non_vaccines["HC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["HC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés (rappel)",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
            name="Vaccinés (rappel)",
            line_color="black",
            marker_size=10,
            showlegend=False
        )
    )


    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(256,256,256,0.8)"
        ),
         margin=dict(
            r=160
        ),
        title={
                            'text': f"<b>Admissions à l'hôpital</b> Covid [{ages_str[idx]}]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.55,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    
    y_non_vaccines=data_non_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    y_vaccines=data_completement_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    y_vaccines_rappel=data_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000

    text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

    fig.add_annotation(
        x=data_completement_vaccines_rappel.date.max(),
        y=y_vaccines_rappel,
        text=text,
        yanchor="bottom",
        showarrow=False,
        align="left",
        yshift=0,
        xshift=100,
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
        font=dict(size=9),
        showarrow=False,
        xshift=0,
        yshift=30
    )
    
    if age=='[0,19]':
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            text="⚠️ Données trop faibles, graphique non interprétable",
            font=dict(size=30, color="red"),
            bgcolor="rgba(255, 255, 255, 0.5)",
            showarrow=False,
            xshift=0,
            yshift=30
        )
        
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"hc_proportion_selon_statut_vaccinal_{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[56]:


ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, data_partiellement_vaccines, _  = get_df_by_vaccine_status(df_drees_age[(df_drees_age.age==age)])
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=data_non_vaccines["HC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["HC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_partiellement_vaccines["date"].values,
            y=data_partiellement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_partiellement_vaccines["date"].values[-1]],
            y=[(data_partiellement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés (rappel)",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
            name="Vaccinés (rappel)",
            line_color="black",
            marker_size=10,
            showlegend=False
        )
    )


    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(256,256,256,0.8)"
        ),
         margin=dict(
            r=160
        ),
        title={
                            'text': f"<b>Admissions à l'hôpital</b> Covid [{ages_str[idx]}]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.55,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    
    y_non_vaccines=data_non_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    y_vaccines=data_completement_vaccines["HC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    y_vaccines_rappel=data_completement_vaccines_rappel["HC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000

    text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

    fig.add_annotation(
        x=data_completement_vaccines_rappel.date.max(),
        y=y_vaccines_rappel,
        text=text,
        yanchor="bottom",
        showarrow=False,
        align="left",
        yshift=0,
        xshift=100,
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
        font=dict(size=9),
        showarrow=False,
        xshift=0,
        yshift=30
    )
    
    if age=='[0,19]':
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            text="⚠️ Données trop faibles, graphique non interprétable",
            font=dict(size=30, color="red"),
            bgcolor="rgba(255, 255, 255, 0.5)",
            showarrow=False,
            xshift=0,
            yshift=30
        )
        
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"hc_proportion_selon_statut_vaccinal_et_date_vaccination{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[57]:


ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]
for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    
    fig = go.Figure()
    
    y_non_vaccines=(data_non_vaccines["HC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values
    y_completement_vaccines=(data_completement_vaccines["HC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values
    y=y_non_vaccines / y_completement_vaccines
    
    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=y,
            name="Ratio",
            line_color="black",
            line_width=4,
            yaxis="y2",
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=y_non_vaccines,
            name="Taux adm. non vaccinées",
            marker_color="rgba(198, 81, 2, 0.2)",
            #fill="tozeroy",
            fillcolor="rgba(198, 81, 2, 0.2)",
            yaxis="y"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=y_completement_vaccines,
            name="Taux adm. complètement vaccinées",
            marker_color="rgba(0, 48, 143, 0.2)",
            #fill="tozeroy",
            fillcolor="rgba(0, 48, 143, 0.2)",
            yaxis="y"
        )
    )
    

    fig.update_layout(
        yaxis=dict(
            title="Admissions / jour / 100k hab.<br>",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            showgrid=False
        ),
        yaxis2=dict(
            title="Ratio : adm. non vaccinées / adm. complètement vaccinées",
            titlefont=dict(
                color="black"
            ),
            tickfont=dict(
                color="black"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0,
            showgrid=False
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(256,256,256,0.8)"
        ),
         margin=dict(
            r=160,
            l=20
        ),
        title={
                            'text': f"Vaccin : réduction du risque d'admission à l'hôpital [{ages_str[idx]}]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.55,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="et admissions selon le statut vaccinal pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    
    fig.add_annotation(
        x=df_drees.date.max(),
        y=y[-1],
        text="<b>" + str(int(round(y[-1]))) + " x plus d'admissions<br>chez les non vaccinés<br></b>par rapport aux<br>vaccinés complètement",
        font=dict(color="black"),
        showarrow=False,
        align="left",
        xshift=90,
        yshift=0,
        yref="y2"
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
        font=dict(size=9),
        showarrow=False,
        xshift=0,
        yshift=30
    )
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"hc_rapport_selon_statut_vaccinal_{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[58]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["SC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["SC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        mode="markers",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        mode="markers",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["SC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        mode="markers",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "Taux d'<b>admission</b> <b>en soins critiques</b> Covid",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.55,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {} - Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["SC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines["SC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel["SC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines_rappel,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    yanchor="bottom",
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Admissions avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    xshift=0,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "sc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[59]:


ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, data_partiellement_vaccines, _  = get_df_by_vaccine_status(df_drees_age[(df_drees_age.age==age)])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=data_non_vaccines["SC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["SC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["SC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["SC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["SC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés (rappel)",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["SC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
            name="Vaccinés (rappel)",
            line_color="black",
            marker_size=10,
            showlegend=False
        )
    )


    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(256,256,256,0.8)"
        ),
         margin=dict(
            r=160
        ),
        title={
                            'text': f"<b>Admissions en soins critiques</b> Covid [{ages_str[idx]}]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.55,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    
    y_non_vaccines=data_non_vaccines["SC_PCR+"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    y_vaccines=data_completement_vaccines["SC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    y_vaccines_rappel=data_completement_vaccines_rappel["SC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000

    text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} admissions<br>non vaccinées</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} admissions<br>vaccinées</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} admissions<br>vaccinées (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

    fig.add_annotation(
        x=df_drees.date.max(),
        y=y_vaccines_rappel,
        text=text,
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        showarrow=False,
        yanchor="bottom",
        align="left",
        yshift=0,
        xshift=100,
    )
    

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
        font=dict(size=9),
        showarrow=False,
        xshift=0,
        yshift=30
    )
    
    if age=='[0,19]':
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            text="⚠️ Données trop faibles, graphique non interprétable",
            font=dict(size=30, color="red"),
            bgcolor="rgba(255, 255, 255, 0.5)",
            showarrow=False,
            xshift=0,
            yshift=30
        )
    
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"sc_proportion_selon_statut_vaccinal_{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[60]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["DC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["DC_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["DC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["DC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                        'text': "Taux de <b>décès</b> Covid à l'hôpital",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["DC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines["DC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} décès<br>non vaccinées</b><br>pour 10 Mio<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} décès<br>vaccinées</b><br>pour 10 Mio<br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} décès<br>vaccinées (rappel)</b><br>pour 10 Mio<br></span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines_rappel,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations pour suspicion Covid19.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Décès à l'hôpital avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Décès hosp. quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "dc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[61]:


ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, data_partiellement_vaccines, _  = get_df_by_vaccine_status(df_drees_age[(df_drees_age.age==age)])
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=data_non_vaccines["DC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["DC_PCR+"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )


    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["DC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["DC_PCR+"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés (rappel)",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
            name="Vaccinés (rappel)",
            line_color="black",
            marker_size=10,
            showlegend=False
        )
    )


    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(256,256,256,0.8)"
        ),
         margin=dict(
            r=160
        ),
        title={
                            'text': f"<b>Décès à l'hôpital</b> Covid [{ages_str[idx]}]",
                            'y':0.97,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'},
        titlefont = dict(
                        size=25),
        annotations = [
                            dict(
                                x=0.55,
                                y=1.12,
                                xref='paper',
                                yref='paper',
                                font=dict(size=14),
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    
    y_non_vaccines=data_non_vaccines["DC_PCR+"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    y_vaccines=data_completement_vaccines["DC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    y_vaccines_rappel=data_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000

    text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} décès<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} décès<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés<br><br></span>"
    text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} décès<br>vaccinés (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)</span>"

    fig.add_annotation(
        x=data_completement_vaccines_rappel.date.max(),
        y=y_vaccines_rappel,
        text=text,
        yanchor="bottom",
        showarrow=False,
        align="left",
        yshift=0,
        xshift=100,
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations Covid19 avec test Covid positif.</i>",
        font=dict(size=9),
        showarrow=False,
        xshift=0,
        yshift=30
    )
    
    if age=='[0,19]':
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            text="⚠️ Données trop faibles, graphique non interprétable",
            font=dict(size=30, color="red"),
            bgcolor="rgba(255, 255, 255, 0.5)",
            showarrow=False,
            xshift=0,
            yshift=30
        )
        
    fig.update_yaxes(title="Décès quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"dc_proportion_selon_statut_vaccinal_{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[62]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["DC_PCR+"].rolling(window=7).mean(),
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["DC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["DC_PCR+"].rolling(window=7).mean(),
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["DC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean(),
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean()).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)


fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(256,256,256,0.8)"
    ),
     margin=dict(
            r=160
        ),
    title={
                    'text': "<b>Décès</b> Covid à l'hôpital",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
    titlefont = dict(
                    size=25),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="selon le statut vaccinal - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

y_non_vaccines=df_drees_non_vaccines["DC_PCR+"].rolling(window=7).mean().values[-1]
y_vaccines=df_drees_completement_vaccines["DC_PCR+"].rolling(window=7).mean().values[-1]
y_vaccines_rappel=df_drees_completement_vaccines_rappel["DC_PCR+"].rolling(window=7).mean().values[-1]

text = f"<span style='color: {COULEUR_NON_VACCINES};'><b>{str(int(round(y_non_vaccines)))} décès<br>non vaccinés</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES};'><b>{str(int(round(y_vaccines)))} décès<br>vaccinés</b><br><br></span>"
text += f"<span style='color: {COULEUR_COMPLETEMENT_VACCINES_RAPPEL};'><b>{str(int(round(y_vaccines_rappel)))} décès<br>vaccinés (rappel)</b><br></span>"

fig.add_annotation(
    x=df_drees.date.max(),
    y=y_vaccines,
    text=text,
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100,
)

fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations avec test Covid19 positif.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)


fig.add_annotation(
    x=0.5,
    y=-0.225,
    xref='paper',
    yref='paper',
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Décès à l'hôpital pour suspicion Covid19.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)

fig.add_annotation(
    x=0.5,
    y=0.5,
    xref='paper',
    yref='paper',
    text="⚠️ Chiffres absolus. Pour évaluer l'efficacité de la vaccination,<br>il faut les rapporter aux effectifs de chaque groupe.",
    bgcolor="rgba(255, 255, 255, 0.7)",
    font=dict(size=15),
    showarrow=False,
    yshift=30
)

fig.update_yaxes(title="Décès hosp. quot. absolus")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "dc_proportion_selon_statut_vaccinal_absolu"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[63]:


positif_vax = round((df_drees_completement_vaccines["nb_PCR+_sympt"].values[-1]/df_drees_ensemble["nb_PCR+_sympt"].values[-1])*100)
pop_vax = round((df_drees_completement_vaccines["effectif"].values[-1]/df_drees_ensemble["effectif"].values[-1])*100)

stages = ["<b>Population générale</b>", "<b>Cas positifs symptomatiques</b>"]
df_mtl = pd.DataFrame(dict(number=[pop_vax, positif_vax], stage=stages))
df_mtl['État vaccinal'] = 'Complètement vacciné (%)'

df_toronto = pd.DataFrame(dict(number=[100-pop_vax, 100-positif_vax], stage=stages))
df_toronto['État vaccinal'] = 'Non vacciné (%)'

df = pd.concat([df_mtl, df_toronto], axis=0)
fig = px.funnel(df, y='number', x='stage', color='État vaccinal', height=700, width=700, orientation="v", title="<b>Statut vaccinal des cas symptomatiques</b><br><span style='font-size: 10px;'>Données DREES au 01/08/21 - Guillaume Rozier</span>")
fig.show()

