#!/usr/bin/env python
# coding: utf-8

# In[62]:


import pandas as pd
import plotly.graph_objects as go
import france_data_management as data
import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
PATH = "../../"


# In[63]:


df_vacsi = data.import_data_vacsi_fra()


# In[ ]:





# In[64]:


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


# In[185]:


fig = go.Figure()

DATE_DEBUT = "2021-09-01"
date_5_mois = (pd.to_datetime(DATE_DEBUT) - relativedelta(months=5) - timedelta(days=2)).strftime(format="%Y-%m-%d")
date_7_mois = (pd.to_datetime(DATE_DEBUT) - relativedelta(months=7) - timedelta(days=2)).strftime(format="%Y-%m-%d")
MI_JANVIER_MOINS_7_MOIS = (pd.to_datetime("2022-01-15") - relativedelta(months=7)).strftime(format="%Y-%m-%d")

dates_rappel_comparaison = [(dt.datetime.strptime(DATE_DEBUT, "%Y-%m-%d") + timedelta(days=n)).strftime("%Y-%m-%d") for n in range(0, 150)]

fig.add_trace(
    go.Scatter(
        x=dates_rappel_comparaison,
        y=df_vacsi[df_vacsi["jour"]>=date_7_mois].n_cum_complet,
        marker_color="blue",
        line_width=3,
        name="Cumul schéma vaccinal complet il y a 7 mois"
        
    )
)

fig.add_trace(
    go.Scatter(
        x=dates_rappel_comparaison,
        y=df_vacsi[df_vacsi["jour"]>=date_5_mois].n_cum_complet,
        line_width=3,
        fill="tonexty",
        fillcolor="lightblue",
        showlegend=False
        
    )
)

fig.add_trace(
    go.Scatter(
        x=dates_rappel_comparaison,
        y=df_vacsi[df_vacsi["jour"]>=date_5_mois].n_cum_complet,
        marker_color="darkblue",
        line_width=3,
        fillcolor="rgba(0, 0, 0)",
        name="Cumul schéma vaccinal complet il y a 5 mois",
        
        
    )
)

fig.add_trace(
    go.Scatter(
        x=dates_rappel_comparaison,
        y=df_vacsi[df_vacsi["jour"]>=DATE_DEBUT].n_cum_rappel,
        marker_color="orange",
        line_width=3,
        name="Cumul doses de rappel effectuées"
    )
)

fig.add_annotation(
    x=df_vacsi.jour.max(),
    y=df_vacsi.n_cum_rappel.max(),
    xshift=0,
    ax=-100,
    ay=0,
    yshift=0,
    align="left",
    arrowhead=6,
    bgcolor="rgba(255, 255, 255, 0.5)",
    font=dict(size=9),
    showarrow=True,
    text=f"<b>{round(df_vacsi.n_cum_rappel.max()/1000000, 1)}</b> Mio de Français ont reçu<br>une <b>dose de rappel</b>".replace(".", ",")
)

now_5_mois = (pd.to_datetime(df_vacsi["jour"].max()) - relativedelta(months=5)).strftime(format="%Y-%m-%d")
now_7_mois = (pd.to_datetime(df_vacsi["jour"].max()) - relativedelta(months=7)).strftime(format="%Y-%m-%d")
nb_pers_5_mois = round(df_vacsi[df_vacsi["jour"]<=now_5_mois].n_cum_complet.max() / 1000000, 1)
nb_pers_7_mois = round(df_vacsi[df_vacsi["jour"]<=now_7_mois].n_cum_complet.max() / 1000000, 1)

fig.add_annotation(
    x=df_vacsi.jour.max(),
    xshift=0,
    yshift=0,
    ax=-20,
    ay=-60,
    align="left",
    arrowhead=6,
    showarrow=True,
    bgcolor="rgba(255, 255, 255, 0.5)",
    font=dict(size=9),
    y=(df_vacsi.n_cum_complet.shift(30*5).max() + df_vacsi.n_cum_complet.shift(30*7).max())/2,
    text=f"Entre <b>{nb_pers_7_mois}</b> et <b>{nb_pers_5_mois}</b> Mio de Français<br>ont <b>terminé leur schema vaccinal</b><br>il y a <b>plus de 5 mois</b> et <b>moins de 7 mois</b>".replace(".", ",")
)

nb_francais_rappel_15_janvier = df_vacsi[df_vacsi["jour"]==MI_JANVIER_MOINS_7_MOIS].n_cum_complet.values[0]

fig.add_annotation(
    x="2022-01-15",
    xshift=0,
    yshift=0,
    ax=0,
    ay=60,
    align="left",
    arrowhead=6,
    showarrow=True,
    bgcolor="rgba(255, 255, 255, 0.5)",
    y=nb_francais_rappel_15_janvier,
    font=dict(size=9),
    text=f"<b>{round(nb_francais_rappel_15_janvier/1000000, 1)}</b> Mio de Français<br>devront avoir effectué<br>leur rappel le 15/01".replace(".", ",")
)


fig.add_annotation(
    x=0.5,
    y=1.12,
    xref='paper',
    yref='paper',
    font=dict(size=14),
    text="Données Ministère de la Santé - @GuillaumeRozier - covidtracker.fr",
    showarrow = False
    )

fig.update_layout(
    legend_orientation="h",
    margin=dict(
            r=30
        ),
    title={
            'text': "Nombre de Français <b>vaccinés il y a plus de 5 mois</b>",
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'font': {'size': 25},
            'yanchor': 'top'},
)
fig.write_image(PATH + "images/charts/france/{}.jpeg".format("vaccination_rappel_comparaison_5_7_mois"), scale=2, width=800, height=600)


