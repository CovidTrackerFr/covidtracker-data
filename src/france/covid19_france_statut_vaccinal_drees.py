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

The charts are exported to 'charts/images/france'.
Data is download to/imported from 'data/france'.
Requirements: please see the imports below (use pip3 to install them).

"""


# In[2]:


import pandas as pd
import plotly.express as px
from datetime import timedelta
import france_data_management as data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import plotly
import cv2
PATH = "../../"
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


# In[3]:


COULEUR_NON_VACCINES = "#C65102"
COULEUR_COMPLETEMENT_VACCINES = "#00308F"
COULEUR_COMPLETEMENT_VACCINES_RAPPEL = "black"
COULEUR_PARTIELLEMENT_VACCINES = "#4777d6"


# In[4]:


df_drees = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-issus-des-appariements-entre-si-vic-si-dep-et-vac-si/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
#df_drees = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-anciens-resultats-nationaux-issus-des-appariements-entre-si-vic-si-dep-/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
#df_drees = df_drees[df_drees["date"]<="2021-09-26"] #TODO SUPPR

df_drees = df_drees.sort_values(by="date")
df_drees = df_drees[df_drees["vac_statut"]!="Ensemble"]


# In[5]:


df_drees_age = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-par-age-issus-des-appariements-entre-si-vic-si-dep-et-vac-si/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")

df_drees_age_all = df_drees_age.groupby(["date", "vac_statut", "age"]).sum().reset_index()
df_drees_age = df_drees_age.sort_values(by="date")
df_drees_age = df_drees_age[df_drees_age["vac_statut"]!="Ensemble"]
df_drees_age_lastday = df_drees_age[df_drees_age["date"] == df_drees_age["date"].max()]


# In[6]:


df_drees_non_vaccines = df_drees[df_drees["vac_statut"]=="Non-vaccinés"]
df_drees_non_vaccines["effectif"] = df_drees_non_vaccines["effectif"].rolling(window=7).mean()

df_drees_completement_vaccines = df_drees[df_drees["vac_statut"].isin(["Complet de moins de 3 mois - sans rappel", "Complet entre 3 mois et 6 mois - sans rappel", "Complet de 6 mois et plus - sans rappel"])].groupby("date").sum().reset_index()
df_drees_completement_vaccines["effectif"] = df_drees_completement_vaccines["effectif"].rolling(window=7).mean()

df_drees_completement_vaccines_rappel = df_drees[df_drees["vac_statut"].isin(["Complet de moins de 3 mois - avec rappel", "Complet entre 3 mois et 6 mois - avec rappel", "Complet de 6 mois et plus - avec rappel"])].groupby("date").sum().reset_index()
df_drees_completement_vaccines_rappel["effectif"] = df_drees_completement_vaccines_rappel["effectif"].rolling(window=7).mean()

df_drees_partiellement_vaccines = df_drees[df_drees["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
df_drees_partiellement_vaccines["effectif"] = df_drees_partiellement_vaccines["effectif"].rolling(window=7).mean()

#df_drees_ensemble = df_drees[df_drees["vac_statut"]=="Ensemble"]
df_drees_ensemble = df_drees.groupby("date").sum().reset_index()


# In[7]:


def get_df_by_vaccine_status(df):
    df_drees_non_vaccines = df[df["vac_statut"]=="Non-vaccinés"]
    df_drees_non_vaccines["effectif"] = df_drees_non_vaccines["effectif"].rolling(window=7).mean()

    df_drees_completement_vaccines = df[df["vac_statut"].isin(["Complet de moins de 3 mois - sans rappel", "Complet entre 3 mois et 6 mois - sans rappel", "Complet de 6 mois et plus - sans rappel"])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines["effectif"] = df_drees_completement_vaccines["effectif"].rolling(window=7).mean()

    df_drees_completement_vaccines_rappel = df[df["vac_statut"].isin(["Complet de moins de 3 mois - avec rappel", "Complet entre 3 mois et 6 mois - avec rappel", "Complet de 6 mois et plus - avec rappel"])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines_rappel["effectif"] = df_drees_completement_vaccines_rappel["effectif"].rolling(window=7).mean()

    df_drees_partiellement_vaccines = df[df["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
    df_drees_partiellement_vaccines["effectif"] = df_drees_partiellement_vaccines["effectif"].rolling(window=7).mean()

    #df_drees_ensemble = df_drees[df_drees["vac_statut"]=="Ensemble"]
    df_drees_ensemble = df.groupby("date").sum().reset_index()
    
    return df_drees_non_vaccines, df_drees_completement_vaccines, df_drees_completement_vaccines_rappel, df_drees_partiellement_vaccines, df_drees_ensemble
    


# In[53]:


fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages = np.delete(ages, np.where(ages == '[0,19]'))

ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]
    
y=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_NON_VACCINES),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Non vaccinés"
))

y=[]
for age in ages:
    #data=df_drees_age[df_drees_age.vac_statut.isin(["Primo dose récente", "Primo dose efficace"])].groupby(["date", "age"]).sum().reset_index()
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_PARTIELLEMENT_VACCINES),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Partiellement vaccinés")
             )

y=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Totalement vaccinés"
))

y=[]
for age in ages:
    _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Totalement vaccinés (avec rappel)"
))
    
fig.update_layout(
    barmode="group", bargroupgap=0,
    title={
                        'text': "<b>Admissions à l'hôpital</b> pour Covid",
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
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Admissions à l'hôpital pour 10 Mio")
fig.update_xaxes(title="Âge")
name_fig = "hc_statut_vaccinal_age"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[9]:


import numpy as np

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y_non_vaccines=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_partiellement_vaccines=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_completement_vaccines=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["HC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

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
                        'text': "<b>Réduction du taux d'admissions à l'hôpital</b> pour Covid",
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
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Réduction du taux d'admissions à l'hôpital", tickformat="%", range=[0,1])
fig.update_xaxes(title="Âge", tickfont=dict(size=16))
name_fig = "hc_statut_vaccinal_age_diminution_risque"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[10]:


import numpy as np

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y_non_vaccines=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_non_vaccines+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_partiellement_vaccines=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_partiellement_vaccines+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

y_completement_vaccines=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y_completement_vaccines+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

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
                        'text': "<b>Réduction du taux d'admissions en soins critiques</b> pour Covid",
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
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Réduction du taux d'admissions en soins critiques", tickformat="%", range=[0,1])
fig.update_xaxes(title="Âge", tickfont=dict(size=16))
name_fig = "sc_statut_vaccinal_age_diminution_risque"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[54]:


import ast 

fig = go.Figure()
ages=df_drees_age_lastday.age.sort_values().unique()
ages = np.delete(ages, np.where(ages == '[0,19]'))
ages_str = ["20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

y=[]
for age in ages:
    data, _, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_NON_VACCINES),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Non vaccinés"
))

y=[]
for age in ages:
    _, _, _, data, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_PARTIELLEMENT_VACCINES),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Partiellement vaccinés")
             )

y=[]
for age in ages:
    _, data, _, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Totalement vaccinés"
))

y=[]
for age in ages:
    _, _, data, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    y+=[data["SC"].rolling(window=7).mean().values[-1]/data["effectif"].values[-1]*10000000]

fig.add_trace(go.Bar(
    x=ages_str,
    y=y,
    marker=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
    text=[int(round(val)) for val in y],
    textposition='outside',
    name="Totalement vaccinés (avec rappel)"
))
    
fig.update_layout(
    barmode="group", bargroupgap=0,
    title={
                        'text': "<b>Admissions en soins critiques</b> pour Covid",
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
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30,
    xshift=0
)

fig.update_yaxes(title="Admissions en soins critiques pour 10 Mio")
fig.update_xaxes(title="Âge")
name_fig = "sc_statut_vaccinal_age"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#fig.show()


# In[12]:


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


# In[13]:


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
y=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas positifs<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    align="left",
    xshift=100,
    yshift=0
)
y=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " cas positifs<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    yshift=0,
    xshift=100
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


# In[14]:


ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]
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
    y=data_non_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " cas positifs<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés",
        font=dict(color=COULEUR_NON_VACCINES),
        showarrow=False,
        align="left",
        xshift=100,
        yshift=0
    )

    y=data_completement_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " cas positifs<br>vaccinés</b><br>pour 10 Mio<br>de vaccinés",
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=100,
    )
    
    y=data_completement_vaccines_rappel["nb_PCR+"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " cas positifs<br>vaccinés (rappel)</b><br>pour 10 Mio<br>de vaccinés (rappel)",
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES_RAPPEL),
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
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = f"pcr_plus_proportion_selon_statut_vaccinal_{age}"
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[15]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["HC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["HC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color="#C65102",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000).values[-1]],
        name="Partiellement vaccinés",
        line_color="#4777d6",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["HC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["HC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["HC"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)

fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["HC"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
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
                        'text': "<b>Admissions à l'hôpital</b> pour Covid",
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

y_non_vaccines=df_drees_non_vaccines["HC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines["HC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel["HC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000

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
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations pour suspicion Covid19.</i>",
    font=dict(size=9),
    showarrow=False,
    yshift=30
)
fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "hc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[60]:


ages=df_drees_age_lastday.age.sort_values().unique()
ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, data_partiellement_vaccines, _  = get_df_by_vaccine_status(df_drees_age[(df_drees_age.age==age)])
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_non_vaccines["date"].values,
            y=data_non_vaccines["HC"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["HC"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_partiellement_vaccines["date"].values,
            y=data_partiellement_vaccines["HC"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_partiellement_vaccines["date"].values[-1]],
            y=[(data_partiellement_vaccines["HC"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["HC"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["HC"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["HC"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés (rappel)",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["HC"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
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
                            'text': f"<b>Admissions à l'hôpital</b> pour Covid [{ages_str[idx]}]",
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
    
    y_non_vaccines=data_non_vaccines["HC"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    y_vaccines=data_completement_vaccines["HC"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    y_vaccines_rappel=data_completement_vaccines_rappel["HC"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000

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


# In[17]:


ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]
for idx, age in enumerate(ages):
    data_non_vaccines, data_completement_vaccines, data_completement_vaccines_rappel, _, _ = get_df_by_vaccine_status(df_drees_age[df_drees_age.age==age])
    
    fig = go.Figure()
    
    y_non_vaccines=(data_non_vaccines["HC"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values
    y_completement_vaccines=(data_completement_vaccines["HC"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values
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
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.<br>Hospitalisations pour suspicion Covid19.</i>",
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


# In[18]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["SC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color="#C65102",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["SC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
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
        y=df_drees_completement_vaccines["SC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["SC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
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
        y=df_drees_completement_vaccines_rappel["SC"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["SC"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        mode="markers",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["SC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["SC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000).values[-1]],
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
                    'text': "<b>Admissions</b> <b>en soins critiques</b> Covid",
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

y_non_vaccines=df_drees_non_vaccines["SC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
y_vaccines=df_drees_completement_vaccines["SC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
y_vaccines_rappel=df_drees_completement_vaccines_rappel["SC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines_rappel["effectif"].values[-1] * 10000000

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
    text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
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
            y=data_non_vaccines["SC"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_non_vaccines["date"].values[-1]],
            y=[(data_non_vaccines["SC"].rolling(window=7).mean() / data_non_vaccines["effectif"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_partiellement_vaccines["date"].values,
            y=data_partiellement_vaccines["SC"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[data_partiellement_vaccines["date"].values[-1]],
            y=[(data_partiellement_vaccines["SC"].rolling(window=7).mean() / data_partiellement_vaccines["effectif"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines["date"].values,
            y=data_completement_vaccines["SC"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines["date"].values[-1]],
            y=[(data_completement_vaccines["SC"].rolling(window=7).mean() / data_completement_vaccines["effectif"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
            marker_size=10,
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=data_completement_vaccines_rappel["date"].values,
            y=data_completement_vaccines_rappel["SC"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000,
            name="Vaccinés (rappel)",
            line_color="black",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[data_completement_vaccines_rappel["date"].values[-1]],
            y=[(data_completement_vaccines_rappel["SC"].rolling(window=7).mean() / data_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
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
                            'text': f"<b>Admissions en soins critiques</b> pour Covid [{ages_str[idx]}]",
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
    
    y_non_vaccines=data_non_vaccines["SC"].rolling(window=7).mean().values[-1] / data_non_vaccines["effectif"].values[-1] * 10000000
    y_vaccines=data_completement_vaccines["SC"].rolling(window=7).mean().values[-1] / data_completement_vaccines["effectif"].values[-1] * 10000000
    y_vaccines_rappel=data_completement_vaccines_rappel["SC"].rolling(window=7).mean().values[-1] / data_completement_vaccines_rappel["effectif"].values[-1] * 10000000

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


# In[20]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_drees_non_vaccines["date"].values,
        y=df_drees_non_vaccines["DC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000,
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_non_vaccines["date"].values[-1]],
        y=[(df_drees_non_vaccines["DC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif"] * 10000000).values[-1]],
        name="Non vaccinés",
        line_color=COULEUR_NON_VACCINES,
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines["date"].values,
        y=df_drees_completement_vaccines["DC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000,
        name="Vaccinés",
        line_color="#00308F",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines["date"].values[-1]],
        y=[(df_drees_completement_vaccines["DC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif"] * 10000000).values[-1]],
        name="Vaccinés",
        line_color="#00308F",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_completement_vaccines_rappel["date"].values,
        y=df_drees_completement_vaccines_rappel["DC"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000,
        name="Vaccinés (rappel)",
        line_color="black",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_completement_vaccines_rappel["date"].values[-1]],
        y=[(df_drees_completement_vaccines_rappel["DC"].rolling(window=7).mean() / df_drees_completement_vaccines_rappel["effectif"] * 10000000).values[-1]],
        name="Vaccinés (rappel)",
        line_color="black",
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=df_drees_partiellement_vaccines["date"].values,
        y=df_drees_partiellement_vaccines["DC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000,
        name="Partiellement vaccinés",
        line_color="#4777d6",
        line_width=4
    )
)
fig.add_trace(
    go.Scatter(
        x=[df_drees_partiellement_vaccines["date"].values[-1]],
        y=[(df_drees_partiellement_vaccines["DC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif"] * 10000000).values[-1]],
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
                            text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)
y=df_drees_non_vaccines["DC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " décès<br>non vaccinés</b><br>pour 10 Mio<br>de non vaccinés",
    font=dict(color=COULEUR_NON_VACCINES),
    showarrow=False,
    align="left",
    xshift=80,
    yshift=50
)
y=df_drees_completement_vaccines["DC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif"].values[-1] * 10000000
fig.add_annotation(
    x=df_drees.date.max(),
    y=y,
    text="<b>" + str(int(round(y))) + " décès<br>vaccinés</b><br>pour 10 Mio de vaccinés",
    font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
    showarrow=False,
    align="left",
    xshift=100,
    yshift=0
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
fig.update_yaxes(title="Décès hosp. quot. / 10 Mio hab. de chaque groupe")
fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees.date.max(), '%Y-%m-%d') + timedelta(days=2)])
name_fig = "dc_proportion_selon_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)


# In[21]:


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


# In[22]:


taux_positif_vax = round((df_drees_completement_vaccines["nb_PCR+_sympt"].values[-1]/df_drees_completement_vaccines["nb_PCR_sympt"].values[-1])*100)
taux_positif_non_vax = round((df_drees_non_vaccines["nb_PCR+_sympt"].values[-1]/df_drees_non_vaccines["nb_PCR_sympt"].values[-1])*100)

stages = ["<b><br><span style='font-size:15px;'>Non vacciné</b></span>", "<b><br><span style='font-size:15px;'>Vacciné</span></b>"]
df_mtl = pd.DataFrame(dict(number=[taux_positif_non_vax, taux_positif_vax], stage=stages))
df_mtl['Résultat'] = '<b>Positif</b> (%)'
df_toronto = pd.DataFrame(dict(number=[100-taux_positif_non_vax, 100-taux_positif_vax], stage=stages))
df_toronto['Résultat'] = '<b>Négatif</b> (%)'
df = pd.concat([df_toronto, df_mtl], axis=0)
fig = px.funnel(df, y='number', x='stage', color='Résultat', height=700, width=600, orientation="v", title="<b>Résultat des tests des personnes symptomatiques</b><br><span style='font-size: 10px;'>Données DREES 01/08/21 - Guillaume Rozier</span>")
fig.show()


# In[23]:


#df = pd.concat([df_completement_vaccine, df_partiellement_vaccine, df_non_vaccine], axis=0)

hosp_vax = int(round((df_drees_completement_vaccines["HC"].values[-1]/df_drees_ensemble["HC"].values[-1])*100))
hosp_partiellement_vax = int(round((df_drees_partiellement_vaccines["HC"].values[-1]/df_drees_ensemble["HC"].values[-1])*100))

pop_vax = int(round((df_drees_completement_vaccines["effectif J-7"].values[-1]/df_drees_ensemble["effectif J-7"].values[-1])*100))
pop_partiellement_vax = int(round((df_drees_partiellement_vaccines["effectif J-7"].values[-1]/df_drees_ensemble["effectif J-7"].values[-1])*100))

x=["<b>Population générale</b>", "<b>Hospitalisés</b>"]
y1 = [100-pop_vax-pop_partiellement_vax, 100-hosp_partiellement_vax-hosp_vax]
fig = go.Figure()
fig.add_trace(go.Funnel(
    name = 'Non vaccinés',
    orientation = "v",
    x = x,
    marker=dict(color="#e76f41"),
    text=[str(val) + " %" for val in y1],
    textinfo="text",
    y = y1,
))

y2 = [pop_partiellement_vax, hosp_partiellement_vax]
fig.add_trace(go.Funnel(
    name = 'Partiellement vaccinés',
    orientation = "v",
    x = x,
    y = y2,
    marker=dict(color="#e9c46a"),
    text=[str(val) + " %" for val in y2],
    textinfo="text",
    textposition = "inside",
))

y3 = [pop_vax, hosp_vax]
fig.add_trace(go.Funnel(
    name = 'Totalement vaccinés',
    orientation = "v",
    x = x,
    y = y3,
    marker=dict(color="#2a9d8f"),
    text=[str(val) + " %" for val in y3],
    textinfo="text"
    ))
fig.update_layout(
    title=f"<b>État vaccinal des personnes admises à l'hôpital</b><br><span style='font-size: 10px;'><b>Lecture :</b> {y3[0]}% des Français sont vaccinés, mais ils représentent {y3[1]}% des admissions à l'hôpital.<br>Données DREES {datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')} - @GuillaumeRozier</span>",
    font=dict(size=10)
)
name_fig = "popgen_hosp_statut_vaccinal"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=600, height=600)


# In[ ]:


ages_str = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "plus 80 ans"]

for (idx, age) in enumerate(ages):
    df_drees_all_ensemble = df_drees_age_all[(df_drees_age_all.age==age)].groupby("date").sum()
    data_completement_vaccines = df_drees_age[(df_drees_age.age==age) & (df_drees_age.vac_statut=="Vaccination complète")]
    data_non_vaccines = df_drees_age[(df_drees_age.age==age) & (df_drees_age.vac_statut=="Non-vaccinés")]
    data_partiellement_vaccines = df_drees_age[(df_drees_age.age==age) & (df_drees_age.vac_statut.isin(["Primo dose récente", "Primo dose efficace"]))].groupby(["date", "age"]).sum().reset_index()
    
    hosp_vax = int(round((data_completement_vaccines["HC"].rolling(window=7).mean().values[-1]/df_drees_all_ensemble["HC"].values[-1])*100))
    hosp_partiellement_vax = int(round((data_partiellement_vaccines["HC"].rolling(window=7).mean().values[-1]/df_drees_all_ensemble["HC"].values[-1])*100))

    pop_vax = int(round((data_completement_vaccines["effectif J-7"].values[-1]/df_drees_all_ensemble["effectif J-7"].values[-1])*100))
    pop_partiellement_vax = int(round((data_partiellement_vaccines["effectif J-7"].values[-1]/df_drees_all_ensemble["effectif J-7"].values[-1])*100))

    x=["<b>Population générale</b>", "<b>Hospitalisés</b>"]
    y1 = [100-pop_vax-pop_partiellement_vax, 100-hosp_partiellement_vax-hosp_vax]
    fig = go.Figure()
    fig.add_trace(go.Funnel(
        name = 'Non vaccinés',
        orientation = "v",
        x = x,
        marker=dict(color="#e76f41"),
        text=[str(val) + " %" for val in y1],
        textinfo="text",
        y = y1,
    ))

    y2 = [pop_partiellement_vax, hosp_partiellement_vax]
    fig.add_trace(go.Funnel(
        name = 'Partiellement vaccinés',
        orientation = "v",
        x = x,
        y = y2,
        marker=dict(color="#e9c46a"),
        text=[str(val) + " %" for val in y2],
        textinfo="text",
        textposition = "inside",
    ))

    y3 = [pop_vax, hosp_vax]
    fig.add_trace(go.Funnel(
        name = 'Totalement vaccinés',
        orientation = "v",
        x = x,
        y = y3,
        marker=dict(color="#2a9d8f"),
        text=[str(val) + " %" for val in y3],
        textinfo="text"
        ))
    fig.update_layout(
        title=f"<b>État vaccinal des personnes admises à l'hôpital [{ages_str[idx]}]</b><br><span style='font-size: 10px;'><b>Lecture :</b> {y3[0]}% des Français sont vaccinés, mais ils représentent {y3[1]}% des admissions à l'hôpital.<br>Données DREES {datetime.strptime(df_drees.date.max(), '%Y-%m-%d').strftime('%d %B %Y')} - @GuillaumeRozier</span>",
        font=dict(size=10)
    )
    name_fig = "popgen_hosp_statut_vaccinal_{}".format(age)
    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=600, height=600)


# In[ ]:


df_drees_age_lastday_completement_vaccines = df_drees_age_lastday[df_drees_age_lastday.vac_statut=="Vaccination complète"][["age", "HC", "effectif J-7"]]
df_drees_age_lastday_completement_vaccines["taux_HC_completement_vaccines"] = df_drees_age_lastday_completement_vaccines["HC"] / df_drees_age_lastday_completement_vaccines["effectif J-7"]
df_drees_age_lastday_completement_vaccines = df_drees_age_lastday_completement_vaccines.drop(["HC", "effectif J-7"], axis=1)


df_drees_age_lastday_non_vaccines = df_drees_age_lastday[df_drees_age_lastday.vac_statut=="Non-vaccinés"][["age", "HC", "effectif J-7"]]
df_drees_age_lastday_non_vaccines["taux_HC_non_vaccines"] = df_drees_age_lastday_non_vaccines["HC"] / df_drees_age_lastday_non_vaccines["effectif J-7"]
df_drees_age_lastday_non_vaccines = df_drees_age_lastday_non_vaccines.drop(["HC", "effectif J-7"], axis=1)

df_drees_age_lastday_taux = df_drees_age_lastday_completement_vaccines.merge(df_drees_age_lastday_non_vaccines, left_on="age", right_on="age")
df_drees_age_lastday_taux["ratio_reduction_risque"] = df_drees_age_lastday_taux["taux_HC_non_vaccines"] / df_drees_age_lastday_taux["taux_HC_completement_vaccines"]
df_drees_age_lastday_taux

