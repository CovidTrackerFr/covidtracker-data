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


from multiprocessing import Pool
import requests
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
from datetime import datetime
from datetime import timedelta
from tqdm import tqdm
import imageio
import json
import locale
import france_data_management as data
import numpy as np
import cv2
import time
from datetime import timedelta

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
colors = px.colors.qualitative.D3 + plotly.colors.DEFAULT_PLOTLY_COLORS + px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet
show_charts = False
PATH_STATS = "../../data/france/stats/"
PATH = "../../"
now = datetime.now()
COLOR_PAPER = "rgba(225, 230, 235, 0.8)"


# In[3]:


#time.sleep(300)
data.download_data()


# In[4]:


import time

success=False
tries = 0

while not success:
    try:
        data.download_data()
        success=True
    except Exception as e:
        print(e)
        time.sleep(20)
        print('retrying in 20s')
        tries += 1
        
        if tries >= 200:
            success=True
        continue


# In[5]:


df_incid_fra_clage = data.import_data_tests_sexe()
df_incid_fra = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]


dates_incid = list(dict.fromkeys(list(df_incid_fra['jour'].values))) 


# In[6]:


df_new = data.import_data_new()
df_new_france = df_new.groupby("jour").sum().reset_index()

dates_new = sorted(list(dict.fromkeys(list(df_new_france['jour'].values))))


# In[7]:


df = data.import_data_df()
df = df[df.sexe==0]
dates = sorted(list(dict.fromkeys(list(df['jour'].values))))
df_france = df.groupby("jour").sum().reset_index()


# In[8]:


last_day_plot_dashboard = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=3)).strftime("%Y-%m-%d")
first_day_plot_adm = (datetime.strptime(max(dates), '%Y-%m-%d') - timedelta(days=150)).strftime("%Y-%m-%d")
last_day_plot = (datetime.strptime(max(dates), '%Y-%m-%d') + timedelta(days=1)).strftime("%Y-%m-%d")


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


# In[10]:


df_incid_fra_corrige = df_incid_fra.copy()
df_incid_fra_corrige.loc[df_incid_fra.jour == "2020-11-11", "P"] = 20000
df_incid_fra_corrige.loc[df_incid_fra.jour == "2020-12-25", "P"] = 18000
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-01-01", "P"] = 18000
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-04-05", "P"] = 47000
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-05-01", "P"] = df_incid_fra_corrige.loc[df_incid_fra_corrige.jour == "2021-04-24", "P"].values[0] * 0.7 #9000
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-05-08", "P"] = df_incid_fra_corrige.loc[df_incid_fra_corrige.jour == "2021-05-01", "P"].values[0] * 0.7 #9000*0.9
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-05-13", "P"] = 0.7 * df_incid_fra_corrige[df_incid_fra_corrige.jour == "2021-05-06"]["P"].values[0]
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-05-24", "P"] = 0.7 * df_incid_fra_corrige[df_incid_fra_corrige.jour == "2021-05-17"]["P"].values[0]
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-07-14", "P"] = 1.8 * df_incid_fra_corrige[df_incid_fra_corrige.jour == "2021-07-07"]["P"].values[0]
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-11-01", "P"] = 1.1 * df_incid_fra_corrige[df_incid_fra_corrige.jour == "2021-10-25"]["P"].values[0]
df_incid_fra_corrige.loc[df_incid_fra.jour == "2021-11-11", "P"] = 1.3 * df_incid_fra_corrige[df_incid_fra_corrige.jour == "2021-11-04"]["P"].values[0]


# In[11]:


"""fig = go.Figure()
ira = pd.read_csv("../../../experimentations/data/infections-resp.csv")
ira["day"] = pd.to_datetime(ira.week.astype('str')+"1", format="%Y%W%w")

fig.add_trace(go.Scatter(
    x = df_incid_fra.jour,
    y = df_incid_fra.P.rolling(window=7).sum()/df_incid_fra["pop"]*100000,
    name = "Incidence Covid",
    line_width=3,
    opacity=1,
    showlegend=True
))

fig.add_trace(go.Scatter(
    x = ira.day,
    y = ira.inc100*1.8,
    name = "Incidence IRA * 1,8",
    line_width=3,
    opacity=1,
    showlegend=True
))


fig.update_layout(
    bargap=0,
    margin=dict(
            l=50,
            r=0,
            b=0,
            t=70,
            pad=10
        ),
    legend_orientation="h",
    barmode='group',
    title={
                'text': "Infections respiratoires aiguës",
                'y':0.99,
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
                    y=0.99,
                    xref='paper',
                    yref='paper',
                    font=dict(size=14),
                    text="",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    showarrow=False
                ),
                dict(
                    x=0.5,
                    y=1.08,
                    xref='paper',
                    yref='paper',
                    font=dict(size=14),
                    text="Données : réseau Sentinelles - @GuillaumeRozier",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    showarrow=False
                ),
                ]
                 )


fig['layout']['annotations'] += (
     dict(
        x=0.5,
        y=-0.1,
        font=dict(size=10),
        xref='paper',
        yref='paper',
        text="",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
        showarrow=False
                ),)

fig.show()"""


# In[12]:


