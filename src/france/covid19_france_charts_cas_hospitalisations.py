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


data.download_data()


# In[4]:


df_hosp_nouveaux_dep = data.import_data_new()
df_hosp_nouveaux_dep = df_hosp_nouveaux_dep[df_hosp_nouveaux_dep["dep"].str.len()<3].groupby("jour").sum().reset_index()

df_tests_viros_dep = data.import_data_tests_viros()
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["cl_age90"]==0]
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["dep"].str.len()<3].groupby("jour").sum().reset_index()

df_metropole = df_tests_viros_dep.merge(df_hosp_nouveaux_dep, left_on="jour", right_on="jour")


# In[5]:


df_hosp_nouveaux_dep = data.import_data_new()
df_hosp_nouveaux_dep = df_hosp_nouveaux_dep[df_hosp_nouveaux_dep["dep"].str.len()==3].groupby("jour").sum().reset_index()

df_tests_viros_dep = data.import_data_tests_viros()
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["cl_age90"]==0]
df_tests_viros_dep = df_tests_viros_dep[df_tests_viros_dep["dep"].str.len()==3].groupby("jour").sum().reset_index()

df_dromcom = df_tests_viros_dep.merge(df_hosp_nouveaux_dep, left_on="jour", right_on="jour")


# In[6]:


df_hosp = data.import_data_hosp_clage().groupby(["jour", "cl_age90"]).sum().reset_index()
df_hosp_nouveaux = data.import_data_new().groupby("jour").sum().reset_index()

df_hosp = df_hosp[df_hosp.cl_age90 == 0].groupby("jour").sum().reset_index()

df_tests_viro = data.import_data_tests_sexe()
df_tests_viro = df_tests_viro[df_tests_viro.cl_age90 == 0].groupby("jour").sum().reset_index()


# In[7]:


df = df_tests_viro.merge(df_hosp_nouveaux, left_on="jour", right_on="jour")

df = df.reset_index()
df["hosp_cas_ratio"] = df.incid_hosp.rolling(window=7).mean()/df.P.rolling(window=7).mean().shift(7) * 100
df["dc_cas_ratio"] = df.incid_dc.rolling(window=7).mean()/df.P.rolling(window=7).mean().shift(14) * 100


# In[8]:


y1 = df.P.rolling(window=7).mean()/67000000*100000
y2 = df.incid_dc.rolling(window=7).mean().shift(-14)/67000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    marker_color='black',
    fillcolor="rgba(0,0,0,0.3)",
    name="D??c??s hospitaliers<br>avanc??s de 14 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
    fill='tozeroy'))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. D??c??s hospitaliers",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et d??c??s hospitaliers avanc??s de 14 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_dc_comparaison"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[9]:



pop=df_metropole["pop"].values[0]
y1 = df_metropole.P.rolling(window=7).mean()/pop*100000
y2 = df_metropole.incid_dc.rolling(window=7).mean().shift(-14)/pop

coef_normalisation = 10000000 #y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    marker_color='black',
    fillcolor="rgba(0,0,0,0.3)",
    name="D??c??s hospitaliers<br>avanc??s de 14 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
    fill='tozeroy'))
fig.update_yaxes(range=[-80, 80])
fig.update_layout(
    title={
                        'text': "Cas vs. D??c??s hospitaliers [Fr. m??trop.]",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et d??c??s hospitaliers avanc??s de 14 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_dc_comparaison_metropole"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[10]:


pop = df_dromcom["pop"].values[0]
y1 = df_dromcom.P.rolling(window=7).mean()/pop*100000
y2 = df_dromcom.incid_dc.rolling(window=7).mean().shift(-14)/pop

coef_normalisation = 10000000#y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    marker_color='black',
    fillcolor="rgba(0,0,0,0.3)",
    name="D??c??s hospitaliers<br>avanc??s de 14 j.<br>pour {} Mio".format(round(coef_normalisation/1000000)),
    fill='tozeroy'))
