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


import pandas as pd
import numpy as np
import plotly.graph_objects as go
import france_data_management as data
from datetime import datetime
from datetime import timedelta
import plotly
import math
import os
import json
from plotly.subplots import make_subplots
PATH = "../../"
PATH_STATS = "../../data/france/stats/"

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
COULEUR_NON_VACCINES = "#C65102"
COULEUR_COMPLETEMENT_VACCINES = "#00308F"


# In[3]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[4]:


df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid[df_incid["cl_age90"] == 0].groupby(["jour", "regionName"]).sum().reset_index()
regions = list(dict.fromkeys(list(df_regions['regionName'].values))) 
dates_incid = list(dict.fromkeys(list(df_incid['jour'].values))) 
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")

df_new_regions = df_new.groupby(["jour", "regionName"]).sum().reset_index()


# In[5]:


lits_reas = pd.read_csv(PATH+'data/france/lits_rea.csv', sep=",")


# In[6]:


regions_deps = df.groupby(["departmentName", "regionName"]).sum().reset_index().loc[:,["departmentName", "regionName"]]
lits_reas = lits_reas.merge(regions_deps, left_on="nom_dpt", right_on="departmentName").drop(["nom_dpt"], axis=1)
lits_reas_regs = lits_reas.groupby(["regionName"]).sum().reset_index()
df_regions = df_regions.merge(lits_reas_regs, left_on="regionName", right_on="regionName")


# In[7]:


df_drees_regions = pd.read_csv("https://data.drees.solidarites-sante.gouv.fr/explore/dataset/covid-19-resultats-regionaux-issus-des-appariements-entre-si-vic-si-dep-et-vac-s/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B", sep=";")
noms_regions = pd.read_csv(PATH+"data/france/noms_regions_code_drees.csv", sep=",")
df_drees_regions = df_drees_regions.merge(noms_regions, left_on="region", right_on="codeRegionDrees")


# In[8]:


#data.download_data_variants_regs()
#df_variants = data.import_data_variants_regs()


# In[9]:


"""def nombre_variants(region):
    df_incid_reg = df_incid_regions[df_incid_regions["regionName"] == region]
    df_incid_reg["P_rolling"] = df_incid_reg["P"].rolling(window=7).mean()
    
    df_variants_reg = df_variants[df_variants["reg"] == df_incid_dep["reg"].values[0]]
    
    fig = go.Figure()
    n_days = len(df_variants_dep)

    y=df_incid_dep["P_rolling"].values[-n_days:] * df_variants_dep.Prc_susp_501Y_V1.values/100
    proportion = str(round(y[-1]/df_incid_dep["P_rolling"].values[-1]*100, 1)).replace(".", ",")
    fig.add_trace(
        go.Scatter(
            x=df_variants_dep.jour,
            y=y,
            name="<b>Variant UK </b><br>" + str(nbWithSpaces(y[-1])) + " cas (" + proportion + " %)",
            stackgroup='one'
        )
    )

    y=df_incid_dep["P_rolling"].values[-n_days:] * df_variants_dep.Prc_susp_501Y_V2_3.values/100
    proportion = str(round(y[-1]/df_incid_dep["P_rolling"].values[-1]*100, 1)).replace(".", ",")
    fig.add_trace(
        go.Scatter(
            x=df_variants_dep.jour,
            y=y,
            name="<b>Variants SA + BZ </b><br>" + str(nbWithSpaces(y[-1])) + " cas (" + proportion + " %)",
            showlegend=True,
            stackgroup='one'
        )
    )

    y=df_incid_dep["P_rolling"].values[-n_days:] * df_variants_dep.Prc_susp_IND.values/100
    proportion = str(round(y[-1]/df_incid_dep["P_rolling"].values[-1]*100, 1)).replace(".", ",")
    fig.add_trace(
        go.Scatter(
            x=df_variants_dep.jour,
            y=y,
            name="<b>Variants indéterminés </b><br>" + str(nbWithSpaces(y[-1])) + " cas (" + proportion + " %)",
            showlegend=True,
            stackgroup='one'
        )
    )
    y=df_incid_dep["P_rolling"].values[-n_days:] * df_variants_dep.Prc_susp_ABS.values/100
    proportion = str(round(y[-1]/df_incid_dep["P_rolling"].values[-1]*100, 1)).replace(".", ",")
    fig.add_trace(
        go.Scatter(
            x=df_variants_dep.jour,
            y=y,
            name="<b>Souche classique </b><br>" + str(nbWithSpaces(y[-1])) + " cas (" + proportion + " %)",
            showlegend=True,
            stackgroup='one'
        )
    )

    fig.update_yaxes(ticksuffix="")

    fig.update_layout(
         title={
            'text': "Nombre de variants dans les cas détectés - " + departement,
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
             'font': {'size': 20}
        },
        annotations = [
                        dict(
                            x=0.5,
                            y=1.1,
                            xref='paper',
                            yref='paper',
                            text='Date : {}. Données : Santé publique France. Auteur : @guillaumerozier - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),
                            showarrow = False
                        )]
    )
    fig.write_image(PATH+"images/charts/france/departements_dashboards/{}.jpeg".format("variants_nombre_"+departement), scale=1.5, width=750, height=500)
"""