suffixe=""
for (date_deb, date_fin) in [("2020-09-18", last_day_plot_dashboard), (dates[-100], last_day_plot)]:
    range_x, name_fig, range_y = [date_deb, date_fin], "cas_journ"+suffixe, [0, df_incid_fra["P"].max()*0.9]
    
    title = "<b>Cas positifs</b> au Covid19"

    #fig = go.Figure()
    for i in ("", "log"):
        if i=="log":
            title += " [log.]"
            range_y=[3, math.log(df_incid_fra["P"].rolling(window=7).mean().values[-100:].max())/2]

        fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])

        df_incid_france_cas_rolling = df_incid_fra["P"].rolling(window=7, center=True).mean()#df_incid_france["P"].rolling(window=7, center=True).mean()
        df_incid_france_cas_rolling_corrige = df_incid_fra_corrige["P"].rolling(window=7, center=True).mean()#df_incid_france["P"].rolling(window=7, center=True).mean()
        df_incid_france_tests_rolling = df_incid_fra["T"].rolling(window=7, center=True).mean()
        
        fig.add_trace(go.Scatter(
            x = df_incid_fra["jour"],
            y = df_incid_france_cas_rolling_corrige,
            name = "Cas positifs (correction jours fériés)",
            marker_color='red', #'rgb(8, 115, 191)'
            line_width=2,
            opacity=1,
            line=dict(dash="dot"),
            showlegend=True
        ), secondary_y=True)
        
        fig.add_trace(go.Scatter(
            x = df_incid_fra["jour"],
            y = df_incid_france_cas_rolling,
            name = "Cas positifs (moyenne 7 j.)",
            marker_color='rgb(8, 115, 191)',
            line_width=4,
            opacity=0.8,
            fill='tozeroy',
            fillcolor="rgba(8, 115, 191, 0.3)",
            showlegend=True
        ), secondary_y=True)
        
        fig.add_trace(go.Bar(
            x = df_incid_fra["jour"],
            y = df_incid_fra["P"],
            name = "",
            #opacity=0.5,
            #mode="markers",
            marker_color='rgba(8, 115, 191, 0.05)',
            #line_width=4,
            showlegend=False
        ), secondary_y=True)
        
        fig.add_trace(go.Scatter(
            x = [df_incid_fra["jour"].values[-4]],
            y = [df_incid_france_cas_rolling_corrige.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgba(255, 255, 255, 0.6)',
            marker_size=12,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x = [df_incid_fra["jour"].values[-4]],
            y = [df_incid_france_cas_rolling_corrige.values[-4]],
            name = "",
            mode="markers",
            marker_color='red',
            marker_size=8,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_shape(type="line",
        x0="2019-12-15", y0=5000, x1="2021-12-15", y1=5000,
        line=dict(color="green",width=2, dash="dot"), xref='x1', yref='y2'
        )

        fig.add_trace(go.Scatter(
            x = [dates_incid[-4]],
            y = [df_incid_france_cas_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgba(255, 255, 255, 0.6)',
            marker_size=12,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x = [dates_incid[-4]],
            y = [df_incid_france_cas_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgb(8, 115, 191)',
            marker_size=8,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        ###
        if i=="log":
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=True)
            #fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=False)
        else:
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13, color="rgba(8, 115, 191, 1)"), secondary_y=True,)
            #fig.update_yaxes(zerolinecolor='blue', tickfont=dict(size=13, color="Grey"), secondary_y=False)

        fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=16), range=range_x)

        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(
            bargap=0,
            margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=70,
                    pad=10
                ),
            legend_orientation="h",
            barmode='group',
            title={
                        'text': title,
                        'y':0.99,
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
                            y=0.99,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),
                        dict(
                            x=0.5,
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Par date de prélèvement sur le patient - @GuillaumeRozier - covidtracker.fr",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                         )

        croissance = round(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100, 1)
        croissance_corrige = round(((df_incid_france_cas_rolling_corrige.values[-4]-df_incid_france_cas_rolling_corrige.values[-4-7]) / df_incid_france_cas_rolling_corrige.values[-4-7])*100, 1)
        if croissance >= 0:
            croissance="+"+str(abs(croissance))
            
        if croissance_corrige >= 0:
            croissance_corrige="+"+str(abs(croissance_corrige))
            
        croissance = str(croissance).replace(".", ",")
        croissance_corrige = str(croissance_corrige).replace(".", ",")
        
        croissance_tests = round(((df_incid_france_tests_rolling.values[-4]-df_incid_france_tests_rolling.values[-4-7]) / df_incid_france_tests_rolling.values[-4-7])*100, 1)
        if croissance_tests >= 0:
            croissance_tests="+"+str(abs(croissance_tests))
            
        croissance_tests = str(croissance_tests).replace(".", ",")  
        
        if i=="log":
            y=math.log(df_incid_france_cas_rolling.values[-4])
        else:
            y=df_incid_france_cas_rolling.values[-4]
        ax=-60
        ax2=-100
        if(suffixe=="_recent"):
            ax=-100
            ax2=0
        fig['layout']['annotations'] += (
            dict(
                x = dates_incid[-4], y = y, # annotation point
                xref='x1', 
                yref='y2',
                text=" <b>{} {}".format('%s' % nbWithSpaces(df_incid_france_cas_rolling.values[-4]), "cas quotidiens<br></b>en moyenne<br>prélevés du {} au {}.<br> {} % en 7 jours<br>".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'), croissance, nbWithSpaces(df_incid_france_cas_rolling_corrige.values[-4]), croissance_corrige)),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="rgb(8, 115, 191)",
                    size=12
                    ),
                bgcolor="rgba(255, 255, 255, 0.6)",
                opacity=1,
                ax=ax,
                ay=-50,
                arrowcolor="rgb(8, 115, 191)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
              dict(
                x = dates_incid[-1], y = 5000, # annotation point
                xref='x1', 
                yref='y2',
                text="Objectif",
                xshift=0,
                yshift=0,
                xanchor="left",
                yanchor="top",
                align='center',
                font=dict(
                    color="green",
                    size=10
                    ),
                opacity=1,
                ax=0,
                ay=0,
                showarrow=False
            ),
             dict(
                x=0.5,
                y=-0.1,
                font=dict(size=10),
                xref='paper',
                yref='paper',
                text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                showarrow=False
                        ))

        fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

        plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
        print("> " + name_fig)
        if show_charts:
            fig.show()
        suffixe="_recent"


# In[13]:


suffixe=""
for (date_deb, date_fin) in [("2020-09-18", last_day_plot_dashboard), (dates[-100], last_day_plot)]:
    range_x, name_fig, range_y = [date_deb, date_fin], "tests_journ"+suffixe, [0, df_incid_fra["T"].max()*1]
    
    title = "<b>Tests</b> de Covid19"

    #fig = go.Figure()
    for i in ("", "log"):
        if i=="log":
            title += " [log.]"
            range_y=[3, math.log(df_incid_fra["T"].rolling(window=7).mean().values[-100:].max())/2]

        fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])

        #df_incid_france_cas_rolling = df_incid_fra[""].rolling(window=7, center=True).mean()#df_incid_france["P"].rolling(window=7, center=True).mean()
        #df_incid_france_cas_rolling_corrige = df_incid_fra_corrige["P"].rolling(window=7, center=True).mean()#df_incid_france["P"].rolling(window=7, center=True).mean()
        df_incid_france_tests_rolling = df_incid_fra["T"].rolling(window=7, center=True).mean()
    
        
        fig.add_trace(go.Scatter(
            x = df_incid_fra["jour"],
            y = df_incid_france_tests_rolling,
            name = "Tests (moyenne 7 j.)",
            marker_color='rgba(60, 60, 60, 1)',
            line_width=4,
            opacity=0.8,
            fill='tozeroy',
            fillcolor="rgba(0, 0, 0, 0.3)",
            showlegend=True
        ), secondary_y=True)
        
        fig.add_trace(go.Bar(
            x = df_incid_fra["jour"],
            y = df_incid_fra["T"],
            name = "",
            #opacity=0.5,
            #mode="markers",
            marker_color='rgba(0, 0, 0, 0.05)',
            #line_width=4,
            showlegend=False
        ), secondary_y=True)
        
        fig.add_trace(go.Scatter(
            x = [df_incid_fra["jour"].values[-4]],
            y = [df_incid_france_tests_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgba(255, 255, 255, 0.6)',
            marker_size=12,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x = [dates_incid[-4]],
            y = [df_incid_france_tests_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgba(255, 255, 255, 0.6)',
            marker_size=12,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x = [dates_incid[-4]],
            y = [df_incid_france_tests_rolling.values[-4]],
            name = "",
            mode="markers",
            marker_color='rgb(60, 60, 60)',
            marker_size=8,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        ###
        if i=="log":
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=True)
            #fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=False)
        else:
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13, color="rgba(8, 115, 191, 1)"), secondary_y=True,)
            #fig.update_yaxes(zerolinecolor='blue', tickfont=dict(size=13, color="Grey"), secondary_y=False)

        fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=16), range=range_x)

        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(
            bargap=0,
            margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=70,
                    pad=10
                ),
            legend_orientation="h",
            barmode='group',
            title={
                        'text': title,
                        'y':0.99,
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
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Par date de prélèvement sur le patient - @GuillaumeRozier - covidtracker.fr",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                         )

        croissance = round(((df_incid_france_tests_rolling.values[-4]-df_incid_france_tests_rolling.values[-4-7]) / df_incid_france_tests_rolling.values[-4-7])*100, 1)

        if croissance >= 0:
            croissance="+"+str(abs(croissance))
            
        croissance = str(croissance).replace(".", ",")
        
        if i=="log":
            y=math.log(df_incid_france_tests_rolling.values[-4])
        else:
            y=df_incid_france_tests_rolling.values[-4]
            
        ax=-60
        ax2=-100
        if(suffixe=="_recent"):
            ax=-100
            ax2=0
            
        fig['layout']['annotations'] += (
            dict(
                x = dates_incid[-4], y = y, # annotation point
                xref='x1', 
                yref='y2',
                text=" <b>{} {}".format('%s' % nbWithSpaces(df_incid_france_tests_rolling.values[-4]), "tests quotidiens<br></b>en moyenne<br>prélevés du {} au {}.<br> {} % en 7 jours<br>".format(datetime.strptime(dates_incid[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_incid[-1], '%Y-%m-%d').strftime('%d %b'), croissance, nbWithSpaces(df_incid_france_cas_rolling_corrige.values[-4]), croissance_corrige)),
                #<br><span style='color:red;'>Avec correction :<br> {} cas en moyenne<br>{} % en 7 jours</span>
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="rgb(60, 60, 60)",
                    size=12
                    ),
                bgcolor="rgba(255, 255, 255, 0.6)",
                opacity=1,
                ax=ax,
                ay=-50,
                arrowcolor="rgb(60, 60, 60)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
             dict(
                x=0.5,
                y=-0.1,
                font=dict(size=10),
                xref='paper',
                yref='paper',
                text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                showarrow=False
                        ))

        fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

        plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
        print("> " + name_fig)
        if show_charts:
            fig.show()
        suffixe="_recent"


# In[14]:



    

range_x, name_fig, range_y = ["2020-05-10", last_day_plot], "cas_journ_croissance", [-50, 150]
title = "<b>Croissance des cas positifs</b> au Covid19"

fig = go.Figure()

df_incid_france_cas_rolling = df_incid_fra["P"].rolling(window=7, center=True).mean()
df_incid_france_cas_rolling = (df_incid_france_cas_rolling-df_incid_france_cas_rolling.shift(7))/df_incid_france_cas_rolling.shift(7)*100

fig.add_trace(go.Bar(
    x = df_incid_fra["jour"],
    y = df_incid_france_cas_rolling,
    name = "",
    marker_color='rgb(8, 115, 191)',
    #line_width=8,
    opacity=0.8,
    #fill='tozeroy',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    showlegend=False
))

###

fig.update_yaxes(zerolinecolor='Grey', range=[-50, 70], tickfont=dict(size=18))
fig.update_xaxes(nticks=10, ticks='inside', range=range_x, tickangle=0, tickfont=dict(size=18))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    bargap=0,
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
                    x=0,
                    y=1,
                    xref='paper',
                    yref='paper',
                    text='Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),
                ]
                 )

croissance = math.trunc(((df_incid_france_cas_rolling.values[-4]-df_incid_france_cas_rolling.values[-4-7]) / df_incid_france_cas_rolling.values[-4-7])*100)

fig['layout']['annotations'] += (dict(
        x = dates_incid[-4], y = df_incid_france_cas_rolling.values[-4], # annotation point
        xref='x1', 
        yref='y1',
        text=" <b>{}% {}".format('%d' % df_incid_france_cas_rolling.values[-4], "de croissance<br>hebdomadaire"),
        xshift=-2,
        yshift=10,
        xanchor="center",
        align='center',
        font=dict(
            color="rgb(8, 115, 191)",
            size=20
            ),
        opacity=1,
        ax=-130,
        ay=-10,
        arrowcolor="rgb(8, 115, 191)",
        arrowsize=1.5,
        arrowwidth=1,
        arrowhead=0,
        showarrow=True
    ),)

fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[15]:


#Comparaison J-7
name_fig = "cas_comp_j7"
fig = go.Figure()
df_temp = df_incid_fra #[df_incid_fra.jour > dates[-400]]
df_incid_france_cas_rolling = df_temp["P"] #.rolling(window=7, center=True).mean()
croissance = ((df_incid_france_cas_rolling-df_incid_france_cas_rolling.shift(7))/df_incid_france_cas_rolling.shift(7)*100)
croissance[croissance>200]=50

fig.add_trace(go.Bar(
    x=df_temp["jour"],
    y=croissance,
    name = "% d'évolution J-7/J-0",
    marker_color='rgb(8, 115, 191)',
#line_width=4,
))

fig.add_trace(go.Scatter(
    x=df_temp["jour"],
    y=croissance.rolling(window=7, center=True).mean(),
    name = "Moyenne mobile du % d'évolution",
    marker_color='black',
#line_width=4,
))

fig.update_yaxes(ticksuffix="%")
fig.update_layout(
    legend_orientation="h",
    annotations=[dict(
                            x=0.5,
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Par date de prélèvement sur le patient - @GuillaumeRozier - covidtracker.fr",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),],
    title={
                        'text': "Évolution en % du nombre de cas entre J-0 et J-7",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        titlefont = dict(
                        size=30),)
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[16]:


df_table_indicateurs = data.download_and_import_table_indicateurs()
df_table_indicateurs_recent = df_table_indicateurs[df_table_indicateurs["date"]>="2022-01-01"]
cas_cum = df_table_indicateurs_recent["conf_j1"].cumsum()/67800000*100
dates_cas_cum = pd.to_datetime(df_table_indicateurs_recent["date"])


# In[17]:


df_new_france_recent = df_new_france[df_new_france["jour"]>="2020-01-01"]
adm_hosp_recent = df_new_france_recent["incid_hosp"].cumsum()
dates_adm_hosp_recent = pd.to_datetime(df_new_france_recent["jour"])


# In[18]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
    x=dates_cas_cum,
    y=cas_cum,
    line=dict(width=6, color=COLOR_PAPER),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    fillcolor="rgba(0,0,0,0.2)",
    fill="tozeroy",
    textposition="middle right",
    showlegend=False,
    mode="lines+text",
    name="Décès hôpital")
)

fig.add_trace(
    go.Scatter(
    x=dates_cas_cum,
    y=cas_cum,
    line=dict(width=3, color="black"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    mode="lines+text",
    showlegend=False,
    name="Décès hospitalier")
)



fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.2,
    text="<b>Cas positifs cumulés</b> depuis le 1er janvier 2022",
    font=dict(size=24),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.1,
    text="En % de la population française.<br>@GuillaumeRozier • Données : Santé publique France",
    font=dict(size=14),
    showarrow=False
)

fig.add_annotation(
    x=dates_cas_cum.max(),
    y=cas_cum.max(),
    text=f"{round(cas_cum.max(), 1)}% des Français<br>positifs depuis le 1er janvier",
    ay=-50,
    ax=-25,
    font=dict(size=14),
)

fig.update_layout(
    showlegend=True,
    legend_orientation="h",
    xaxis=dict(showgrid=False, zeroline=True, showline=True, range=[dates_cas_cum.min(), dates_cas_cum.max()+timedelta(days=2)]),
    yaxis=dict(ticksuffix=" %", zeroline=True, range=[0, 105]),
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(r=50)
)
fig.add_hline(y=100, line=dict(color="black", dash="dot"),)

fig.write_image(PATH + f"images/charts/france/cas_cum.jpeg", scale=2, width=900, height=600)


# In[19]:


fig = go.Figure()

fig.add_trace(
    go.Scatter(
    x=dates_adm_hosp_recent,
    y=adm_hosp_recent,
    line=dict(width=6, color=COLOR_PAPER),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    fillcolor="rgba(0,0,0,0.2)",
    fill="tozeroy",
    textposition="middle right",
    showlegend=False,
    mode="lines+text",
    name="Décès hôpital")
)

fig.add_trace(
    go.Scatter(
    x=dates_adm_hosp_recent,
    y=adm_hosp_recent,
    line=dict(width=3, color="black"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    mode="lines+text",
    showlegend=False,
    name="Décès hospitalier")
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.2,
    text="<b>Admissions à l'hôpital cumulées</b> depuis le 1er janvier 2022",
    font=dict(size=24),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.1,
    text="<br>@GuillaumeRozier • Données : Santé publique France",
    font=dict(size=14),
    showarrow=False
)

fig.add_annotation(
    x=dates_adm_hosp_recent.max(),
    y=adm_hosp_recent.max(),
    text=f"{round(adm_hosp_recent.max(), 1)} admissions à<br>l'hôpital depuis le<br>1er janvier",
    ay=-50,
    ax=0,
    font=dict(size=14),
)

fig.update_layout(
    showlegend=True,
    legend_orientation="h",
    xaxis=dict(showgrid=False, zeroline=True, showline=True, range=[dates_adm_hosp_recent.min(), dates_adm_hosp_recent.max()+timedelta(days=5)]),
    yaxis=dict(ticksuffix="", zeroline=True),
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(r=50)
)

fig.write_image(PATH + f"images/charts/france/adm_hosp_cum.jpeg", scale=2, width=900, height=600)


# In[20]:


#Comparaison J-7
name_fig = "tests_comp_j7"
fig = go.Figure()
df_temp = df_incid_fra[df_incid_fra.jour > dates[-400]]
df_incid_france_cas_rolling = df_temp["T"] #.rolling(window=7, center=True).mean()
croissance = ((df_incid_france_cas_rolling-df_incid_france_cas_rolling.shift(7))/df_incid_france_cas_rolling.shift(7)*100)
croissance[croissance>200]=50

fig.add_trace(go.Bar(
    x=df_temp["jour"],
    y=croissance,
    name = "% d'évolution J-7/J-0",
    marker_color='rgb(8, 115, 191)',
#line_width=4,
))

fig.add_trace(go.Scatter(
    x=df_temp["jour"],
    y=croissance.rolling(window=7, center=True).mean(),
    name = "Moyenne mobile du % d'évolution",
    marker_color='black',
#line_width=4,
))

fig.update_yaxes(ticksuffix="%")
fig.update_layout(
    legend_orientation="h",
    annotations=[dict(
                            x=0.5,
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Par date de prélèvement sur le patient - @GuillaumeRozier - covidtracker.fr",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),],
    title={
                        'text': "Évolution en % du nombre de tests entre J-0 et J-7",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        titlefont = dict(
                        size=30),)
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[21]:




title = "<b>Admissions à l'hôpital</b> avec Covid19"
incid_hosp_rolling = df_new_france["incid_hosp"].rolling(window=7, center=True).mean()

range_x, name_fig, range_y = ["2020-12-29", last_day_plot], "hosp_journ_adm", [0, incid_hosp_rolling[-150:].max()*1.2]

for i in ("", "log"):
    if i=="log":
        title += " [log.]"
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])
    
    fig.add_trace(go.Bar(
        x = df_new_france["jour"],
        y = df_new_france["incid_hosp"],
        name = "Admissions soins critiques",
        marker_color='rgba(209, 102, 21, 0.5)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = incid_hosp_rolling,
        name = "Admissions à l'hôpital",
        marker_color='rgb(209, 102, 21)',
        marker_size=5,
        line_width=6,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_shape(type="line",
    x0="2020-03-17", y0=0, x1="2020-03-17", y1=15000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-05-11", y0=0, x1="2020-05-11", y1=15000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-10-30", y0=0, x1="2020-10-30", y1=15000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-11-28", y0=0, x1="2020-11-28", y1=15000,
    line=dict(color="Orange",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-12-15", y0=0, x1="2020-12-15", y1=15000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_trace(go.Scatter(
        x = [dates[-4]],
        y = [incid_hosp_rolling.values[-4]],
        name = "",
        mode="markers",
        marker_color='rgba(255, 255,255, 0.6)',
        marker_size=18,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = [dates[-4]],
        y = [incid_hosp_rolling.values[-4]],
        name = "",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=13,
        opacity=1,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), type="log", range=[0, 4])
    else:
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y)
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=[first_day_plot_adm, last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
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
                        y=0.95,
                        font=dict(size=14),
                        xref='paper',
                        yref='paper',
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    
                    ]
                     )

    croissance = round((incid_hosp_rolling.values[-4] - incid_hosp_rolling.values[-11]) * 100 / incid_hosp_rolling.values[-11], 1)
    if croissance > 0:
        croissance="+"+str(abs(croissance))
    croissance = str(croissance).replace(".", ",")
    
    date_deb, date_fin = datetime.strptime(dates_new[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_new[-1], '%Y-%m-%d').strftime('%d %b.')
 
    fig['layout']['annotations'] += (dict(
            x = dates[-4], y = incid_hosp_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%s' % nbWithSpaces(incid_hosp_rolling.values[-4]), "admissions quotidiennes<br>à l'hôpital</b><br>en moyenne du {} au {},<br>{} % en 7 jours".format(date_deb, date_fin, croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=14
                ),
            opacity=0.8,
            ax=-70,
            ay=-50,
            arrowcolor="rgb(209, 102, 21)",
            bgcolor="rgba(255, 255, 255, 0.6)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = "2020-03-17", y = 8100, # annotation point
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="red",
                size=8
                )
        ),
            dict(
            x = "2020-10-30", y = 8100, # annotation point
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="red",
                size=8
                )
        ),
            dict(
            x = "2020-05-11", y = 8100, # annotation point
            text="Déconfinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="green",
                size=8
                )
        ),
        dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[22]:


df_txad = data.download_and_import_hosp_txad_fra()
df_pour = df_txad[df_txad["PourAvec"]==1]
df_avec = df_txad[df_txad["PourAvec"]==2]


# In[23]:




title = "<b>Admissions à l'hôpital</b> avec vs. pour Covid19"

range_x, name_fig, range_y = ["2020-12-29", df_pour["jour"].max()], "hosp_journ_adm", [0, df_pour["tx_indic_7J_hosp"][-150:].max()*1.2]


fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])