fig.update_yaxes(range=[-80, 80])
fig.update_layout(
    title={
                        'text': "Cas vs. D??c??s hospitaliers [DROM-COM]",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et d??c??s hospitaliers avanc??s de 14 j. pour {} Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/1000000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_dc_comparaison_dromcom"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[11]:


y1 = df.P.rolling(window=7).mean()/67000000*100000
y2 = df.incid_hosp.rolling(window=7).mean().shift(-7)/67000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. h??pital<br>avanc??es de 7 j.<br>pour {} Mio".format(round(coef_normalisation/100000)),
    marker_color='rgb(209, 102, 21)',
    fillcolor="rgba(209, 102, 21,0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions ?? l'h??pital",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et admissions ?? l'h??pital avanc??es de 7 jours pour {} Million d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/100000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_hospitalisations_comparaison"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[12]:


y1 = df_metropole.P.rolling(window=7).mean()/67000000*100000
y2 = df_metropole.incid_hosp.rolling(window=7).mean().shift(-7)/67000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. h??pital<br>avanc??es de 7 j.<br>pour {} Mio".format(round(coef_normalisation/100000)),
    marker_color='rgb(209, 102, 21)',
    fillcolor="rgba(209, 102, 21,0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions ?? l'h??pital [Fr. m??trop.]",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et admissions ?? l'h??pital avanc??es de 7 jours pour {} Million d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(round(coef_normalisation/100000), datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_hospitalisations_comparaison_metropole"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[13]:


y1 = df.P.rolling(window=7).mean()/67000000*100000
y2 = df.incid_rea.rolling(window=7).mean().shift(-7)/67000000*5000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. soins critiques<br>avanc??es de 7 j.<br>pour 5 Mio",
    marker_color='rgb(201, 4, 4)',
    fillcolor="rgba(201, 4, 4,0.3)",
    fill='tozeroy'))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions en soins critiques",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et admissions en soins critiques (avanc??es de 7j) pour 5 Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_sc_comparaison"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[14]:


y1 = df_metropole.P.rolling(window=7).mean()/67000000*100000
y2 = df_metropole.incid_rea.rolling(window=7).mean().shift(-7)/67000000*5000000

coef_normalisation = y1.max()/y2.max()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    name="Cas pour 100 k",
    marker_color='rgb(8, 115, 191)',
    fillcolor="rgba(8, 115, 191, 0.3)",
    fill='tozeroy'))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y1,
    name="Miroir des cas",
    marker_color='rgba(8, 115, 191, 0.2)',
    line=dict(
        dash="dot")
))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=-y2*coef_normalisation,
    name="Adm. soins critiques<br>avanc??es de 7 j.<br>pour 5 Mio",
    marker_color='rgb(201, 4, 4)',
    fillcolor="rgba(201, 4, 4,0.3)",
    fill='tozeroy'))
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Cas vs. Admissions en soins critiques [Fr. m??trop.]",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.12,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="Cas pour 100 000 habitants et admissions en soins critiques (avanc??es de 7j) pour 5 Millions d'habitants<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

name_fig = "cas_sc_comparaison_metropole"
fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        


# In[15]:



y1 = df.incid_hosp.rolling(window=7).mean().shift()
y2 = df.P.rolling(window=7).mean().shift(7)*0.09

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    line_width=8,
    opacity=0.2,
    name="Adm. h??pital",
    marker_color='orange',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y1,
    line_width=2,
    opacity=1,
    showlegend=False,
    marker_color='orange',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y2,
    line_width=8,
    opacity=0.2,
    name="Estimation adm. h??p.",
    marker_color='rgb(8, 115, 191)',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.add_trace(go.Scatter(
    x=df.jour,
    y=y2,
    line_width=2,
    opacity=1,
    showlegend=False,
    marker_color='rgb(8, 115, 191)',
    #fillcolor="rgba(8, 115, 191, 0.3)",
    ))
fig.update_xaxes(range=["2021-01-01", df.jour.max()])
fig.update_yaxes()
fig.update_layout(
    title={
                        'text': "Estimation des hospitalisations ?? partir des cas",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
    titlefont = dict(
                    size=30),
    annotations = [
                        dict(
                            x=0.5,
                            y=1.17,
                            xref='paper',
                            yref='paper',
                            font=dict(size=14),
                            text="La courbe bleue repr??sente l'estimation des hospitalisations ?? partir des cas,<br>en fixant le taux d'hospitaliastion ?? sa valeur de janvier 2021<br>{} - @GuillaumeRozier - covidtracker.fr".format(datetime.strptime(df.jour.max(), '%Y-%m-%d').strftime('%d %B %Y')),#'Date : {}. Source : Sant?? publique France. Auteur : GRZ - covidtracker.fr.'.format(),                    showarrow = False
                            showarrow=False
                        ),
                        ]
)

#name_fig = "cas_hospitalisations_ratio"
#fig.write_image(PATH + "images/charts/france/{}.jpeg".format(name_fig), scale=2, width=900, height=600)
#plotly.offline.plot(fig, filename = PATH + 'images/html_exports/france/{}.html'.format(name_fig), auto_open=False)
        

