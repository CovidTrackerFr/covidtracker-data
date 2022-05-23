#!/usr/bin/env python
# coding: utf-8

# In[37]:


# Guillaume Rozier - 2020 - MIT License
# This script will automatically tweet new data and graphes on the account @covidtracker_fr

# importing the module 

import france_data_management as data
import math
from datetime import datetime
import locale
import tweepy
import pandas as pd
import secrets as s
from datetime import timedelta
PATH = "../../"

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

"""
Secrets :
    consumer_key ="xxxxxxxxxxxxxxxx"
    consumer_secret ="xxxxxxxxxxxxxxxx"
    access_token ="xxxxxxxxxxxxxxxx"
    access_token_secret ="xxxxxxxxxxxxxxxx"
"""

# authentication 
auth = tweepy.OAuthHandler(s.consumer_key, s.consumer_secret) 
auth.set_access_token(s.access_token, s.access_token_secret) 

api = tweepy.API(auth) 
    
def tweet_france_maps():
    #_, _, dates, _, _, _, _, df_incid, _ = data.import_data()
    #df_incid = df_incid[df_incid["cl_age90"] == 0]
    
    df_incid_fra_clage = data.import_data_tests_viros()
    df_incid = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]
    
    lastday_df_incid = datetime.strptime(df_incid['jour'].max(), '%Y-%m-%d')
    
    ## TWEET2
    df_incid["incidence"] = df_incid["P"].rolling(window=7).sum() / df_incid["pop"] * 100000
    df_incid_lastday = df_incid.loc[df_incid['jour']==df_incid['jour'].max(), :]
    filter_departement_alerte = df_incid_lastday[df_incid_lastday["incidence"] >= 50]
    nb_dep = len(filter_departement_alerte)
    departements_alerte = filter_departement_alerte.departmentName.values
    departements_alerte_valeurs = filter_departement_alerte.incidence.values
    
    images_path2 =[PATH+"images/charts/france/dep-map-incid-cat/latest.jpeg"]
    media_ids2 = []
    
    for filename in images_path2:
        res = api.media_upload(filename)
        media_ids2.append(res.media_id)
        
    tweet = "🔴 {} départements (métropole + DOM-TOM) devraient être classés rouge, car ils dépassent le niveau d'alerte de 50 cas pour 100 000 habitants en 7 jours (données du {})\n➡️ Plus d'infos : covidtracker.fr/covidtracker-france".format(nb_dep, lastday_df_incid.strftime('%d/%m'))
    
    tweet_departements = "Départements dépassant le seuil d'alerte : "
    for (idx, departement) in enumerate(departements_alerte):
        tweet_departements += departement + " (" + str(int(round(departements_alerte_valeurs[idx]))) + "), "
    tweet_departements = tweet_departements[:len(tweet_departements)-2]
    if len(tweet_departements)>240:
        tweet_departements = tweet_departements[:236] + "…"
    first_tweet = api.update_status(status=tweet, media_ids=media_ids2)
    #reply_tweet = api.update_status(status=tweet_departements, 
    #                            in_reply_to_status_id=first_tweet.id, 
    #                            auto_populate_reply_metadata=True)
    
tweet_france_maps()