fig.add_trace(go.Scatter(
    x = df_pour["jour"],
    y = df_pour["tx_indic_7J_hosp"]*670/7,
    marker_color='rgb(209, 102, 21)',
    fillcolor='rgba(209, 102, 21, 0.5)',
    marker_size=5,
    line_width=2,
    opacity=1,
    showlegend=True,
    stackgroup="one",
    name="dont soignés pour Covid19",
    fill="tonexty"
))

fig.add_trace(go.Scatter(
    x = df_avec["jour"],
    y = df_avec["tx_indic_7J_hosp"]*670/7,
    marker_color='rgba(237, 137, 62, 1)',
    fillcolor='rgba(209, 102, 21, 0.2)',
    marker_size=5,
    line_width=2,
    opacity=1,
    showlegend=True,
    stackgroup="one",
    name="soignés pour autre pathologie, mais avec Covid19",
    fill="tonexty"
))

fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=[range_x[0], range_x[1]])

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    margin=dict(
            l=50,
            r=50,
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
                    y=0.95,
                    font=dict(size=14),
                    xref='paper',
                    yref='paper',
                    text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),

                ]
                 )


fig['layout']['annotations'] += (
    dict(
        x=df_pour["jour"].max(),
        y=df_pour["tx_indic_7J_hosp"].values[-1]*670/7,
        font=dict(size=10, color="rgb(209, 102, 21)"),
        text=f"{round(df_pour['tx_indic_7J_hosp'].values[-1]*670/7)}<br>",
        showarrow=False,
        xshift=10,
        xanchor="left"
                ),
     dict(
        x=df_avec["jour"].max(),
        y=df_avec["tx_indic_7J_hosp"].values[-1]*670/7+df_pour["tx_indic_7J_hosp"].values[-1]*670/7,
        font=dict(size=10, color="rgba(237, 137, 62, 1)"),
        text=f"{round(df_avec['tx_indic_7J_hosp'].values[-1]*670/7)}<br>",
        showarrow=False,
        xshift=10,
        xanchor="left"
                ),
    dict(
        x=0.5,
        y=-0.1,
        font=dict(size=10),
        xref='paper',
        yref='paper',
        text="Données Santé publique France • {}".format(datetime.strptime(df_avec["jour"].max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
        showarrow=False
                ),)

fig.write_image(PATH + "images/charts/france/{}_pouravec.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}_pouravec.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[24]:


title = "<b>Décès à l'hôpital</b> avec vs. pour Covid19"

range_x, name_fig, range_y = ["2020-12-29", df_pour["jour"].max()], "dc_journ_adm", [0, df_pour["tx_indic_7J_DC"][-150:].max()*1.2]


fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])


fig.add_trace(go.Scatter(
    x = df_pour["jour"],
    y = df_pour["tx_indic_7J_DC"]*670/7,
    marker_color='rgb(209, 102, 21)',
    fillcolor='rgba(209, 102, 21, 0.5)',
    marker_size=5,
    line_width=2,
    opacity=1,
    showlegend=True,
    stackgroup="one",
    name="dont soignés pour Covid19",
    fill="tonexty"
))

fig.add_trace(go.Scatter(
    x = df_avec["jour"],
    y = df_avec["tx_indic_7J_DC"]*670/7,
    marker_color='rgba(237, 137, 62, 1)',
    fillcolor='rgba(209, 102, 21, 0.2)',
    marker_size=5,
    line_width=2,
    opacity=1,
    showlegend=True,
    stackgroup="one",
    name="soignés pour autre pathologie, mais avec Covid19",
    fill="tonexty"
))

fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=[range_x[0], range_x[1]])

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    margin=dict(
            l=50,
            r=50,
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
                    y=0.95,
                    font=dict(size=14),
                    xref='paper',
                    yref='paper',
                    text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),

                ]
                 )


