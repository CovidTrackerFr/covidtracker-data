#!/usr/bin/env python
# coding: utf-8

# In[116]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
import datetime as dt
PATH = "../../"


# In[117]:


df_vacsi = data.import_data_vacsi_fra()


# In[118]:


date_5_mois = (pd.to_datetime(df_vacsi["jour"].max()) - dt.timedelta(days=30*5)).strftime(format="%Y-%m-%d")
date_6_mois = (pd.to_datetime(df_vacsi["jour"].max()) - dt.timedelta(days=30*6)).strftime(format="%Y-%m-%d")


# In[119]:


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


# In[120]:


df_vacsi[df_vacsi["jour"] == date_5_mois]
df_vacsi[df_vacsi["jour"] == date_6_mois]


# In[121]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_vacsi.jour,
        y=df_vacsi.n_cum_rappel,
        marker_color="orange",
        name="Cumul doses de rappel effectuées"
    )
)

fig.add_trace(
    go.Scatter(
        x=df_vacsi.jour,
        y=df_vacsi.n_cum_dose1.shift(30*6),
        marker_color="blue",
        name="Cumul schéma vaccinal complet il y a 6 mois"
        
    )
)

fig.add_trace(
    go.Scatter(
        x=df_vacsi.jour,
        y=df_vacsi.n_cum_dose1.shift(30*5),
        #marker_color="darkblue",
        fill="tonexty",
        fillcolor="lightblue",
        #name="Schéma vaccinal complet il y a 5 mois",
        showlegend=False
        
    )
)

fig.add_trace(
    go.Scatter(
        x=df_vacsi.jour,
        y=df_vacsi.n_cum_dose1.shift(30*5),
        marker_color="darkblue",
        fillcolor="rgba(0, 0, 0)",
        name="Cumul schéma vaccinal complet il y a 5 mois",
        
        
    )
)

fig.add_annotation(
    x=df_vacsi.jour.max(),
    y=df_vacsi.n_cum_rappel.max(),
    xshift=100,
    yshift=0,
    align="left",
    showarrow=False,
    text=f"<b>{round(df_vacsi.n_cum_rappel.max()/1000000, 1)}</b> Mio de Français ont reçu<br>une <b>dose de rappel</b>".replace(".", ",")
)
nb_pers_5_mois = round(df_vacsi.n_cum_dose1.shift(30*5).max() / 1000000, 1)
nb_pers_6_mois = round(df_vacsi.n_cum_dose1.shift(30*6).max() / 1000000, 1)

fig.add_annotation(
    x=df_vacsi.jour.max(),
    xshift=125,
    yshift=0,
    align="left",
    showarrow=False,
    y=(df_vacsi.n_cum_dose1.shift(30*5).max() + df_vacsi.n_cum_dose1.shift(30*6).max())/2,
    text=f"Entre <b>{nb_pers_6_mois}</b> et <b>{nb_pers_5_mois}</b> Mio de Français<br>ont <b>débuté leur schema vaccinal</b><br>il y a <b>plus de 5 mois</b> et <b>moins de 6 mois</b>".replace(".", ",")
)

fig.add_annotation(
    x=0.62,
    y=1.12,
    xref='paper',
    yref='paper',
    font=dict(size=14),
    text="Données Ministère de la Santé - @GuillaumeRozier - covidtracker.fr",
    showarrow = False
    )

fig.update_xaxes(range=[date_6_mois, df_vacsi.jour.max()])

fig.update_layout(
    legend_orientation="h",
    margin=dict(
            r=250
        ),
    title={
            'text': "Nombre de Français <b>vaccinés il y a plus de 5 mois</b>",
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'font': {'size': 25},
            'yanchor': 'top'},
)
fig.write_image(PATH + "images/charts/france/{}.jpeg".format("vaccination_rappel_comparaison_5_6_mois"), scale=2, width=1000, height=600)