# In[16]:


def pcr_plus_statut_vaccinal(region):
    df_drees_reg = df_drees_regions[df_drees_regions["regionName"] == region]
    df_drees_reg = df_drees_reg.sort_values(by="date")
    
    df_drees_non_vaccines = df_drees_reg[df_drees_reg["vac_statut"]=="Non-vaccinés"]
    df_drees_non_vaccines["effectif J-7"] = df_drees_non_vaccines["effectif J-7"].rolling(window=7).mean()

    df_drees_completement_vaccines = df_drees_reg[df_drees_reg["vac_statut"].isin(["Vaccination complète",])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines["effectif J-7"] = df_drees_completement_vaccines["effectif J-7"].rolling(window=7).mean()

    df_drees_partiellement_vaccines = df_drees_reg[df_drees_reg["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
    df_drees_partiellement_vaccines["effectif J-7"] = df_drees_partiellement_vaccines["effectif J-7"].rolling(window=7).mean()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_drees_non_vaccines["date"].values,
            y=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df_drees_non_vaccines["date"].values[-1]],
            y=[(df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_drees_partiellement_vaccines["date"].values,
            y=df_drees_partiellement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df_drees_partiellement_vaccines["date"].values[-1]],
            y=[(df_drees_partiellement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_drees_completement_vaccines["date"].values,
            y=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[df_drees_completement_vaccines["date"].values[-1]],
            y=[(df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
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
                            'text': "<b>Cas positifs</b> pour Covid - " + region,
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
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees_reg.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    y=df_drees_non_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees_reg.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " cas positifs<br>non vaccinés</b><br>/ 10 Mio de non vaccinés",
        font=dict(color=COULEUR_NON_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=105
    )

    y=df_drees_completement_vaccines["nb_PCR+"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees_reg.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " cas positifs<br>complètement vaccinés</b><br>/ 10 Mio de vaccinés",
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=105,
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal.</i>",
        font=dict(size=9),
        showarrow=False,
        yshift=30
    )
    fig.update_yaxes(title="Cas positifs quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees_reg.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees_reg.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = "pcr_plus_proportion_selon_statut_vaccinal"
    fig.write_image(PATH + "images/charts/france/regions_dashboards/{}.jpeg".format(name_fig+"_"+region), scale=1.5, width=900, height=600)
    


# In[10]:


def adm_hc_statut_vaccinal(region):
    df_drees_reg = df_drees_regions[df_drees_regions["regionName"] == region]
    df_drees_reg = df_drees_reg.sort_values(by="date")
    
    df_drees_non_vaccines = df_drees_reg[df_drees_reg["vac_statut"]=="Non-vaccinés"]
    df_drees_non_vaccines["effectif J-7"] = df_drees_non_vaccines["effectif J-7"].rolling(window=7).mean()

    df_drees_completement_vaccines = df_drees_reg[df_drees_reg["vac_statut"].isin(["Vaccination complète",])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines["effectif J-7"] = df_drees_completement_vaccines["effectif J-7"].rolling(window=7).mean()

    df_drees_partiellement_vaccines = df_drees_reg[df_drees_reg["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
    df_drees_partiellement_vaccines["effectif J-7"] = df_drees_partiellement_vaccines["effectif J-7"].rolling(window=7).mean()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_drees_non_vaccines["date"].values,
            y=df_drees_non_vaccines["HC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df_drees_non_vaccines["date"].values[-1]],
            y=[(df_drees_non_vaccines["HC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_drees_partiellement_vaccines["date"].values,
            y=df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df_drees_partiellement_vaccines["date"].values[-1]],
            y=[(df_drees_partiellement_vaccines["HC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_drees_completement_vaccines["date"].values,
            y=df_drees_completement_vaccines["HC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[df_drees_completement_vaccines["date"].values[-1]],
            y=[(df_drees_completement_vaccines["HC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
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
                            'text': "<b>Admissions à l'hôpital</b> pour Covid - " + region,
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
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees_reg.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    y=df_drees_non_vaccines["HC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees_reg.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " admissions<br>non vaccinées</b><br>/ 10 Mio de non vaccinés",
        font=dict(color=COULEUR_NON_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=105
    )

    y=df_drees_completement_vaccines["HC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees_reg.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " admissions<br>complètement vaccinées</b><br>/ 10 Mio de vaccinés",
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=105,
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Hospitalisation pour suspicion Covid.</i>",
        font=dict(size=9),
        showarrow=False,
        yshift=30
    )
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees_reg.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees_reg.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = "hc_proportion_selon_statut_vaccinal"
    fig.write_image(PATH + "images/charts/france/regions_dashboards/{}.jpeg".format(name_fig+"_"+region), scale=1.5, width=900, height=600)
    


# In[11]:


def adm_sc_statut_vaccinal(region):
    df_drees_reg = df_drees_regions[df_drees_regions["regionName"] == region]
    df_drees_reg = df_drees_reg.sort_values(by="date")
    
    df_drees_non_vaccines = df_drees_reg[df_drees_reg["vac_statut"]=="Non-vaccinés"]
    df_drees_non_vaccines["effectif J-7"] = df_drees_non_vaccines["effectif J-7"].rolling(window=7).mean()

    df_drees_completement_vaccines = df_drees_reg[df_drees_reg["vac_statut"].isin(["Vaccination complète",])].groupby("date").sum().reset_index()
    df_drees_completement_vaccines["effectif J-7"] = df_drees_completement_vaccines["effectif J-7"].rolling(window=7).mean()

    df_drees_partiellement_vaccines = df_drees_reg[df_drees_reg["vac_statut"].isin(["Primo dose récente", "Primo dose efficace"])].groupby("date").sum().reset_index()
    df_drees_partiellement_vaccines["effectif J-7"] = df_drees_partiellement_vaccines["effectif J-7"].rolling(window=7).mean()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_drees_non_vaccines["date"].values,
            y=df_drees_non_vaccines["SC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000,
            name="Non vaccinés",
            line_color="#C65102",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df_drees_non_vaccines["date"].values[-1]],
            y=[(df_drees_non_vaccines["SC"].rolling(window=7).mean() / df_drees_non_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Non vaccinés",
            line_color="#C65102",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_drees_partiellement_vaccines["date"].values,
            y=df_drees_partiellement_vaccines["SC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000,
            name="Partiellement vaccinés",
            line_color="#4777d6",
            line_width=4
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df_drees_partiellement_vaccines["date"].values[-1]],
            y=[(df_drees_partiellement_vaccines["SC"].rolling(window=7).mean() / df_drees_partiellement_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Partiellement vaccinés",
            line_color="#4777d6",
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_drees_completement_vaccines["date"].values,
            y=df_drees_completement_vaccines["SC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000,
            name="Vaccinés",
            line_color="#00308F",
            line_width=4
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[df_drees_completement_vaccines["date"].values[-1]],
            y=[(df_drees_completement_vaccines["SC"].rolling(window=7).mean() / df_drees_completement_vaccines["effectif J-7"] * 10000000).values[-1]],
            name="Vaccinés",
            line_color="#00308F",
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
                            'text': "<b>Admissions en soins critiques</b> pour Covid - " + region,
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
                                text="selon le statut vaccinal, pour 10 Mio hab. de chaque groupe - {}<br>Données DREES - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df_drees_reg.date.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                                showarrow=False
                            ),
                            ]
    )
    y=df_drees_non_vaccines["SC"].rolling(window=7).mean().values[-1] / df_drees_non_vaccines["effectif J-7"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees_reg.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " admissions<br>non vaccinées</b><br>/ 10 Mio de non vaccinés",
        font=dict(color=COULEUR_NON_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=105
    )

    y=df_drees_completement_vaccines["SC"].rolling(window=7).mean().values[-1] / df_drees_completement_vaccines["effectif J-7"].values[-1] * 10000000
    fig.add_annotation(
        x=df_drees_reg.date.max(),
        y=y,
        text="<b>" + str(int(round(y))) + " admissions<br>complètement vaccinées</b><br>/ 10 Mio de vaccinés",
        font=dict(color=COULEUR_COMPLETEMENT_VACCINES),
        showarrow=False,
        align="left",
        yshift=0,
        xshift=105,
    )

    fig.add_annotation(
        x=0.5,
        y=-0.225,
        xref='paper',
        yref='paper',
        text="<i>Une personne est considérée comme vaccinée après avoir terminé son schéma vaccinal. Hospitalisations pour suspicion Covid.</i>",
        font=dict(size=9),
        showarrow=False,
        yshift=30
    )
    fig.update_yaxes(title="Admissions quot. / 10 Mio hab. de chaque groupe")
    fig.update_xaxes(tickformat="%d/%m", range=[datetime.strptime(df_drees_reg.date.min(), '%Y-%m-%d') + timedelta(days=5), 
                                                datetime.strptime(df_drees_reg.date.max(), '%Y-%m-%d') + timedelta(days=2)])
    name_fig = "sc_proportion_selon_statut_vaccinal"
    fig.write_image(PATH + "images/charts/france/regions_dashboards/{}.jpeg".format(name_fig+"_"+region), scale=1.5, width=900, height=600)
    


# In[11]:


def cas_journ(region):
        
    df_incid_reg = df_incid_regions[df_incid_regions["regionName"] == region]
    df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    df_tests_reg_rolling = df_incid_reg["T"].rolling(window=7, center=True).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "cas_journ_"+region, [0, df_incid_reg["P"].max()]
    title = "<b>Cas positifs</b> au Covid19 - <b>" + region + "</b>"

    #fig = go.Figure()
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x = df_incid_reg["jour"],
        y = df_incid_reg_rolling,
        name = "",
        marker_color='rgb(8, 115, 191)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(8, 115, 191, 0.3)",
        showlegend=False
    ), secondary_y=True)
    
    fig.add_trace(go.Scatter(
        x = [dates_incid[-4]],
        y = [df_incid_reg_rolling.values[-4]],
        name = "",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ), secondary_y=True)

    """fig.add_trace(go.Scatter(
        x = df_incid_reg["jour"],
        y = df_incid_reg["P"],
        name = "",
        mode="markers",
        marker_color='rgb(8, 115, 191)',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ), secondary_y=True)"""
    
    fig.add_trace(go.Bar(
        x = df_incid_reg["jour"],
        y = df_tests_reg_rolling,
        name = "Tests réalisés",
        marker_color='rgba(0, 0, 0, 0.2)',
        opacity=0.8,
        showlegend=False,
    ), secondary_y=False)

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), secondary_y=True)
    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), secondary_y=False)
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.93,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates_incid[-4], y = df_incid_reg_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y2',
            text=" <b>{} {}".format('%d' % df_incid_reg_rolling.values[-4], "cas quotidiens<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=0,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(8, 115, 191)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-250,
            ay=-70,
            arrowcolor="rgb(8, 115, 191)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),dict(
            x = dates_incid[-4], y = df_tests_reg_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_tests_reg_rolling.values[-4], "tests réalisés<br></b>en moyenne du {} au {}.".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgba(0, 0, 0, 0.5)",
                size=13
                ),
            bgcolor="rgba(255, 255, 255, 0.4)",
            opacity=1,
            ax=-250,
            ay=-70,
            arrowcolor="rgba(0, 0, 0, 0.5)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ))

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1.2, width=900, height=600)

    print("> " + name_fig)
    
#cas_journ("Auvergne-Rhône-Alpes")


# In[12]:


def hosp_journ(region):   
    df_reg = df_regions[df_regions["regionName"] == region]
    df_new_reg = df_new_regions[df_new_regions["regionName"] == region]
    #df_incid_reg_rolling = df_incid_reg["P"].rolling(window=7, center=True).mean()
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "hosp_journ_"+region
    title = "<b>Personnes hospitalisées</b> pour Covid19 - <b>" + region + "</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
        y = df_reg["hosp"],
        name = "",
        marker_color='rgb(209, 102, 21)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_reg["hosp"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_new_reg["jour"],
        y = df_new_reg["incid_hosp"],
        name = "Admissions hosp.",
        marker_color='rgb(209, 102, 21)',
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_reg["jour"],
        y = df_new_reg["incid_hosp"].rolling(window=7).mean(),
        name = "Admissions hosp.",
        marker_color='rgb(209, 102, 21)',
        #mode="lines"
        line_width=2,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.93,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_reg["hosp"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_reg["hosp"].values[-1], "personnes<br>hospitalisées</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-250,
            ay=-90,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = df_new_reg["jour"].values[-1], y = (df_new_reg["incid_hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_reg["incid_hosp"].values[-1], "<br>admissions"),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=10
                ),
            opacity=0.8,
            ax=-20,
            ay=-40,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1.2, width=900, height=600)

    print("> " + name_fig)


# In[13]:


def hosp_journ_elias(reg):
    df_new_reg = df_new_regions[df_new_regions["regionName"]==reg]
    
    entrees_rolling = df_new_reg["incid_hosp"].rolling(window=7).mean().values
    
    rad_rolling = df_new_reg["incid_rad"].rolling(window=7).mean()
    dc_rolling = df_new_reg["incid_dc"].rolling(window=7).mean()
    sorties_rolling = (rad_rolling + dc_rolling).values

    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "hosp_journ_flux_"+reg, [0, 1.1*max( max(np.nan_to_num(entrees_rolling)), max(np.nan_to_num(sorties_rolling)))]
    title = "<b>Entrées et sorties de l'hôpital</b> pour Covid19 • <b>" + reg + "</b>"
    
    for i in [""]:
        if i=="log":
            title+= " [log.]"

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x = dates,
            y = entrees_rolling,
            name = "",
            marker_color='red',
            line_width=6,
            opacity=1,
            fill='tozeroy',
            fillcolor="rgba(235, 64, 52,0.5)",
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x = dates,
            y = sorties_rolling,
            name = "",
            marker_color='green',
            line_width=0,
            opacity=1,
            fill='tozeroy',
            fillcolor="rgba(12, 161, 2, 0.5)",
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x = dates,
            y = [entrees_rolling[i] if entrees_rolling[i]<sorties_rolling[i] else sorties_rolling[i] for i in range(len(entrees_rolling))],
            name = "",
            marker_color='yellow',
            line_width=0,
            opacity=1,
            fill='tozeroy',
            fillcolor="rgba(255, 255, 255, 1)",
            showlegend=False
        ))

        
        fig.add_trace(go.Scatter(
            x = dates,
            y = sorties_rolling,
            name = "",
            marker_color='green',
            line_width=6,
            opacity=1,
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x = dates,
            y =entrees_rolling,
            name = "",
            marker_color='red',
            line_width=6,
            opacity=1,
            showlegend=False
        ))

        fig.add_shape(type="line",
        x0="2020-03-17", y0=0, x1="2020-03-17", y1=300000,
        line=dict(color="Red",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-05-11", y0=0, x1="2020-05-11", y1=300000,
        line=dict(color="Green",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-10-30", y0=0, x1="2020-10-30", y1=300000,
        line=dict(color="Red",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-11-28", y0=0, x1="2020-11-28", y1=300000,
        line=dict(color="Orange",width=0.5, dash="dot")
        )

        fig.add_shape(type="line",
        x0="2020-12-15", y0=0, x1="2020-12-15", y1=300000,
        line=dict(color="green",width=0.5, dash="dot")
        )

        fig.add_trace(go.Scatter(
            x = [dates[-1]],
            y = [sorties_rolling[-1]],
            name = "",
            mode="markers",
            marker_color='green',
            marker_size=13,
            opacity=1,
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x = [dates[-1]],
            y = [entrees_rolling[-1]],
            name = "",
            mode="markers",
            marker_color='red',
            marker_size=13,
            opacity=1,
            showlegend=False
        ))

        ###
        fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), ) #range=["2020-03-17", last_day_plot_dashboard]
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y)
        
        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(
            paper_bgcolor='rgba(255,255,255,1)',
            plot_bgcolor='rgba(255,255,255,1)',
            margin=dict(
                    l=50,
                    r=150,
                    b=50,
                    t=70,
                    pad=0
                ),
            legend_orientation="h",
            barmode='group',
            title={
                        'text': title,
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        titlefont = dict(
                        size=30),
            xaxis=dict(
                    title='',
                    tickformat='%d/%m'),

            annotations = [
                        dict(
                            x=0.5,
                            y=1.01,
                            font=dict(size=14),
                            xref='paper',
                            yref='paper',
                            text="Moyenne mobile 7 jours. Données Santé publique France. Auteurs @eorphelin @guillaumerozier - <b>covidtracker.fr</b>.", #'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    
                            showarrow = False
                        ),

                        ]
                    )

        if entrees_rolling[-1]<sorties_rolling[-1]:
            y_e = -20
            y_s = -100
        else:
            y_e = -100
            y_s = -20
            
        fig['layout']['annotations'] += (
            dict(
            x = "2020-05-20", y = (entrees_rolling[62]+sorties_rolling[62])/2, # annotation point
            xref='x1', 
            yref='y1',
            text="L'aire représente le solde.<br>Si elle est <span style='color:green'>verte</span>, il y a plus de sorties que d'entrées,<br>le nombre de lits occupés diminue.",
            xshift=0,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=10
                ),
            bgcolor="rgba(255, 255, 255, 0)",
            opacity=0.8,
            ax=80,
            ay=-100,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=6,
            showarrow=True
        ),
            dict(
                x = dates[-1], y = (entrees_rolling[-1]), # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{} {}".format(round(entrees_rolling[-1], 1), "entrées à l'hôpital</b><br>en moyenne le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="red",
                    size=12
                    ),
                bgcolor="rgba(255, 255, 255, 0)",
                opacity=0.8,
                ax=100,
                ay=y_e,
                arrowcolor="red",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
            dict(
                x = dates[-1], y = (sorties_rolling[-1]), # annotation point
                xref='x1', 
                yref='y1',
                text=" <b>{} {}".format(round(sorties_rolling[-1], 1), "sorties de l'hôpital</b><br>en moyenne le {}.<br>dont {} décès et<br>{} retours à domicile".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), round(dc_rolling.values[-1], 1), round(rad_rolling.values[-1], 1))),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="green",
                    size=12
                    ),
                bgcolor="rgba(255, 255, 255, 0)",
                opacity=0.8,
                ax=100,
                ay=y_s,
                arrowcolor="green",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ), 
                dict(
                x = "2020-10-30", y = 40000, # annotation point
                xref='x1', 
                yref='y1',
                text="Confinement",
                xanchor="left",
                yanchor="top",
                align='center',
                font=dict(
                    color="red",
                    size=8
                    ),
                showarrow=False
            ),
              dict(
                x = "2020-05-11", y = 40000, # annotation point
                xref='x1', 
                yref='y1',
                text="Déconfinement",
                xanchor="left",
                yanchor="top",
                align='center',
                font=dict(
                    color="green",
                    size=8
                    ),
                showarrow=False
            ),
               dict(
                x=0.5,
                y=-0.1,
                font=dict(size=10),
                xref='paper',
                yref='paper',
                text="",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                showarrow=False
                        ))

        fig.write_image(PATH + "images/charts/france/regions_dashboards/{}.jpeg".format(name_fig+i), scale=1.5, width=1100, height=600)

        #plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/departements_dashboards/{}.html'.format(name_fig+i), auto_open=False)
        print("> " + name_fig)
            
#hosp_journ_elias("Nouvelle-Aquitaine")


# In[14]:


def rea_journ(region):
    df_reg = df_regions[df_regions["regionName"] == region]
    df_new_reg = df_new_regions[df_new_regions["regionName"] == region]
    
    range_x, name_fig = ["2020-03-29", last_day_plot], "rea_journ_" + region
    title = "Personnes en <b>réanimation</b> pour Covid19 - <b>" + region + "</b>"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_reg["rea"],
        name = "",
        marker_color='rgb(201, 4, 4)',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(201, 4, 4,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_reg["rea"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_new_reg["jour"],
        y = df_new_reg["incid_rea"],
        name = "Admissions",
        marker_color='rgb(201, 4, 4)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_reg["jour"],
        y = df_new_reg["incid_rea"].rolling(window=7).mean(),
        name = "Admissions",
        marker_color='rgb(201, 4, 4)',
        marker_size=2,
        opacity=0.8,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.93,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_reg["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_reg["rea"].values[-1], "personnes<br>en réanimation</b><br>le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-250,
            ay=-90,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = df_new_reg["jour"].values[-1], y = (df_new_reg["incid_rea"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_reg["incid_rea"].values[-1], "<br>admissions"),
            xshift=-2,
            yshift=10,
            xanchor="center",
            align='center',
            font=dict(
                color='rgb(201, 4, 4)',
                size=10
                ),
            opacity=0.8,
            ax=-20,
            ay=-40,
            arrowcolor='rgb(201, 4, 4)',
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1.2, width=900, height=600)

    print("> " + name_fig)
#rea_journ("Auvergne-Rhône-Alpes")


# In[15]:


def dc_journ(region): 
    df_reg = df_new_regions[df_new_regions["regionName"] == region]
    dc_new_rolling = df_reg["incid_dc"].rolling(window=7).mean()
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ_"+region, [0, df_reg["incid_dc"].max()]
    title = "<b>Décès hospitaliers quotidiens</b> du Covid19 - <b>" + region + "</b>"

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=8,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(0,0,0,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=15,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_reg["jour"],
        y = df_reg["incid_dc"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.4,
        showlegend=False
    ))

    ###

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.93,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % math.trunc(round(dc_new_rolling.values[-1], 2)), "décès quotidiens</b><br>en moyenne<br>du {} au {}.".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-250,
            ay=-90,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1.2, width=900, height=600)

    print("> " + name_fig)


# In[16]:



def saturation_rea_journ(region):
    df_reg = df_regions[df_regions["regionName"] == region]
    df_saturation = 100 * df_reg["rea"] / df_reg["LITS_y"]
    
    range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "saturation_rea_journ_"+region, [0, df_saturation.max()*1.2]
    title = "<b>Occupation des réa.</b> par les patients Covid19 - <b>" + region + "</b>"

    fig = go.Figure()

    colors_sat = ["green" if val < 60 else "red" if val > 100  else "orange" for val in df_saturation.values]
    fig.add_trace(go.Bar(
        x = dates,
        y = df_saturation,
        name = "Nouveaux décès hosp.",
        marker_color=colors_sat,
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_shape(
            type="line",
            x0="2019-03-15",
            y0=100,
            x1="2022-01-01",
            y1=100,
            opacity=1,
            fillcolor="orange",
            line=dict(
                color="red",
                width=1,
            )
        )

    fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-15", last_day_plot])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=0,
                b=50,
                t=70,
                pad=0
            ),
        legend_orientation="h",
        barmode='group',
        title={
                    'text': title,
                    'y':0.93,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    titlefont = dict(
                    size=20),
        xaxis=dict(
                title='',
                tickformat='%d/%m'),

        annotations = [
                    dict(
                        x=0,
                        y=1,
                        xref='paper',
                        yref='paper',
                        font=dict(size=15),
                        text='{}. Données : Santé publique France. <b>@GuillaumeRozier - covidtracker.fr</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                    ),
                    ]
                     )

    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_saturation.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % df_saturation.values[-1], " %</b> des lits de réa. occupés par<br>des patients Covid19 le {}.".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'))),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color=colors_sat[-1],
                size=20
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=1,
            ax=-250,
            ay=-20,
            arrowcolor=colors_sat[-1],
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),)

    fig.write_image(PATH+"images/charts/france/regions_dashboards/{}.jpeg".format(name_fig), scale=1.2, width=900, height=600)

    print("> " + name_fig)
    return df_saturation.values[-1]


# In[17]:


for reg in regions:
    pcr_plus_statut_vaccinal(reg)
    adm_hc_statut_vaccinal(reg)
    adm_sc_statut_vaccinal(reg)


# In[18]:


import cv2
dict_saturation = {}

for reg in regions:
    dict_saturation[reg] = round(saturation_rea_journ(reg), 1)
    
    hosp_journ_elias(reg)
    saturation_rea_journ(reg)
    cas_journ(reg)
    hosp_journ(reg)
    rea_journ(reg)
    dc_journ(reg)

    im1 = cv2.imread(PATH+'images/charts/france/regions_dashboards/cas_journ_{}.jpeg'.format(reg))
    im2 = cv2.imread(PATH+'images/charts/france/regions_dashboards/hosp_journ_{}.jpeg'.format(reg))
    im3 = cv2.imread(PATH+'images/charts/france/regions_dashboards/rea_journ_{}.jpeg'.format(reg))
    im4 = cv2.imread(PATH+'images/charts/france/regions_dashboards/dc_journ_{}.jpeg'.format(reg))

    im_haut = cv2.hconcat([im1, im2])
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite(PATH+'images/charts/france/regions_dashboards/dashboard_jour_{}.jpeg'.format(reg), im_totale)
    
    os.remove(PATH+'images/charts/france/regions_dashboards/cas_journ_{}.jpeg'.format(reg))
    os.remove(PATH+'images/charts/france/regions_dashboards/hosp_journ_{}.jpeg'.format(reg))
    os.remove(PATH+'images/charts/france/regions_dashboards/rea_journ_{}.jpeg'.format(reg))
    os.remove(PATH+'images/charts/france/regions_dashboards/dc_journ_{}.jpeg'.format(reg))

with open(PATH_STATS + 'saturation_rea_regions.json', 'w') as outfile:
    json.dump(dict_saturation, outfile)


# In[19]:


n_tot=4
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

for i in range(0, n_tot):
    evol_tests_regs, evol_hosp_regs = [], []

    fig = go.Figure()

    fig.add_shape(type="rect",
            x0=-1000, y0=0, x1=0, y1=1000,
            line=dict(color="orange",width=0.5, dash="dot"), fillcolor="orange", opacity=0.2,
            layer="below"
        )
    fig.add_shape(type="rect",
            x0=0, y0=-1000, x1=1000, y1=0,
            line=dict(color="orange",width=0.5, dash="dot"), fillcolor="orange", opacity=0.2,
            layer="below"
        )

    fig.add_shape(type="rect",
            x0=0, y0=0, x1=1000, y1=1000,
            line=dict(color="Red",width=0.5, dash="dot"), fillcolor="red", opacity=0.2,
            layer="below"
        )

    fig.add_shape(type="rect",
            x0=-1000, y0=-1000, x1=0, y1=0,
            line=dict(color="red",width=0.5, dash="dot"), fillcolor="green", opacity=0.2,
            layer="below"
        )

    regs_vert, regs_orange, regs_rouge = "", "", ""
    nb_vert, nb_orange, nb_rouge = 0, 0, 0
    for reg in regions:
        df_incid_reg = df_incid_regions[df_incid_regions["regionName"]==reg]
        tests_reg_rolling = df_incid_reg["P"].rolling(window=7).mean().values
        evol_tests_reg = (tests_reg_rolling[-1-i] - tests_reg_rolling[-8-i]) / tests_reg_rolling[-8] * 100
        evol_tests_regs += [evol_tests_reg]

        hosp_reg_rolling = df_new_regions[df_new_regions["regionName"]==reg]["incid_hosp"].rolling(window=7).mean().values
        evol_hosp_reg = ( hosp_reg_rolling[-1-i] - hosp_reg_rolling[-8-i]) / hosp_reg_rolling[-8] * 100
        evol_hosp_regs += [evol_hosp_reg]

        if (evol_tests_reg < 0) & (evol_hosp_reg<0):
            color = "green"
            regs_vert += df_incid_reg["regionName"].values[0] + ", "
            nb_vert += 1

        elif (evol_tests_reg > 0) & (evol_hosp_reg > 0):
            color = "red"
            regs_rouge += df_incid_reg["regionName"].values[0] + ", "
            nb_rouge += 1

        else:
            color = "orange"
            regs_orange += df_incid_reg["regionName"].values[0] + ", "
            nb_orange += 1

        fig.add_trace(go.Scatter(
            x = [evol_tests_reg],
            y = [evol_hosp_reg],
            name = reg,
            text=[df_incid_reg["regionName"].values[0][:4]+"."],
            marker_color=color,
            marker_size=20,
            line_width=8,
            opacity=0.8,
            fill='tozeroy',
            mode='markers+text',
            fillcolor="rgba(8, 115, 191, 0.3)",
            textfont_color="black",
            showlegend=False,
            textposition="middle center"
        ))

    liste_deps_str = "{} en <b>vert</b> : {}<br><br>{} en <b>orange</b> : {}<br><br>{} en <b>rouge</b> : {}".format(nb_vert, regs_vert, nb_orange, regs_orange, nb_rouge, regs_rouge)

    fig['layout']['annotations'] += (dict(
            x = 50, y = 50, # annotation point
            xref='x1', yref='y1',
            text="Les cas augmentent.<br>Les admissions à l'hôpital augmentent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = -50, y = -50, # annotation point
            xref='x1', yref='y1',
            text="Les cas baissent.<br>Les admissions à l'hôpital baissent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = -50, y = 50, # annotation point
            xref='x1', yref='y1',
            text="Les cas baissent.<br>Les admissions à l'hôpital augmentent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
            x = 50, y = -50, # annotation point
            xref='x1', yref='y1',
            text="Les cas augmentent.<br>Les admissions à l'hôpital baissent.",
            xanchor="center",align='center',
            font=dict(
                color="black", size=10
                ),
            showarrow=False
        ),dict(
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                font=dict(size=14),
                text='{}. Données : Santé publique France. Auteur : <b>@GuillaumeRozier - covidtracker.fr.</b>'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %b')),                    showarrow = False
                        ),
            dict(
                x=-0.08,
                y=-0.3,
                xref='paper',
                yref='paper',
                font=dict(size=14),
                align="left",
                text=liste_deps_str[:150]+"<br>"+liste_deps_str[151:], showarrow = False
          ),)

    fig.update_xaxes(title="Évolution hebdomadaire des cas positifs", range=[-200, 200], ticksuffix="%")
    fig.update_yaxes(title="Évolution hedbomadaire des admissions à l'hôpital", range=[-200, 200], ticksuffix="%")
    fig.update_layout(
         title={
                        'text': "<b>Évolution des cas et hospitalisations dans les régions</b> • {}".format(datetime.strptime(dates[-i-1], '%Y-%m-%d').strftime('%d %b')),
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
        titlefont = dict(
                    size=20),
        margin=dict(
            b=200
        ),
        )
    fig.write_image(PATH+"images/charts/france/evolution_regs/{}_{}.jpeg".format("evolution_regs", i), scale=3, width=1000, height=900)


# In[20]:


"""for reg in regions:
    
    heading = "<!-- wp:heading --><h2 id=\"{}\">{}</h2><!-- /wp:heading -->\n".format(reg, reg)
    string = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/dashboard_jour_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/dashboard_jour_{}.jpeg\" width=\"100%\"> </a></p><br>\n".format(reg, reg)
    string2 = "<p align=\"center\"> <a href=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/saturation_rea_journ_{}.jpeg\" target=\"_blank\" rel=\"noopener noreferrer\"><img src=\"https://raw.githubusercontent.com/rozierguillaume/covid-19/master/images/charts/france/regions_dashboards/saturation_rea_journ_{}.jpeg\" width=\"70%\"> </a></p>\n".format(reg, reg)

    space = "<!-- wp:spacer {\"height\":50} --><div style=\"height:50px\" aria-hidden=\"true\" class=\"wp-block-spacer\"></div><!-- /wp:spacer -->"
    retourmenu="<a href=\"#Menu\">Retour au menu</a>"
    print(space+retourmenu+heading+string+string2)
"""


# In[21]:


"""print("<!-- wp:buttons --><div class=\"wp-block-buttons\">\n")
#for reg in regions:
    print("""#<!-- wp:button {"className":"is-style-outline"} -->
    #<div class="wp-block-button is-style-outline">""")
    
    #print("<a class=\"wp-block-button__link\" href=\"#{}\">".format(reg))
    
    #print("{}</a></div><!-- /wp:button --></div>\n".format(reg))
#print("<!-- /wp:buttons -->")"""