fig['layout']['annotations'] += (
    dict(
        x=df_pour["jour"].max(),
        y=df_pour["tx_indic_7J_DC"].values[-1]*670/7,
        font=dict(size=10, color="rgb(209, 102, 21)"),
        text=f"{round(df_pour['tx_indic_7J_hosp'].values[-1]*670/7)}<br>",
        showarrow=False,
        xshift=10,
        xanchor="left"
                ),
     dict(
        x=df_avec["jour"].max(),
        y=df_avec["tx_indic_7J_DC"].values[-1]*670/7+df_pour["tx_indic_7J_hosp"].values[-1]*670/7,
        font=dict(size=10, color="rgba(237, 137, 62, 1)"),
        text=f"{round(df_avec['tx_indic_7J_hosp'].values[-1]*670/7)}<br>",
        showarrow=False,
        xshift=10,
        xanchor="left"
                ),
    dict(
        x=0.5,
        y=-0.1,
        font=dict(size=10),
        xref='paper',
        yref='paper',
        text="Données Santé publique France • {}".format(datetime.strptime(df_avec["jour"].max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
        showarrow=False
                ),)

fig.write_image(PATH + "images/charts/france/{}_pouravec.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}_pouravec.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[25]:



title = "<b>Admissions en soins critiques</b> avec vs. pour Covid19"

range_x, name_fig, range_y = ["2020-12-29", df_pour["jour"].max()], "rea_journ_adm", [0, df_pour["tx_indic_7J_hosp"][-150:].max()*1.2]


fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])


fig.add_trace(go.Scatter(
    x = df_pour["jour"],
    y = df_pour["tx_indic_7J_SC"]*670/7,
    marker_color='rgb(201, 4, 4)',
    fillcolor='rgba(201, 4, 4, 0.5)',
    marker_size=5,
    line_width=2,
    opacity=1,
    showlegend=True,
    stackgroup="one",
    name="dont soignés pour Covid19",
    fill="tonexty"
))

fig.add_trace(go.Scatter(
    x = df_avec["jour"],
    y = df_avec["tx_indic_7J_SC"]*670/7,
    marker_color='rgb(227, 61, 61)',
    fillcolor='rgba(227, 61, 61, 0.4)',
    marker_size=5,
    line_width=2,
    opacity=1,
    showlegend=True,
    stackgroup="one",
    name="soignés pour autre pathologie, mais avec Covid19",
    fill="tonexty"
))

fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=[range_x[0], range_x[1]])

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
    margin=dict(
            l=50,
            r=50,
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
                    y=0.95,
                    font=dict(size=14),
                    xref='paper',
                    yref='paper',
                    text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                ),

                ]
                 )