# In[190]:


fig = go.Figure()

DATE_DEBUT = "2021-07-01"
DATE_DEBUT_DT = dt.datetime.strptime(DATE_DEBUT, "%Y-%m-%d")
date_5_mois = (pd.to_datetime(DATE_DEBUT) - relativedelta(months=5) - timedelta(days=2)).strftime(format="%Y-%m-%d")
date_7_mois = (pd.to_datetime(DATE_DEBUT) - relativedelta(months=7) - timedelta(days=2)).strftime(format="%Y-%m-%d")
MI_JANVIER_MOINS_7_MOIS = (pd.to_datetime("2022-01-15") - relativedelta(months=7)).strftime(format="%Y-%m-%d")

n_days = (dt.datetime.strptime(df_vacsi["jour"].max(), "%Y-%m-%d") - DATE_DEBUT_DT).days
dates_rappel_comparaison = [(DATE_DEBUT_DT + timedelta(days=n)).strftime("%Y-%m-%d") for n in range(0, n_days+1)]

fig.add_trace(
    go.Scatter(
        x=df_vacsi["jour"],
        y=df_vacsi.n_cum_dose1,
        marker_color="rgba(170, 201, 227, 1)",
        fillcolor="rgba(170, 201, 227, 1)",
        line_width=0,
        fill="tozeroy",
        name="Vaccinés partiellement"
    )
)

fig.add_trace(
    go.Scatter(
        x=df_vacsi["jour"],
        y=df_vacsi.n_cum_complet,
        marker_color="rgba(70, 148, 224, 1)",
        fillcolor="rgba(70, 148, 224, 1)",
        fill="tozeroy",
        line_width=0,
        name="Vaccinés complètement"
    )
)

fig.add_trace(
    go.Scatter(
        x=dates_rappel_comparaison,
        y=df_vacsi[df_vacsi["jour"]>=date_5_mois].n_cum_complet,
        marker_color="rgba(181, 220, 245, 1)",
        fillcolor="rgba(181, 220, 245, 1)",
        line=dict(width=1, dash="dot"),
        name="Éligibles au rappel",
    )
)


fig.add_trace(
    go.Scatter(
        x=dates_rappel_comparaison,
        y=df_vacsi[df_vacsi["jour"]>=DATE_DEBUT].n_cum_rappel,
        marker_color="rgba(52, 116, 184, 1)",
        fillcolor="rgba(52, 116, 184, 1)",
        fill="tozeroy",
        line_width=0,
        name="Vaccinés avec rappel"
    )
)

fig.add_shape(type="line",
    x0=df_vacsi["jour"].min(), y0=67407241, x1=df_vacsi["jour"].max(), y1=67407241,
    line=dict(color="black",width=1, dash="dot")
)

fig.add_shape(type="line",
    x0=df_vacsi["jour"].min(), y0=57656000, x1=df_vacsi["jour"].max(), y1=57656000,
    line=dict(color="rgba(70, 148, 224, 1)",width=1, dash="dot")
)

fig.add_annotation(
    x=df_vacsi["jour"].max(),
    y=57656000+1000000,
    font=dict(size=7, color="rgba(70, 148, 224, 1)"),
    text="Français éligibles (+12 ans)",
    xanchor="right",
    showarrow = False
    )

fig.add_annotation(
    x=df_vacsi["jour"].max(),
    y=67407241-1000000,
    font=dict(size=7, color="black"),
    text="Population française",
    xanchor="right",
    showarrow = False
    )


fig.add_annotation(
    x=df_vacsi["jour"].max(),
    y=df_vacsi.n_cum_dose1.max(),
    xshift=10,
    font=dict(size=10, color="black"),
    align="left",
    text=f"<span style='color: rgba(115, 154, 186, 1);'><b>{round(df_vacsi.n_cum_dose1.max()/1000000, 1)}</b> millions<br>partiellement vaccinés<br></span>"
          f"<span style='color: rgba(70, 148, 224, 1);'><b>{round(df_vacsi.n_cum_complet.max()/1000000, 1)}</b> millions<br>complètement vaccinés</span>",
    xanchor="left",
    yanchor="top",
    showarrow = False
    
    )

fig.add_annotation(
    x=df_vacsi["jour"].max(),
    y=df_vacsi.n_cum_rappel.max(),
    xshift=10,
    font=dict(size=10, color="black"),
    align="left",
    text=f"<span style='color: rgba(52, 116, 184, 1);'><b>{round(df_vacsi.n_cum_rappel.max()/1000000, 1)}</b> millions<br>vaccinés avec rappel</span>",
    xanchor="left",
    showarrow = False
    )


fig.add_annotation(
    x=0.5,
    y=1.12,
    xref='paper',
    yref='paper',
    font=dict(size=14),
    text="Données Ministère de la Santé - @GuillaumeRozier - covidtracker.fr",
    showarrow = False
    )

fig.update_xaxes(range=[df_vacsi["jour"].min(), df_vacsi["jour"].max()])
fig.update_yaxes(rangemode="nonnegative")

fig.update_layout(
    legend_orientation="h",
    margin=dict(
            r=140
        ),
    title={
            'text': "Nombre de Français vaccinés",
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'font': {'size': 25},
            'yanchor': 'top'},
)
fig.write_image(PATH + "images/charts/france/{}.jpeg".format("vaccination_repartition"), scale=2, width=1000, height=600)