fig['layout']['annotations'] += (
    dict(
        x=df_pour["jour"].max(),
        y=df_pour["tx_indic_7J_SC"].values[-1]*670/7,
        font=dict(size=10, color="rgb(201, 4, 4)"),
        text=f"{round(df_pour['tx_indic_7J_SC'].values[-1]*670/7)}<br>",
        showarrow=False,
        xshift=10,
        xanchor="left"
                ),
     dict(
        x=df_avec["jour"].max(),
        y=df_avec["tx_indic_7J_SC"].values[-1]*670/7+df_pour["tx_indic_7J_SC"].values[-1]*670/7,
        font=dict(size=10, color="rgba(227, 61, 61, 1)"),
        text=f"{round(df_avec['tx_indic_7J_SC'].values[-1]*670/7)}<br>",
        showarrow=False,
        xshift=10,
        xanchor="left"
                ),
    dict(
        x=0.5,
        y=-0.1,
        font=dict(size=10),
        xref='paper',
        yref='paper',
        text="Données Santé publique France • {}".format(datetime.strptime(df_avec["jour"].max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
        showarrow=False
                ),)

fig.write_image(PATH + "images/charts/france/{}_pouravec.jpeg".format(name_fig), scale=2, width=900, height=600)

plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}_pouravec.html'.format(name_fig), auto_open=False)
print("> " + name_fig)
if show_charts:
    fig.show()


# In[26]:


range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "hosp_journ", [0, df_france["hosp"].max()*1.1]
title = "<b>Personnes hospitalisées</b> pour Covid19"

for i in ("", "log"):
    if i=="log":
        title+= " [log.]"
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_france["hosp"],
        name = "",
        marker_color='rgb(209, 102, 21)',
        line_width=4,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    
    
    """fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-05-11", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.05,
                    layer="below"
        )
    """
    """fig.add_shape(type="rect",
                    x0="2020-03-17", x1="2020-03-17", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=0.5,
                    ),
                    layer="below"
        )
    """
    """fig.add_shape(type="rect",
                    x0="2020-10-30", x1=last_day_plot_dashboard, 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=2,
                    ),
                    fillcolor="red",
                    opacity=0.05,
                      layer="below"

        )"""
    
    """fig.add_shape(type="rect",
                    x0="2020-10-30", x1="2020-10-30", 
                    y0=0, 
                    y1=100000,
                    line=dict(
                        color="red",
                        width=0.5,
                    ),
                    layer="below"
        )"""
    
    fig.add_trace(go.Bar(
        x = df_new_france["jour"],
        y = df_new_france["incid_hosp"],
        name = "",
        marker_color='rgb(209, 102, 21)',
        #line_width=8,
        opacity=0.8,
        #fill='tozeroy',
        #fillcolor="rgba(209, 102, 21,0.3)",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = df_new_france["incid_hosp"].rolling(window=7).mean(),
        name = "",
        marker_color='rgb(209, 102, 21)',
        marker_size=2,
        opacity=0.8,
        showlegend=False
    ))

    try:
        nope
        model = make_pipeline(PolynomialFeatures(3), Ridge())
        model.fit(df_france["jour"][-20:].index.values.reshape(-1, 1), df_france["hosp"][-20:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max-4, index_max+5)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_france["jour"]), '%Y-%m-%d') - timedelta(days=4))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(209, 102, 21, 0.4)',
            line_width=5,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except Exception as e:
        print(e)
        print("error")
        pass

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["hosp"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=12,
        opacity=1,
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["hosp"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgb(209, 102, 21)',
        marker_size=8,
        opacity=1,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), type="log", range=[0, 5]) #range=[0, max(max(y_plot), df_france["hosp"].max())*1.1]
    else:
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y) #range=[0, max(max(y_plot), df_france["hosp"].max())*1.1] 
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-17", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
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
                        y=0.95,
                        font=dict(size=14),
                        xref='paper',
                        yref='paper',
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>", #'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    
                        showarrow = False
                    ),
 
                    ]
                )

    croissance = round(((df_france["hosp"].values[-1]-df_france["hosp"].values[-1-7]) / df_france["hosp"].values[-1-7]) * 100, 1)
    if croissance > 0:
        croissance="+"+str(abs(croissance))
    croissance = str(croissance).replace(".", ",")
    
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = (df_france["hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%s' % nbWithSpaces(df_france["hosp"].values[-1]), "personnes<br>hospitalisées</b><br>le {}.<br>{} % en 7 jours".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(209, 102, 21)",
                size=15
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-50,
            ay=-100,
            arrowcolor="rgb(209, 102, 21)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ), dict(
            x = df_new_france["jour"].values[-1], y = (df_new_france["incid_hosp"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_france["incid_hosp"].values[-1], "<br>admissions"),
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
        ),
          
           dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[27]:


range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "dc_journ", [0, df_new_france["incid_dc"].max()]
title = "<b>Décès hospitaliers quotidiens</b> du Covid19"

for i in ("", "log"):
    dc_new_rolling = df_new_france["incid_dc"].rolling(window=7).mean()
    
    if i=="log":
        title += " [log.]"
        range_y=[0, math.log(df_new_france["incid_dc"].max())/2]
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = dc_new_rolling,
        name = "Nouveaux décès hosp.",
        marker_color='black',
        line_width=4,
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
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=14,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [dc_new_rolling.values[-1]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        marker_size=9,
        opacity=1,
        showlegend=False
    ))

    #
    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = df_new_france["incid_dc"],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='black',
        line_width=3,
        opacity=0.2,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18), type="log")
    else:
        fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=18))
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-17", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
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
                        y=0.95,
                        xref='paper',
                        yref='paper',
                        font=dict(size=14),
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>", #'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    
                        showarrow = False
                    ),
                    ]
                   )
    try:
        croissance = round((dc_new_rolling.values[-1]-dc_new_rolling.values[-7-1]) * 100 / dc_new_rolling.values[-1-7], 1)
    except:
        croissance=0
    if croissance > 0:
        croissance="+"+str(abs(croissance))
    croissance = str(croissance).replace(".", ",")
        
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = dc_new_rolling.values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%s' % nbWithSpaces(math.trunc(round(dc_new_rolling.values[-1], 2))), "décès quotidiens</b><br>en moyenne<br>du {} au {}.<br>{} % en 7 jours".format(datetime.strptime(dates[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="black",
                size=15
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-60,
            ay=-250,
            arrowcolor="black",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            
            dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[28]:




title = "<b>Admissions en soins critiques</b> avec Covid19"
incid_rea_rolling = df_new_france["incid_rea"].rolling(window=7, center=True).mean()

range_x, name_fig, range_y = ["2020-09-29", last_day_plot], "rea_journ_adm", [0, incid_rea_rolling[-150:].max()*1.2]

for i in ("", "log"):
    if i=="log":
        title += " [log.]"
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])
    
    fig.add_trace(go.Bar(
        x = df_new_france["jour"],
        y = df_new_france["incid_rea"],
        name = "Admissions soins critiques",
        marker_color='rgba(201, 4, 4, 0.5)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = incid_rea_rolling,
        name = "Admissions soins critiques",
        marker_color='rgb(201, 4, 4)',
        marker_size=5,
        line_width=6,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_shape(type="line",
    x0="2020-03-17", y0=0, x1="2020-03-17", y1=15000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-05-11", y0=0, x1="2020-05-11", y1=15000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-10-30", y0=0, x1="2020-10-30", y1=15000,
    line=dict(color="Red",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-11-28", y0=0, x1="2020-11-28", y1=15000,
    line=dict(color="Orange",width=0.5, dash="dot")
    )
    
    fig.add_shape(type="line",
    x0="2020-12-15", y0=0, x1="2020-12-15", y1=15000,
    line=dict(color="Green",width=0.5, dash="dot")
    )
    
    fig.add_trace(go.Scatter(
        x = [dates[-4]],
        y = [incid_rea_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=18,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = [dates[-4]],
        y = [incid_rea_rolling.values[-4]],
        name = "Nouveaux décès hosp.",
        mode="markers",
        marker_color='rgba(201, 4, 4, 1)',
        marker_size=13,
        opacity=1,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), type="log", range=[0, 4])
    else:
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y)
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=[first_day_plot_adm, last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
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
                        y=0.95,
                        font=dict(size=14),
                        xref='paper',
                        yref='paper',
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    
                    ]
                     )

    croissance = round((incid_rea_rolling.values[-4] - incid_rea_rolling.values[-11]) * 100 / incid_rea_rolling.values[-11], 1)
    if croissance > 0:
        croissance="+"+str(abs(croissance))
    croissance = str(croissance).replace(".", ",")
    
    date_deb, date_fin = datetime.strptime(dates_new[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(dates_new[-1], '%Y-%m-%d').strftime('%d %b.')
    
    fig['layout']['annotations'] += (dict(
            x = dates[-4], y = incid_rea_rolling.values[-4], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%d' % incid_rea_rolling.values[-4], "admissions quotidiennes<br>en soins critiques</b><br>en moyenne du {} au {},<br>{} % en 7 jours".format(date_deb, date_fin, croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=14
                ),
            opacity=0.8,
            ax=-70,
            ay=-50,
            arrowcolor="rgb(201, 4, 4)",
            bgcolor="rgba(255, 255, 255, 0.6)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),
            dict(
            x = "2020-03-17", y = 8100, # annotation point
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="red",
                size=8
                )
        ),
            dict(
            x = "2020-10-30", y = 8100, # annotation point
            text="Confinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="red",
                size=8
                )
        ),
            dict(
            x = "2020-05-11", y = 8100, # annotation point
            text="Déconfinement",
            xanchor="left",
            yanchor="top",
            align='center',
            showarrow=False,
            font=dict(
                color="green",
                size=8
                )
        ),
        dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[29]:



range_x, name_fig, range_y = ["2020-03-29", last_day_plot], "rea_journ", [0, df_france["rea"].max()*1.1]
title = "<b>Personnes en soins critiques (dont réa.)</b> avec Covid19"

for i in ("", "log"):
    if i=="log":
        title += " [log.]"
        
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[title], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x = dates,
        y = df_france["rea"],
        name = "Soins critiques (dont réanimations)",
        marker_color='rgb(201, 4, 4)',
        line_width=4,
        opacity=0.8,
        fill='tozeroy',
        fillcolor="rgba(201, 4, 4,0.3)",
        showlegend=False
    ))
    
    fig.add_trace(go.Bar(
        x = df_new_france["jour"],
        y = df_new_france["incid_rea"],
        name = "Admissions soins critiques",
        marker_color='rgb(201, 4, 4)',
        opacity=0.8,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = df_new_france["jour"],
        y = df_new_france["incid_rea"].rolling(window=7).mean(),
        name = "Admissions soins critiques",
        marker_color='rgb(201, 4, 4)',
        marker_size=2,
        opacity=0.8,
        showlegend=False
    ))

    try:
        nope
        model = make_pipeline(PolynomialFeatures(2), Ridge())
        model.fit(df_france["jour"][-10:].index.values.reshape(-1, 1), df_france["rea"][-10:].fillna(method="bfill"))

        index_max = df_france["jour"].index.max()
        x_pred = np.array([x for x in range(index_max-0, index_max+14)]).reshape(-1, 1)

        date_deb = (datetime.strptime(max(df_france["jour"]), '%Y-%m-%d') - timedelta(days=0))
        x_pred_dates = [(date_deb + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(x_pred))]

        y_plot = model.predict(x_pred)

        fig.add_trace(go.Scatter(
            x = x_pred_dates,
            y = y_plot,
            name = "pred",
            marker_color='rgba(201, 4, 4, 0.2)',
            line_width=4,
            opacity=0.8,
            mode="lines",
            #fill='tozeroy',
            #fillcolor="orange",
            showlegend=False
        ))

    except Exception as e:
        print(e)
        print("error")
        pass
    
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["rea"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgba(255, 255, 255, 0.6)',
        marker_size=12,
        opacity=1,
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x = [dates[-1]],
        y = [df_france["rea"].values[-1]],
        name = "",
        mode="markers",
        marker_color='rgb(201, 4, 4)',
        marker_size=8,
        opacity=1,
        showlegend=False
    ))

    ###
    if i=="log":
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), type="log", range=[0, 4])
    else:
        fig.update_yaxes(zerolinecolor='Grey', tickfont=dict(size=18), range=range_y)
        
    fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=18), range=["2020-03-17", last_day_plot_dashboard])

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(
        margin=dict(
                l=50,
                r=10,
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
                        y=0.95,
                        font=dict(size=14),
                        xref='paper',
                        yref='paper',
                        text="<b>@GuillaumeRozier - covidtracker.fr</b>",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                    ),
                    
                    ]
                     )

    croissance = round((df_france["rea"].values[-1] - df_france["rea"].values[-8]) * 100 / df_france["rea"].values[-8], 1)
    if croissance > 0:
        croissance="+"+str(abs(croissance))
    croissance = str(croissance).replace(".", ",")
    
    fig['layout']['annotations'] += (dict(
            x = dates[-1], y = df_france["rea"].values[-1], # annotation point
            xref='x1', 
            yref='y1',
            text=" <b>{} {}".format('%s' % nbWithSpaces(df_france["rea"].values[-1]), "personnes<br>en soins critiques</b><br>le {}.<br>{} % en 7 jours".format(datetime.strptime(dates[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
            xshift=-2,
            yshift=0,
            xanchor="center",
            align='center',
            font=dict(
                color="rgb(201, 4, 4)",
                size=15
                ),
            bgcolor="rgba(255, 255, 255, 0.6)",
            opacity=0.8,
            ax=-50,
            ay=-100,
            arrowcolor="rgb(201, 4, 4)",
            arrowsize=1.5,
            arrowwidth=1,
            arrowhead=0,
            showarrow=True
        ),dict(
            x = df_new_france["jour"].values[-1], y = (df_new_france["incid_rea"].values[-1]), # annotation point
            xref='x1', 
            yref='y1',
            text="<b>{}</b> {}".format('%d' % df_new_france["incid_rea"].values[-1], "<br>admissions"),
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
        ),
         
        dict(
            x=0.5,
            y=-0.1,
            font=dict(size=10),
            xref='paper',
            yref='paper',
            text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
            showarrow=False
                    ))

    fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

    plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
    print("> " + name_fig)
    if show_charts:
        fig.show()


# In[30]:


for croiss in [""]:
    im1 = cv2.imread(PATH + 'images/charts/france/cas_journ{}.jpeg'.format(croiss))
    im2 = cv2.imread(PATH + 'images/charts/france/hosp_journ{}.jpeg'.format(croiss))
    im3 = cv2.imread(PATH + 'images/charts/france/rea_journ{}.jpeg'.format(croiss))
    im4 = cv2.imread(PATH + 'images/charts/france/dc_journ{}.jpeg'.format(croiss))

    im_haut = cv2.hconcat([im1, im2])
    #cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)
    im_bas = cv2.hconcat([im3, im4])

    im_totale = cv2.vconcat([im_haut, im_bas])
    cv2.imwrite(PATH + 'images/charts/france/dashboard_jour{}.jpeg'.format(croiss), im_totale)
    


# In[31]:


data.download_data_vue_ensemble()
df_vue_ensemble = data.import_data_vue_ensemble()
df_vue_ensemble.loc[df_vue_ensemble.date >= "2021-05-21", "total_cas_confirmes"] += 346000
#df_vue_ensemble=df_vue_ensemble.append({"date": "2021-03-30", "total_cas_confirmes": 4554683}, ignore_index=True)


# In[32]:


"""suffixe=""
for (date_deb, date_fin) in [("2020-01-18", datetime.strptime(df_vue_ensemble.date.max(), '%Y-%m-%d') + timedelta(days=4)), ("2020-01-18", datetime.strptime(df_vue_ensemble.date.max(), '%Y-%m-%d') + timedelta(days=4))]:
    range_x, name_fig, range_y = [date_deb, date_fin], "cas_journ_spf"+suffixe, [0, df_vue_ensemble["total_cas_confirmes"].diff().max()*0.7]
    
    title = "<b>Cas positifs</b> au Covid19"

    #fig = go.Figure()
    for i in ("", "log"):
        if i=="log":
            title += " [log.]"
            range_y=[0, math.log(df_vue_ensemble["total_cas_confirmes"].diff().max())/2]

        fig = make_subplots(rows=1, cols=1, shared_yaxes=True, subplot_titles=[""], vertical_spacing = 0.08, horizontal_spacing = 0.1, specs=[[{"secondary_y": True}]])
        df_incid_france_cas_rolling = df_vue_ensemble["total_cas_confirmes"].diff().shift().rolling(window=7, center=False).mean() #df_incid_france["P"].rolling(window=7, center=True).mean()
        df_incid_france_cas_rolling[df_incid_france_cas_rolling<0]=1
        
        fig.add_trace(go.Scatter(
            x = df_vue_ensemble["date"],
            y = df_incid_france_cas_rolling,
            name = "Cas positifs (moyenne 7 j.)",
            marker_color='rgb(8, 115, 191)',
            line_width=8,
            opacity=0.8,
            fill='tozeroy',
            fillcolor="rgba(8, 115, 191, 0.3)",
            showlegend=True
        ), secondary_y=True)
        
        fig.add_trace(go.Bar(
            x = df_vue_ensemble["date"],
            y = df_vue_ensemble["total_cas_confirmes"].diff(),
            name = "Cas positifs (moyenne 7 j.)",
            marker_color='rgb(8, 115, 191)',
            #line_width=8,
            opacity=0.3,
            #fill='tozeroy',
            #fillcolor="rgba(8, 115, 191, 0.3)",
            showlegend=True
        ), secondary_y=True)
        

        fig.add_shape(type="line",
        x0="2019-12-15", y0=5000, x1="2021-12-15", y1=5000,
        line=dict(color="green",width=2, dash="dot"), xref='x1', yref='y2'
        )

        fig.add_trace(go.Scatter(
            x = [df_vue_ensemble["date"].values[-1]],
            y = [df_incid_france_cas_rolling.values[-1]],
            name = "",
            mode="markers",
            marker_color='rgba(255, 255, 255, 0.6)',
            marker_size=16,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x = [df_vue_ensemble["date"].values[-1]],
            y = [df_incid_france_cas_rolling.values[-1]],
            name = "",
            mode="markers",
            marker_color='rgb(8, 115, 191)',
            marker_size=11,
            opacity=1,
            showlegend=False
        ), secondary_y=True)

        ###
        if i=="log":
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=True)
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13), type="log", secondary_y=False)
        else:
            fig.update_yaxes(zerolinecolor='Grey', range=range_y, tickfont=dict(size=13, color="rgba(8, 115, 191, 1)"), secondary_y=True,)
            fig.update_yaxes(zerolinecolor='blue', tickfont=dict(size=13, color="Grey"), secondary_y=False)

        fig.update_xaxes(nticks=10, ticks='inside', tickangle=0, tickfont=dict(size=16), range=range_x)

        # Here we modify the tickangle of the xaxis, resulting in rotated labels.
        fig.update_layout(
            bargap=0,
            margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=70,
                    pad=10
                ),
            legend_orientation="h",
            barmode='group',
            title={
                        'text': title,
                        'y':0.99,
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
                            y=0.99,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),
                        dict(
                            x=0.5,
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Par date de remontée du résultat de test - @GuillaumeRozier - covidtracker.fr",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),
                        ]
                         )

        croissance = math.trunc(round(((df_incid_france_cas_rolling.values[-1]-df_incid_france_cas_rolling.values[-8]) / df_incid_france_cas_rolling.values[-8])*100))
        if croissance >= 0:
            croissance="+"+str(abs(croissance))

        if i=="log":
            y=math.log(df_incid_france_cas_rolling.values[-1])
        else:
            y=df_incid_france_cas_rolling.values[-1]
            
        ax=-100
        ax2=-100
        if(suffixe=="_recent"):
            ax=-100
            ax2=0
            
        fig['layout']['annotations'] += (dict(
                x = df_vue_ensemble["date"].values[-1], y = y, # annotation point
                xref='x1', 
                yref='y2',
                text=" <b>{} {}".format('%s' % nbWithSpaces(df_incid_france_cas_rolling.values[-1]), "cas quotidiens</b><br>en moyenne<br> publiés du {} au {}.<br> {} % en 7 jours".format(datetime.strptime(df_vue_ensemble["date"].values[-7], '%Y-%m-%d').strftime('%d'), datetime.strptime(df_vue_ensemble["date"].values[-1], '%Y-%m-%d').strftime('%d %b'), croissance)),
                xshift=-2,
                yshift=0,
                xanchor="center",
                align='center',
                font=dict(
                    color="rgb(8, 115, 191)",
                    size=20
                    ),
                opacity=1,
                ax=ax,
                ay=-100,
                arrowcolor="rgb(8, 115, 191)",
                arrowsize=1.5,
                arrowwidth=1,
                arrowhead=0,
                showarrow=True
            ),
              dict(
                x = df_vue_ensemble["date"].values[-1], y = 5000, # annotation point
                xref='x1', 
                yref='y2',
                text="Objectif",
                xshift=0,
                yshift=0,
                xanchor="left",
                yanchor="top",
                align='center',
                font=dict(
                    color="green",
                    size=10
                    ),
                opacity=1,
                ax=0,
                ay=0,
                showarrow=False
            ),
                dict(
                x = "2020-10-30", y = 65000, # annotation point
                xref='x1', 
                yref='y2',
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
                x=0.5,
                y=-0.1,
                font=dict(size=10),
                xref='paper',
                yref='paper',
                text="Données Santé publique France",#'Date : {}. Source : Santé publique France. Auteur : guillaumerozier.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                showarrow=False
                        ))

        fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig+i), scale=2, width=900, height=600)

        plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig+i), auto_open=False)
        print("> " + name_fig)
        if show_charts:
            fig.show()
        suffixe="_recent"
    """


# In[33]:


#Comparaison J-7
name_fig = "tests_comp_j7"
fig = go.Figure()
df_temp = df_incid_fra[df_incid_fra.jour > dates[-400]]
df_incid_france_cas_rolling = df_temp["T"] #.rolling(window=7, center=True).mean()
croissance = ((df_incid_france_cas_rolling-df_incid_france_cas_rolling.shift(7))/df_incid_france_cas_rolling.shift(7)*100)
croissance[croissance>200]=50

fig.add_trace(go.Bar(
    x=df_temp["jour"],
    y=croissance,
    name = "% d'évolution J-7/J-0",
    marker_color='rgba(0, 0, 0, 0.4)',
#line_width=4,
))

fig.add_trace(go.Scatter(
    x=df_temp["jour"],
    y=croissance.rolling(window=7, center=True).mean(),
    name = "Moyenne mobile du % d'évolution",
    marker_color='black',
#line_width=4,
))

fig.update_yaxes(ticksuffix="%")
fig.update_layout(
    legend_orientation="h",
    annotations=[dict(
                            x=0.5,
                            y=1.08,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Par date de prélèvement sur le patient - @GuillaumeRozier - covidtracker.fr",#'Date : {}. Source : Santé publique France. Auteur : GRZ - covidtracker.fr.'.format(datetime.strptime(max(dates), '%Y-%m-%d').strftime('%d %B %Y')),                    showarrow = False
                            showarrow=False
                        ),],
    title={
                        'text': "Évolution en % du nombre de tests entre J-0 et J-7",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        titlefont = dict(
                        size=30),)
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)


# In[34]:


df_incid_fra_recent = df_incid_fra[-300:]
df_new_france_recent = df_new_france[-300:]

df_incid_fra_recent["taux_incid"] = df_incid_fra["P"].rolling(window=7, center=True).mean()
df_incid_fra_recent["taux_incid_taux_pic"] = df_incid_fra_recent["taux_incid"] / 35000 * 100

df_new_france_recent["dc_rolling"] = df_new_france_recent["incid_dc"].rolling(window=7, center=True).mean()
df_new_france_recent["dc_taux_pic"] = df_new_france_recent["dc_rolling"] /  df_new_france_recent["dc_rolling"].max() * 100

df_new_france_recent["incid_hosp_rolling"] = df_new_france_recent["incid_hosp"].rolling(window=7, center=True).mean()

df_new_france_recent["incid_hosp_taux_pic"] = df_new_france_recent["incid_hosp_rolling"] /  df_new_france_recent["incid_hosp_rolling"].max() * 100

fig = go.Figure()

fig.add_trace(
    go.Scatter(
    x=df_incid_fra_recent["jour"],
    y=df_incid_fra_recent["taux_incid_taux_pic"],
    line=dict(width=3, color="rgb(8, 115, 191)"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" Cas"],
    textposition="middle right",
    mode="lines+text",
    name="cas")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["incid_hosp_taux_pic"],
    line=dict(width=5, color="rgba(225, 230, 235, 0.7)"),
    line_shape='spline',
    textposition="middle right",
    mode="lines+text",
    name="hosp")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["incid_hosp_taux_pic"],
    line=dict(width=3, color="rgb(209, 102, 21)"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" Adm.<br> hôpital<br>"],
    textposition="middle right",
    mode="lines+text",
    name="hosp")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["dc_taux_pic"],
    line=dict(width=5, color="rgba(225, 230, 235, 0.7)"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" Décès"],
    textposition="middle right",
    mode="lines+text",
    name="dc")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["dc_taux_pic"],
    line=dict(width=3, color="black"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" Décès"],
    textposition="middle right",
    mode="lines+text",
    name="dc")
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.2,
    text="<b>La proportion de cas terminant en admission ou décès a diminué</b>",
    font=dict(size=24),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.1,
    text="Cas, admissions à l'hôpital et décès Covid par rapport à leur valeur la plus élevée au printemps 2021.<br>@GuillaumeRozier • Données : Santé publique France • Inspiration @jburnmurdoch",
    font=dict(size=14),
    showarrow=False
)
fig.add_vrect(
    x0="2021-11-30", x1=df_new_france_recent.jour.max(),
    fillcolor="LightSalmon", opacity=0.2,
    layer="below", line_width=0,
),
fig.add_annotation(
    x="2021-11-30",
    y=800,
    text="Apparition<br>d'Omicron",
    xanchor="left",
    font=dict(size=9, color="LightSalmon"),
    showarrow=False
)
fig.update_layout(
    showlegend=False,
    xaxis=dict(showgrid=False),
    yaxis=dict(ticksuffix=" %"),
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(r=50)
)

fig.write_image(PATH + f"images/charts/france/cas_hosp_dc_comparaison_pic.jpeg", scale=2, width=900, height=600)


# In[35]:


df_incid_fra_recent = df_incid_fra[-150:]
df_new_france_recent = df_new_france[-150:]

df_incid_fra_recent["taux_incid"] = df_incid_fra["P"].rolling(window=7, center=True).mean()
df_incid_fra_recent["taux_incid_taux_pic"] = df_incid_fra_recent["taux_incid"] / 35000 * 100

df_new_france_recent["dc_rolling"] = df_new_france_recent["incid_dc"].rolling(window=7, center=True).mean()
df_new_france_recent["dc_taux_pic"] = df_new_france_recent["dc_rolling"] /  df_new_france_recent["dc_rolling"].max() * 100

df_new_france_recent["incid_hosp_rolling"] = df_new_france_recent["incid_hosp"].rolling(window=7, center=True).mean()
df_new_france_recent["incid_rea_rolling"] = df_new_france_recent["incid_rea"].rolling(window=7, center=True).mean()

df_new_france_recent["incid_hosp_taux_pic"] = df_new_france_recent["incid_hosp_rolling"] /  df_new_france_recent["incid_hosp_rolling"].max() * 100

fig = go.Figure()


fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=(df_new_france_recent["incid_rea_rolling"]/df_new_france_recent["incid_hosp_rolling"])*100,
    line=dict(width=5, color=COLOR_PAPER),
    line_shape='spline',
    textposition="middle right",
    mode="lines+text",
    name="hosp")
)
y=(df_new_france_recent["incid_rea_rolling"]/df_new_france_recent["incid_hosp_rolling"])*100
fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=y,
    line=dict(width=3, color="rgb(8, 115, 191)"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [ "  " + str(round(y.values[-4])) + " %"],
    textposition="middle right",
    mode="lines+text",
    name="cas")
)






fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.2,
    text="<b>Proportion d'admissions en soins critiques rapporté aux hospitalisations</b>",
    font=dict(size=22),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.1,
    text="Nombre de nouvelles admissions en soins critiques divisé par les admissions à l'hôpital.<br>@GuillaumeRozier • Données : Santé publique France",
    font=dict(size=14),
    showarrow=False
)

fig.update_layout(
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=True, showline=True),
    yaxis=dict(ticksuffix=" %", zeroline=True, range=[0, 30]),
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(r=50)
)

fig.write_image(PATH + f"images/charts/france/proportion_rea_hosp.jpeg", scale=2, width=900, height=600)


# In[36]:


df_incid_fra_recent = df_incid_fra[-500:]
df_new_france_recent = df_new_france[-500:]

df_incid_fra_recent["taux_incid"] = df_incid_fra["P"].rolling(window=7, center=True).mean()
df_incid_fra_recent["taux_incid_taux_pic"] = df_incid_fra_recent["taux_incid"] / 35000 * 100

df_new_france_recent["dc_rolling"] = df_new_france_recent["incid_dc"].rolling(window=7, center=True).mean()
df_new_france_recent["dc_taux_pic"] = df_new_france_recent["dc_rolling"] /  df_new_france_recent["dc_rolling"].max() * 100

df_new_france_recent["incid_hosp_rolling"] = df_new_france_recent["incid_hosp"].rolling(window=7, center=True).mean()
df_new_france_recent["incid_rea_rolling"] = df_new_france_recent["incid_rea"].rolling(window=7, center=True).mean()

df_new_france_recent["incid_hosp_taux_pic"] = df_new_france_recent["incid_hosp_rolling"] /  df_new_france_recent["incid_hosp_rolling"].max() * 100

fig = go.Figure()


fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=(df_new_france_recent["incid_rea_rolling"].values/df_incid_fra_recent["taux_incid"].shift(8).values)*100,
    line=dict(width=6, color=COLOR_PAPER),
    line_shape='spline',
    textposition="middle right",
    mode="lines+text",
    name="hosp")
)
y=(df_new_france_recent["incid_rea_rolling"].values/df_incid_fra_recent["taux_incid"].shift(8).values)*100
fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=y,
    line=dict(width=4, color="rgb(8, 115, 191)"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [ "  " + str(round(y[-4], 2)) + " %"],
    textposition="middle right",
    mode="lines+text",
    name="cas")
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.2,
    text="<b>Proportion de cas admis en soins critiques</b>",
    font=dict(size=24),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.1,
    text="Nombre de nouvelles admissions en soins critiques divisé par les cas positifs décalés de 8 j.<br>@GuillaumeRozier • Données : Santé publique France",
    font=dict(size=14),
    showarrow=False
)
fig.update_yaxes(ticksuffix="%")
fig.add_vrect(
    x0="2021-11-30", x1=df_new_france_recent.jour.max(),
    fillcolor="LightSalmon", opacity=0.2,
    layer="below", line_width=0,
),
fig.add_annotation(
    x="2021-11-30",
    y=1.8,
    text="Apparition<br>d'Omicron",
    xanchor="left",
    font=dict(size=9, color="LightSalmon"),
    showarrow=False
)
fig.update_layout(
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=True, showline=True),
    yaxis=dict(ticksuffix=" %", zeroline=True),
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(r=50)
)

fig.write_image(PATH + f"images/charts/france/proportion_cas_hosp.jpeg", scale=2, width=900, height=600)


# In[37]:


df_incid_fra_recent = df_incid_fra[-300:]
df_new_france_recent = df_new_france[-300:]

df_incid_fra_recent["taux_incid"] = df_incid_fra["P"].rolling(window=7, center=True).mean()
df_incid_fra_recent["taux_incid_taux_pic"] = df_incid_fra_recent["taux_incid"] / 35000 * 100

df_new_france_recent["dc_rolling"] = df_new_france_recent["incid_dc"].rolling(window=7, center=True).mean()
df_new_france_recent["dc_taux_pic"] = df_new_france_recent["dc_rolling"] /  df_new_france_recent["dc_rolling"].max() * 100

df_new_france_recent["incid_hosp_rolling"] = df_new_france_recent["incid_hosp"].rolling(window=7, center=True).mean()
df_new_france_recent["incid_rea_rolling"] = df_new_france_recent["incid_rea"].rolling(window=7, center=True).mean()

df_new_france_recent["incid_hosp_taux_pic"] = df_new_france_recent["incid_hosp_rolling"] /  df_new_france_recent["incid_hosp_rolling"].max() * 100

fig = go.Figure()

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["incid_rea_rolling"]/df_new_france_recent["incid_rea_rolling"].min()*90,
    line=dict(width=6, color=COLOR_PAPER),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    mode="lines+text",
    showlegend=False,
    name="Admissions soins critiques")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["incid_rea_rolling"]/df_new_france_recent["incid_rea_rolling"].min()*90,
    line=dict(width=3, color="red"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    mode="lines+text",
    name="Admissions soins critiques")
)


fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["incid_hosp_rolling"]/df_new_france_recent["incid_hosp_rolling"].min()*100,
    line=dict(width=6, color=COLOR_PAPER),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    showlegend=False,
    mode="lines+text",
    name="")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=df_new_france_recent["incid_hosp_rolling"]/df_new_france_recent["incid_hosp_rolling"].min()*100,
    line=dict(width=3, color="darkorange"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    mode="lines+text",
    name="Admission hôpital")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=(df_new_france_recent["dc_rolling"]/df_new_france_recent["dc_rolling"].min()).shift(-8)*100,
    line=dict(width=6, color=COLOR_PAPER),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    showlegend=False,
    mode="lines+text",
    name="Décès hôpital")
)

fig.add_trace(
    go.Scatter(
    x=df_new_france_recent["jour"],
    y=(df_new_france_recent["dc_rolling"]/df_new_france_recent["dc_rolling"].min()).shift(-8)*100,
    line=dict(width=3, color="black"),
    line_shape='spline',
    text = [""] * (len(df_new_france_recent["jour"])-4) + [" "],
    textposition="middle right",
    mode="lines+text",
    name="Décès hospitalier")
)

fig.add_vrect(
    x0="2021-11-30", x1=df_new_france_recent.jour.max(),
    fillcolor="LightSalmon", opacity=0.2,
    layer="below", line_width=0,
),
fig.add_annotation(
    x="2021-11-30",
    y=2100,
    text="Apparition d'Omicron",
    xanchor="left",
    font=dict(size=9, color="LightSalmon"),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    x=0.5,
    y=1.2,
    text="<b>Admissions à l'hôpital et en soins critiques</b>",
    font=dict(size=24),
    showarrow=False
)

fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.5,
    y=1.1,
    text="En % par rapport à leur valeur la plus basse des dernières semaines.<br>@GuillaumeRozier • Données : Santé publique France",
    font=dict(size=14),
    showarrow=False
)

fig.update_layout(
    showlegend=True,
    legend_orientation="h",
    xaxis=dict(showgrid=False, zeroline=True, showline=True),
    yaxis=dict(ticksuffix=" %", zeroline=True,),
    paper_bgcolor='rgba(225, 230, 235, 1)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(r=50)
)

fig.write_image(PATH + f"images/charts/france/adm_rea_hosp.jpeg", scale=2, width=900, height=600)

