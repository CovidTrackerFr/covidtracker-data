#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
LICENSE MIT
2021
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
import json
import france_data_management as data
import math
import numpy as np

show_charts = False
PATH_STATS = "../../data/france/stats/"
PATH = "../../"


# In[3]:


data.download_data()


# In[4]:


df_regions_meta = pd.read_csv(PATH+"data/france/population_grandes_regions.csv")


# In[5]:


#data.download_data_obepine()
#df_obepine = data.import_data_obepine()
#df_obepine_france = df_obepine.groupby("Date").mean().reset_index()


# In[6]:


df_adm_hosp_clage = data.import_data_hosp_ad_age()
#df_adm_hosp_clage["jour"] = pd.to_datetime(df_adm_hosp_clage.Semaine+"-6", format="%Y-S%U-%w").fillna(0)
df_adm_hosp_clage_france = df_adm_hosp_clage.groupby(["jour", "cl_age90"]).sum().fillna(0).reset_index()


# In[7]:


df, df_confirmed, dates, df_new, df_tests, df_deconf, df_sursaud, df_incid, df_tests_viros = data.import_data()


# In[8]:


df_new_france = data.import_data_new().groupby("jour").sum().reset_index()


# In[9]:


df_vue_ensemble = data.import_data_vue_ensemble()


# In[10]:


df_education = data.import_data_education()

df_niveaux_scolaires_fra = data.download_and_import_data_niveaux_scolaires_fra()
df_niveaux_scolaires_reg = data.download_and_import_data_niveaux_scolaires_reg()
df_niveaux_scolaires_dep = data.download_and_import_data_niveaux_scolaires_dep()


# In[11]:


#df_vacsi_a = data.import_data_vacsi_a_fra()
#df_vacsi_a_reg = data.import_data_vacsi_a_reg()
#df_vacsi_a_dep = data.import_data_vacsi_a_dep()

df_vacsi = data.import_data_vacsi_fra() #df_vacsi_a.groupby("jour").sum().reset_index()
df_vacsi_reg = data.import_data_vacsi_reg() #df_vacsi_a_reg.groupby(["jour", "reg"]).sum().reset_index()
df_vacsi_reg = df_vacsi_reg.merge(df_regions_meta, left_on="reg", right_on="code").rename({"n_tot_dose1": "n_cum_dose1"}, axis=1)

df_vacsi_dep = data.import_data_vacsi_dep().rename({"n_tot_dose1": "n_cum_dose1"}, axis=1)
#df_vacsi_a_dep.groupby(["jour", "dep"]).sum().reset_index().rename({"n_tot_dose1": "n_cum_dose1"}, axis=1)


# In[12]:


df_metro = data.import_data_metropoles()
df_metro["jour"] = df_metro["sg"].map(lambda x: x[11:])

df_metro_65 = df_metro[df_metro["cl_age65"] == 65]
df_metro_0 = df_metro[df_metro["cl_age65"] == 0]
metropoles = list(dict.fromkeys(list(df_metro['Metropole'].dropna().values))) 


# In[13]:


df_tests_viros_enrichi = data.import_data_tests_viros()
df_tests_viros_enrichi = df_tests_viros_enrichi.drop("regionName_y", axis=1).rename({"regionName_x": "regionName"}, axis=1)


# In[14]:


df_incid_clage = df_incid.copy()

df_incid_fra_clage = data.import_data_tests_sexe()
df_incid_fra = df_incid_fra_clage[df_incid_fra_clage["cl_age90"]==0]
df_france = df.groupby(["jour"]).sum().reset_index()
df_incid = df_incid[df_incid.cl_age90 == 0]

df_sursaud_france = df_sursaud.groupby(["date_de_passage"]).sum().reset_index()
df_sursaud_regions = df_sursaud.groupby(["date_de_passage", "regionName"]).sum().reset_index()

#df_new_france = df_new.groupby(["jour"]).sum().reset_index()
df_new_regions = df_new.groupby(["jour", "regionName"]).sum().reset_index()


# In[15]:


df_incid_clage_regions = df_incid_clage.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()


# In[16]:


df_tests_viros_regions = df_tests_viros_enrichi.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()
df_tests_viros_france = df_tests_viros_enrichi.groupby(["jour", "cl_age90"]).sum().reset_index()


# In[17]:


df_hosp_clage = data.import_data_hosp_clage()
df_hosp_clage_france = df_hosp_clage.groupby(["jour", "cl_age90"]).sum().reset_index()
df_hosp_clage_regions = df_hosp_clage.groupby(["regionName", "jour", "cl_age90"]).sum().reset_index()


# In[18]:


departements = list(dict.fromkeys(list(df_incid['dep'].values)))
regions = list(dict.fromkeys(list(df_incid['regionName'].dropna().values))) 
clage_list = list(dict.fromkeys(list(df_incid_fra_clage['cl_age90'].dropna().values))) 

df_regions = df.groupby(["jour", "regionName"]).sum().reset_index()
df_incid_regions = df_incid.groupby(["jour", "regionName"]).sum().reset_index()


zone_a = ["zone_a", "01", "03", "07", "15", "16", "17", "19", "21", "23", "24", "25", "26", "33", "38", "39", "40", "42", "43", "47", "58", "63", "64", "69", "70", "71", "73", "74", "79", "86", "90"]
zone_b = ["zone_b", "02", "04", "05", "06", "08", "10", "13", "14", "18", "22", "27", "28", "29", "35", "36", "37", "41", "44", "45", "49", "50", "51", "52", "53", "54", "55", "56", "57", "59", "60", "61", "62", "67", "68", "72", "76", "80", "83", "84", "85", "88"]
zone_c = ["zone_c", "09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "75", "77", "78", "81", "82", "91", "92", "93", "94", "95"]

confines_mars_2021 = ["confines_mars_2021", "02", "06", "27", "59", "60", "62", "75", "76", "77", "78", "80", "91", "92", "93", "94", "95"]


# In[19]:


df_opendata_indicateurs = data.download_and_import_opendata_indicateurs()


# In[20]:


def generate_data(data_incid=pd.DataFrame(), data_hosp=pd.DataFrame(), data_sursaud=pd.DataFrame(), data_new=pd.DataFrame(), data_vue_ensemble=pd.DataFrame(), data_metropole=pd.DataFrame(), data_vacsi=pd.DataFrame(), data_obepine=pd.DataFrame(), data_opendata_indicateurs=pd.DataFrame(), mode="", export_jour=False, taux_croissance=False):## Incidence
        
    dict_data = {}
    
    if export_jour:
        dict_data["jour_incid"] = list(data_incid.jour)
        dict_data["jour_hosp"] = list(data_hosp.jour)
        dict_data["jour_new"] = list(data_new.jour)
        dict_data["jour_sursaud"] = list(data_sursaud.date_de_passage)
        dict_data["jour_metropoles"] = list(data_metropole.jour.unique())
        dict_data["jour_vacsi"] = list(data_vacsi.jour)
        dict_data["jour_obepine"] = "" #list(data_obepine.Date)
        
    if (taux_croissance) and (len(data_incid)>0):
        cas = data_incid["P"].fillna(0)
        taux_croissance_cas = ((cas-cas.shift(7))/cas.shift(7).replace(0, None)).fillna(0) * 100
        taux_croissance_cas[taux_croissance_cas>200]=200
        taux_croissance_cas[taux_croissance_cas<-200]=-200
        
        cas_rolling = data_incid["P"].rolling(window=7, center=True).mean().fillna(0)
        taux_croissance_cas_rolling = ((cas_rolling-cas_rolling.shift(7))/cas_rolling.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_cas"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_croissance_cas, 1))}
        dict_data["croissance_cas_rolling7"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_croissance_cas_rolling, 1))}
        
        tests = data_incid["T"].rolling(window=7).mean().fillna(0)
        taux_croissance_tests= ((tests-tests.shift(7))/tests.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_tests"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_croissance_tests, 1))}
        dict_data["croissance_tests_rolling7"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_croissance_tests.rolling(window=7, center=True).mean().fillna(0), 1))}
        
    if (taux_croissance) and (len(data_hosp)>0):
        hospitalisations = data_hosp.hosp.fillna(0)
        taux_croissance_hospitalisations = ((hospitalisations-hospitalisations.shift(7))/hospitalisations.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(round(taux_croissance_hospitalisations, 1))}
        dict_data["croissance_hospitalisations_rolling7"] = {"jour_nom": "jour_hosp", "valeur": list(round(taux_croissance_hospitalisations.rolling(window=7, center=True).mean().fillna(0), 1))}
        
        reanimations = data_hosp.rea.fillna(0)
        taux_croissance_reanimations = ((reanimations-reanimations.shift(7))/reanimations.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(round(taux_croissance_reanimations, 1))}
        dict_data["croissance_reanimations_rolling7"] = {"jour_nom": "jour_hosp", "valeur": list(round(taux_croissance_reanimations.rolling(window=7, center=True).mean().fillna(0), 1))}
    
    if (taux_croissance) and (len(data_new)>0):
        hospitalisations = data_new.incid_hosp.fillna(0)
        taux_croissance_hospitalisations = ((hospitalisations-hospitalisations.shift(7))/hospitalisations.shift(7).replace(0, None)).fillna(0) * 100
        
        hospitalisations_rolling = data_new.incid_hosp.fillna(0).rolling(window=7, center=True).mean()
        taux_croissance_hospitalisations_rolling = ((hospitalisations_rolling-hospitalisations_rolling.shift(7))/hospitalisations_rolling.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_incid_hospitalisations"] = {"jour_nom": "jour_new", "valeur": list(round(taux_croissance_hospitalisations, 1))}
        dict_data["croissance_incid_hospitalisations_rolling7"] = {"jour_nom": "jour_new", "valeur": list(round(taux_croissance_hospitalisations_rolling, 1))}
        
        reanimations = data_new.incid_rea.fillna(0)
        taux_croissance_reanimations = ((reanimations-reanimations.shift(7))/reanimations.shift(7).replace(0, None)).fillna(0) * 100
        
        reanimations_rolling = data_new.incid_rea.fillna(0).rolling(window=7, center=True).mean()
        taux_croissance_reanimations_rolling = ((reanimations_rolling-reanimations_rolling.shift(7))/reanimations_rolling.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_incid_reanimations"] = {"jour_nom": "jour_new", "valeur": list(round(taux_croissance_reanimations, 1))}
        dict_data["croissance_incid_reanimations_rolling7"] = {"jour_nom": "jour_new", "valeur": list(round(taux_croissance_reanimations_rolling, 1))}
    
    if (taux_croissance)and len(data_opendata_indicateurs):
        dict_data["jour_spf_opendata"] = list(data_opendata_indicateurs[["date", "conf_j1"]].dropna().date)
        
        data_opendata_indicateurs["conf_j1_corrige"] = data_opendata_indicateurs["conf"].diff()
        data_opendata_indicateurs.loc[data_opendata_indicateurs["date"]=="2021-05-20", "conf_j1_corrige"] = 15000
        
        #cas_spf_opendata = data_opendata_indicateurs["conf_j1_corrige"].fillna(0)
        cas_spf_opendata = data_opendata_indicateurs["conf_j1"].dropna()
            
        taux_croissance_cas_spf_opendata = ((cas_spf_opendata-cas_spf_opendata.shift(7))/cas_spf_opendata.shift(7).replace(0, None)).fillna(0) * 100
        cas_spf_opendata_rolling = cas_spf_opendata.rolling(window=7, center=True).mean().fillna(0)
        taux_croissance_cas_spf_opendata_rolling = ((cas_spf_opendata_rolling-cas_spf_opendata_rolling.shift(7))/cas_spf_opendata_rolling.shift(7).replace(0, None)).fillna(0) * 100
        
        dict_data["croissance_cas_spf_opendata"] = {"jour_nom": "jour_spf_opendata", "valeur": list(round(taux_croissance_cas_spf_opendata, 1))}
        dict_data["croissance_cas_spf_opendata_rolling7"] = {"jour_nom": "jour_spf_opendata", "valeur": list(round(taux_croissance_cas_spf_opendata_rolling, 1))}
        
        cas_spf_opendata_corrige = data_opendata_indicateurs[["date", "conf_j1_corrige"]]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-02", "conf_j1_corrige"] = cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-04-25", "conf_j1_corrige"].values[0] * 0.7
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-09", "conf_j1_corrige"] = cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-02", "conf_j1_corrige"].values[0] * 0.7
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-14", "conf_j1_corrige"] = 0.7 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-07"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-25", "conf_j1_corrige"] = 0.7 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-05-18"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-07-15", "conf_j1_corrige"] = 1.8 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-07-08"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-11-02", "conf_j1_corrige"] = 1.1 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-10-26"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-11-12", "conf_j1_corrige"] = 1.3 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-11-05"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-12-26", "conf_j1_corrige"] = 1.5 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-12-19"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-01-01", "conf_j1_corrige"] = 2 * cas_spf_opendata_corrige.loc[cas_spf_opendata_corrige.date == "2021-12-25"]["conf_j1_corrige"].values[0]
        cas_spf_opendata_corrige = cas_spf_opendata_corrige["conf_j1_corrige"].rolling(window=7).mean().fillna(0)
        
        dict_data["cas_spf_opendata_rolling_corrige"] = {"jour_nom": "jour_spf_opendata", "valeur": list(round(cas_spf_opendata_corrige, 1))}

    if(len(data_vacsi)>0):
        n_cum_dose1 = data_vacsi["n_cum_dose1"].fillna(0)
        dict_data["n_cum_dose1"] = {"jour_nom": "jour_vacsi", "valeur": list(n_cum_dose1)}
        
        n_dose1 = data_vacsi["n_dose1"].rolling(window=7).mean().fillna(0)
        dict_data["n_dose1"] = {"jour_nom": "jour_vacsi", "valeur": list(round(n_dose1, 1))}
    
    if len(data_vue_ensemble)>0:
        dict_data["jour_ehpad"] = list(data_vue_ensemble.date)
        deces_ehpad = data_vue_ensemble["total_deces_ehpad"].diff().rolling(window=7).mean().fillna(0)
        dict_data["deces_ehpad"] = {"jour_nom": "jour_ehpad", "valeur": list(round(deces_ehpad,2))}
        
        cas_spf = data_vue_ensemble.total_cas_confirmes.diff().fillna(0)
        cas_spf[cas_spf<0] = 0
        cas_spf = cas_spf.replace(to_replace=0, method='ffill')
        cas_spf_rolling = cas_spf.rolling(window=7).mean().fillna(0)
        dict_data["cas_spf"] = {"jour_nom": "jour_ehpad", "valeur": list(round(cas_spf_rolling, 2))}
        dict_data["cas_spf_brut"] = {"jour_nom": "jour_ehpad", "valeur": list(round(cas_spf, 2))}
        
    if len(data_opendata_indicateurs):
        dict_data["jour_spf_opendata"] = list(data_opendata_indicateurs[["date", "conf_j1"]].dropna().date)
        #cas_spf_opendata = data_opendata_indicateurs["conf_j1_corrige"].fillna(0)
        cas_spf_opendata = data_opendata_indicateurs["conf_j1"].dropna()
        cas_spf_opendata_rolling = cas_spf_opendata.rolling(window=7).mean().fillna(0)
        
        dict_data["cas_spf_opendata"] = {"jour_nom": "jour_spf_opendata", "valeur": list(cas_spf_opendata)}
        dict_data["cas_spf_opendata_rolling"] = {"jour_nom": "jour_spf_opendata", "valeur": list(round(cas_spf_opendata_rolling, 2))}
        
        
    if len(data_obepine)>0:
        indicateur_obepine = data_obepine.Indicateur.fillna(0)
        
        dict_data["obepine"] = {"jour_nom": "jour_obepine", "jours":list(data_obepine.Date), "valeur": list(round(indicateur_obepine, 2))}
        
    if len(data_incid)>0:
        taux_incidence = data_incid["P"].rolling(window=7).sum().fillna(0) * 100000 / int(data_incid["pop"].values[0])
        dict_data["incidence"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_incidence, 1))}

        taux_positivite = (data_incid["P"] / data_incid["T"] * 100).rolling(window=7).mean().fillna(0)
        dict_data["taux_positivite"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite, 2))}
        
        taux_positivite = (data_incid["P"].rolling(window=7).mean() / data_incid["T"].rolling(window=7).mean() * 100).fillna(0)
        dict_data["taux_positivite_rolling_before"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite, 2))}
    
        cas = data_incid["P"].rolling(window=7).mean().fillna(0)
        dict_data["cas"] = {"jour_nom": "jour_incid", "valeur": list(round(cas, 1))}
        
        cas = data_incid["P"].fillna(0)
        dict_data["cas_brut"] = {"jour_nom": "jour_incid", "valeur": list(round(cas, 1))}
        
        cas_total = data_incid["P"].sum()
        dict_data["cas_total"] = {"jour_nom": "jour_incid", "valeur": int(cas_total)}
    
        tests = data_incid["T"].rolling(window=7).mean().fillna(0)
        dict_data["tests"] = {"jour_nom": "jour_incid", "valeur": list(round(tests, 1))}
        
        tests_total = data_incid["T"].sum()
        dict_data["tests_total"] = {"jour_nom": "jour_incid", "valeur": int(tests_total)}
        
    if (len(data_metropole)>0) & (mode=="metropoles"):
        taux_incidence = data_metropole["ti"].fillna(0)
        dict_data["incidence"] = {"jour_nom": "jour_metropoles", "valeur": list(round(taux_incidence, 1))}
        
    if (taux_croissance) and (len(data_hosp)>0):
        hospitalisations_rolling = data_hosp.hosp.rolling(window=7).mean().fillna(0)
        croissance_hospitalisations = ((hospitalisations_rolling-hospitalisations_rolling.shift(7))/hospitalisations_rolling.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(round(croissance_hospitalisations, 1))}
        
        sc_rolling = data_hosp.rea.rolling(window=7).mean().fillna(0)
        croissance_sc = ((sc_rolling-sc_rolling.shift(7))/sc_rolling.shift(7).replace(0, None)).fillna(0) * 100
        dict_data["croissance_reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(round(croissance_sc, 1))}
        
    if len(data_hosp)>0:
        hospitalisations = data_hosp["hosp"].fillna(0)
        dict_data["hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(hospitalisations)}

        reanimations = data_hosp.rea.fillna(0)
        dict_data["reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(reanimations)}
        
        saturation_rea = round(data_hosp["rea"]/data_hosp["LITS"].fillna(0)*100, 1)
        dict_data["saturation_reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(saturation_rea)}
    
    if len(data_new)>0:
        incid_hospitalisations = data_new.incid_hosp.rolling(window=7).mean().fillna(0)
        dict_data["incid_hospitalisations"] = {"jour_nom": "jour_new", "valeur": list(round(incid_hospitalisations, 1))}
        
        incid_hospitalisations_total = data_new.incid_hosp.sum()
        dict_data["incid_hospitalisations_total"] = {"jour_nom": "jour_new", "valeur": int(incid_hospitalisations_total)}

        incid_reanimations = data_new.incid_rea.rolling(window=7).mean().fillna(0)
        dict_data["incid_reanimations"] = {"jour_nom": "jour_new", "valeur": list(round(incid_reanimations, 1))}
        
        incid_reanimations_total = data_new.incid_rea.sum()
        dict_data["incid_reanimations_total"] = {"jour_nom": "jour_new", "valeur": int(incid_reanimations_total)}
    
    if len(data_sursaud)>0:
        nbre_acte_corona = data_sursaud.nbre_acte_corona.rolling(window=7).mean().fillna(0)
        dict_data["nbre_acte_corona"] = {"jour_nom": "jour_sursaud", "valeur": list(round(nbre_acte_corona, 1))}

        nbre_pass_corona = data_sursaud.nbre_pass_corona.rolling(window=7).mean().fillna(0)
        dict_data["nbre_pass_corona"] = {"jour_nom": "jour_sursaud", "valeur": list(round(nbre_pass_corona,  1))}
    
    if len(data_new)>0:
        deces_hospitaliers = data_new.incid_dc
        taux_croissance_deces_hospitaliers = ((deces_hospitaliers-deces_hospitaliers.shift(7))/deces_hospitaliers.shift(7).replace(0, None)).fillna(0) * 100
        
        deces_hospitaliers_rolling = data_new.incid_dc.rolling(window=7, center=False).mean().fillna(0)
        taux_croissance_deces_hospitaliers_rolling = ((deces_hospitaliers_rolling-deces_hospitaliers_rolling.shift(7))/deces_hospitaliers_rolling.shift(7).replace(0, None)).fillna(0) * 100
        
        dict_data["deces_hospitaliers"] = {"jour_nom": "jour_new", "valeur": list(round(deces_hospitaliers_rolling, 1))}
        dict_data["croissance_deces_hospitaliers"] = {"jour_nom": "jour_new", "valeur": list(round(taux_croissance_deces_hospitaliers, 1))}
        dict_data["croissance_deces_hospitaliers_rolling7"] = {"jour_nom": "jour_new", "valeur": list(round(taux_croissance_deces_hospitaliers_rolling, 1))}
        
        deces_hospitaliers_total = data_new.incid_dc.sum()
        dict_data["deces_hospitaliers_total"] = {"jour_nom": "jour_new", "valeur": int(deces_hospitaliers_total)}
    
    if len(data_incid)>0:
        population = data_incid["pop"].values[0]
        dict_data["population"] = population

    return dict_data


# In[21]:


def generate_data_age(data_incid, data_hosp, data_adm_hosp_clage=pd.DataFrame(), export_jour=False):## Incidence
    clage_tranches = [["9", "19", "29", "39", "49", "59", "69", "79", "89", "90"], ["9", "19"], ["29", "39"], ["49", "59"], ["69", "79"], ["89", "90"]]
    clage_noms = ["tous", "19", "39", "59", "79", "90"]
    clage_noms_disp = ["Tous âges", "0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 79 ans", "Plus de 80 ans"]
    
    dict_data = {}
    
    for (idx, clage) in enumerate(clage_tranches):
        clage_nom = clage_noms[idx]
        
        data_incid_clage = data_incid[data_incid.cl_age90.isin(clage)].groupby("jour").sum().reset_index()

        dict_data[clage_nom] = {}

        taux_incidence = data_incid_clage["P"].rolling(window=7).sum().fillna(0) * 100000 / data_incid_clage["pop"].values[0]
        dict_data[clage_nom]["incidence"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_incidence,0))}

        taux_positivite = (data_incid_clage["P"] / data_incid_clage["T"] * 100).rolling(window=7).mean().fillna(0)
        dict_data[clage_nom]["taux_positivite"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_positivite,2))}

        cas = data_incid_clage["P"].rolling(window=7).mean().fillna(0)
        dict_data[clage_nom]["cas"] = {"jour_nom": "jour_incid", "valeur": list(round(cas, 1))}
        
        taux_croissance_cas = ((cas-cas.shift(7))/cas.shift(7).replace(0, None)).fillna(0) * 100
        taux_croissance_cas[taux_croissance_cas>200] = 200
        taux_croissance_cas[taux_croissance_cas<-200] = -200
        #taux_croissance_cas = taux_croissance_cas.rolling(window=7).mean().fillna(0)
        dict_data[clage_nom]["cas_croissance_hebdo"] = {"jour_nom": "jour_incid", "valeur": list(round(taux_croissance_cas, 1))}

        tests = data_incid_clage["T"].rolling(window=7).mean().fillna(0)
        dict_data[clage_nom]["tests"] = {"jour_nom": "jour_incid", "valeur": list(round(tests, 1))}
        
        population = data_incid_clage["pop"].values[0]
        dict_data[clage_nom]["population"] = population
        
        if (len(data_hosp)):  
            data_hosp_clage = data_hosp[data_hosp.cl_age90.isin(clage)].groupby("jour").sum().reset_index()
            hospitalisations = data_hosp_clage.hosp.fillna(0)
            dict_data[clage_nom]["hospitalisations"] = {"jour_nom": "jour_hosp", "valeur": list(hospitalisations)}

            reanimations = data_hosp_clage.rea.fillna(0)
            dict_data[clage_nom]["reanimations"] = {"jour_nom": "jour_hosp", "valeur": list(reanimations)}

            deces_hospitaliers = data_hosp_clage.dc.diff().rolling(window=7).mean().fillna(0)
            dict_data[clage_nom]["deces_hospitaliers"] = {"jour_nom": "jour_hosp", "valeur": list(round(deces_hospitaliers, 1))}
        
        if(len(data_adm_hosp_clage)):
            df_adm_hosp_clage_temp = data_adm_hosp_clage[data_adm_hosp_clage.cl_age90.isin(clage)].groupby("jour").sum().reset_index()
            adm_hospitalisations = df_adm_hosp_clage_temp["NewAdmHospit"]
            dict_data[clage_nom]["adm_hospitalisations"] = {"jour_nom": "jour_adm_hosp_clage", "valeur": list(round(adm_hospitalisations/7, 1))}
            
    if export_jour:
            dict_data["jour_incid"] = list(data_incid.jour.unique())
            dict_data["jour_hosp"] = list(data_hosp.jour.unique())
            dict_data["tranches"] = clage_tranches
            dict_data["tranches_noms"] = clage_noms
            dict_data["tranches_noms_affichage"] = clage_noms_disp
            
            if(len(data_adm_hosp_clage)):
                dict_data["jour_adm_hosp_clage"] = list(data_adm_hosp_clage.jour.dt.strftime('%Y-%m-%d').unique())

    return dict_data
 


# In[22]:


def generate_data_niveaux_scolaires(data_incid_niveaux_scolaires, export_jour=False):
    dict_data={}
    clage_tranches = ["0", "2", "5", "10", "14", "17", "18"]
    clage_noms = ["tous_scol", "02_scol", "05_scol", "10_scol", "14_scol", "17_scol", "18_scol"]
    clage_noms_disp = ["Tous", "0 - 2 ans", "3 - 5 ans", "6 - 10 ans", "11 - 14 ans", "15 - 17 ans", "plus 18 ans"]
    
    for (idx, clage) in enumerate(clage_tranches):
        clage_nom = clage_noms[idx]
        data_incid_niveaux_scolaires_clage = data_incid_niveaux_scolaires[data_incid_niveaux_scolaires.age_18ans == clage].reset_index()

        dict_data[clage_nom] = {}

        taux_incidence = data_incid_niveaux_scolaires_clage["ti"]
        taux_depistage = data_incid_niveaux_scolaires_clage["td"]
        taux_positivite = data_incid_niveaux_scolaires_clage["tp"]
        
        dict_data[clage_nom]["incidence"] = {"jour_nom": "jour_niveaux_scolaires", "valeur": round(taux_incidence.astype(float)).astype(int).tolist()}
        dict_data[clage_nom]["depistage"] = {"jour_nom": "jour_niveaux_scolaires", "valeur": round(taux_depistage.astype(float)).astype(int).tolist()}
        dict_data[clage_nom]["positivite"] = {"jour_nom": "jour_niveaux_scolaires", "valeur": round(taux_positivite.astype(float), 1).tolist()}
            
    if export_jour:
            dict_data["jour_niveaux_scolaires"] = list(data_incid_niveaux_scolaires.jour.unique().astype(str))
            dict_data["tranches_scolaires"] = clage_tranches
            dict_data["tranches_noms_scolaires"] = clage_noms
            dict_data["tranches_noms_affichage_scolaires"] = clage_noms_disp

    return dict_data
 


# In[23]:


def generate_data_education(df_education):
    clage_noms = [2, 5, 10, 14, 17, 18]
    clage_disp = ["0 - 2 ans", "3 - 5 ans", "6 - 10 ans", "11 - 14 ans", "15 - 17 ans", "Plus 18 ans"]
    
    dict_data = {}
    dict_data["tranches_noms"] = clage_noms
    dict_data["tranches_noms_affichage"] = clage_disp
    
    for clage in clage_noms:
        dict_data[clage] = {}
        
        df_temp = df_education[df_education["age_18ans"]==clage]
        
        dict_data[clage]["Ti"] = df_temp["Ti"].fillna(0).tolist()
        dict_data[clage]["Tp"] = df_temp["Tp"].fillna(0).tolist()
        dict_data[clage]["Td"] = df_temp["Td"].fillna(0).tolist()
        
    return dict_data


# In[24]:


def export_data(data, suffix=""):
    with open(PATH_STATS + 'dataexplorer{}.json'.format(suffix), 'w') as outfile:
        json.dump(data, outfile)


# In[25]:


def dataexplorer():
    dict_data = {}
    
    regions = sorted(list(df_regions.regionName.unique()))
    departements = list(df.dep.unique())
    
    dict_data["regions"] = regions
    dict_data["metropoles"] = sorted(metropoles)
    dict_data["departements"] = departements
    dict_data["france"] = generate_data(df_incid_fra, df_france, df_sursaud_france, df_new_france, df_vue_ensemble, data_metropole=df_metro_0, data_vacsi=df_vacsi, data_obepine=df_obepine_france, data_opendata_indicateurs=df_opendata_indicateurs, mode="france", export_jour=True, taux_croissance=True)
    dict_data["metropole"] = generate_data(df_incid[df_incid["dep"].str.len()<=2].groupby(["jour"]).sum(), df[df["dep"].str.len()<=2].groupby(["jour"]).sum(), df_sursaud[df_sursaud["dep"].str.len()<=2].groupby(["date_de_passage"]).sum(), df_new[df_new["dep"].str.len()<=2].groupby(["jour"]).sum(), data_vacsi=df_vacsi_dep[df_new["dep"].str.len()<=2].groupby(["jour"]).sum())
    dict_data["drom_com"] = generate_data(df_incid[df_incid["dep"].str.len()>2].groupby(["jour"]).sum(), df[df["dep"].str.len()>2].groupby(["jour"]).sum(), df_sursaud[df_sursaud["dep"].str.len()>2].groupby(["date_de_passage"]).sum(), df_new[df_new["dep"].str.len()>2].groupby(["jour"]).sum(), data_vacsi=df_vacsi_dep[df_new["dep"].str.len()>2].groupby(["jour"]).sum())

    noms_departements={}
    
    for reg in regions:
        print(reg)
        data_hosp = df_regions[df_regions.regionName==reg]
        dict_data[reg] = generate_data(data_incid=df_incid_regions[df_incid_regions.regionName==reg],                                        data_hosp=data_hosp,                                       data_sursaud=df_sursaud_regions[df_sursaud_regions.regionName==reg],
                                       data_new=df_new_regions[df_new_regions.regionName==reg],
                                       data_vacsi=df_vacsi_reg[df_vacsi_reg.regionName==reg],\
                                       data_obepine=df_obepine[df_obepine.regionName==reg]
                                      )
    print("Regions : done")
    
    for dep in departements:
        print(dep)
        df_incid_dep = df_incid[df_incid.dep==dep]
        df_dep = df[df.dep==dep]
        dict_data[dep] = generate_data(data_incid=df_incid_dep, 
                                       data_hosp=df_dep,
                                       data_sursaud=df_sursaud[df_sursaud.dep==dep],
                                       data_new=df_new[df_new.dep==dep],
                                       data_vacsi=df_vacsi_dep[df_vacsi_dep.dep==dep])
        noms_departements[dep] = df_dep["departmentName"].values[0]
    dict_data["departements_noms"] = noms_departements
    
    for zone in [zone_a, zone_b, zone_c]:
        df_incid_zone = df_incid[df_incid.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_zone = df[df.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_sursaud_zone = df_sursaud[df_sursaud.dep.isin(zone)].groupby("date_de_passage").sum().reset_index()
        df_new_zone = df_new[df_new.dep.isin(zone)].groupby("jour").sum().reset_index()
        df_vacsi_zone = df_vacsi_dep[df_vacsi_dep.dep.isin(zone)].groupby("jour").sum().reset_index()
        
        dict_data[zone[0]] = generate_data(df_incid_zone, df_zone, df_sursaud_zone, df_new_zone, data_vacsi=df_vacsi_zone)
    
    # Confinés mars 2021
    df_incid_zone = df_incid[df_incid.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    df_zone = df[df.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    df_sursaud_zone = df_sursaud[df_sursaud.dep.isin(confines_mars_2021)].groupby("date_de_passage").sum().reset_index()
    df_new_zone = df_new[df_new.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    df_vacsi_zone = df_vacsi_dep[df_vacsi_dep.dep.isin(confines_mars_2021)].groupby("jour").sum().reset_index()
    
    dict_data["confines_mars_2021"] = generate_data(df_incid_zone, df_zone, df_sursaud_zone, df_new_zone, data_vacsi=df_vacsi_zone)
        
    for metropole in metropoles:
        print(metropole)
        dict_data[metropole] = generate_data(data_metropole=df_metro_0[df_metro_0.Metropole == metropole], mode="metropoles")
        
    dict_data["zones_vacances"] = ["zone_a", "zone_b", "zone_c"]
    
    export_data(dict_data, suffix="_compr")
    export_data(dict_data["france"], suffix="_compr_france")
    return dict_data


# In[26]:


def dataexplorer_age():
    dict_data = {}
    regions_tests_viros = list(dict.fromkeys(list(df_tests_viros_enrichi['regionName'].dropna().values))) 
    departements_tests_viros = list(dict.fromkeys(list(df_tests_viros_enrichi['dep'].dropna().values))) 
    dict_data["regions"] = sorted(regions_tests_viros)
    dict_data["departements"] = sorted(departements_tests_viros)
    
    dict_data["france"] = generate_data_age(df_tests_viros_france, df_hosp_clage_france, data_adm_hosp_clage=df_adm_hosp_clage_france, export_jour=True)
    
    for reg in regions_tests_viros:
        dict_data[reg] = generate_data_age(df_tests_viros_regions[df_tests_viros_regions.regionName == reg],                                           df_hosp_clage_regions[df_hosp_clage_regions.regionName == reg]) #data_adm_hosp_clage=data_adm_hosp_clage
    noms_departements={}
    for dep in departements_tests_viros:
        df_tests_viros_enrichi_temp = df_tests_viros_enrichi[df_tests_viros_enrichi.dep == dep]
        dict_data[dep] = generate_data_age(df_tests_viros_enrichi_temp,                                           pd.DataFrame())
        
        nom_dep = df_tests_viros_enrichi_temp["departmentName"].values[0]
        
        if(type(nom_dep) is float): #Pas de nom, nom_dep == NaN
            #print(dep)
            nom_dep = "--"
        
        noms_departements[dep] = nom_dep
        
    dict_data["departements_noms"] = noms_departements
    
    export_data(dict_data, suffix="_compr_age")
    return dict_data


# In[27]:


def dataexplorer_education():
    dict_data = {}
    dict_data["france"] = generate_data_education(df_education=df_education)
    export_data(dict_data, suffix="_education")


# In[28]:


def dataexplorer_niveaux_scolaires():
    df_niveaux_scolaires_dep_sorted = df_niveaux_scolaires_dep.sort_values(by="dep")
    df_niveaux_scolaires_reg_sorted = df_niveaux_scolaires_reg.sort_values(by="reg")
    
    dict_data = {}
    
    dict_data["departements_noms"] = list(df_niveaux_scolaires_dep_sorted["departmentName"].unique().astype(str))
    dict_data["departements"] = list(df_niveaux_scolaires_dep_sorted["dep"].unique().astype(str))
    
    dict_data["regions_noms"] = list(df_niveaux_scolaires_reg_sorted["regionName"].unique().astype(str))
    dict_data["regions"] = dict_data["regions_noms"] #list(df_niveaux_scolaires_reg_sorted["reg"].unique().astype(str))
    
    dict_data["france"] = generate_data_niveaux_scolaires(data_incid_niveaux_scolaires=df_niveaux_scolaires_fra, export_jour=True)
    
    for dep in dict_data["departements"]:
        data_incid_niveaux_scolaires_dep_temp = df_niveaux_scolaires_dep[df_niveaux_scolaires_dep["dep"] == dep]
        dict_data[dep] = generate_data_niveaux_scolaires(data_incid_niveaux_scolaires=data_incid_niveaux_scolaires_dep_temp, export_jour=False)
        
    for reg in dict_data["regions_noms"]:
        print(reg)
        data_incid_niveaux_scolaires_reg_temp = df_niveaux_scolaires_reg[df_niveaux_scolaires_reg["regionName"] == reg]
        dict_data[reg] = generate_data_niveaux_scolaires(data_incid_niveaux_scolaires=data_incid_niveaux_scolaires_reg_temp, export_jour=False)
    
    export_data(dict_data, suffix="_education")
    return dict_data


# In[29]:


def data_nouveau_dashboard_france():
    data={}
    name="hospitalisations_par_age"
    
    df = df_hosp_clage_france[df_hosp_clage_france["jour"]==df_hosp_clage_france["jour"].max()]
    df = df[df["cl_age90"] != 0].sort_values(by="cl_age90")
    
    data["cl_age90"] = ["0-9 ans", "10-19 ans", "20-29 ans", "30-39 ans", "40-49 ans", "50-59 ans", "60-69 ans", "70-79 ans", "80-89 ans", "+ 90 ans"]
    data["hosp"] = df["hosp"].fillna(0).tolist()
    data["rea"] = df["rea"].fillna(0).tolist()
    
    with open(PATH_STATS + 'api/{}.json'.format(name), 'w') as outfile:
        json.dump(data, outfile)


# In[30]:


data_nouveau_dashboard_france()


# In[31]:


dict_ns = dataexplorer_niveaux_scolaires()


# In[32]:


dict_dataexplorer = dataexplorer()


# In[33]:


dict_data = dataexplorer_age()


# In[34]:


def objectif_deconfinement():
    dict_json = {}
    n = 70
    
    ## HOSP
    struct = {"dates": [], "values": []}
    dict_json["hosp"] = struct
    dict_json["hosp"]["values"] = [float(round(x, 1)) for x in df_france["hosp"].values[-n:]]
    dict_json["hosp"]["dates"] = list(df_france["jour"].values[-n:])
    
    ## HOSP ADM
    struct = {"dates": [], "values": []}
    dict_json["adm_hosp"] = struct
    dict_json["adm_hosp"]["values"] = [float(round(x, 1))for x in df_new_france["incid_hosp"].rolling(window=7).mean().dropna(0).values[-n:]]
    dict_json["adm_hosp"]["dates"] = list(df_new_france["jour"].values[-n:])
    
    ## REA
    struct = {"dates": [], "values": []}
    dict_json["rea"] = struct
    dict_json["rea"]["values"] = [float(round(x, 1)) for x in df_france["rea"].values[-n:]]
    dict_json["rea"]["dates"] = list(df_france["jour"].values[-n:])
    
    ## REA ADM
    struct = {"dates": [], "values": []}
    dict_json["adm_rea"] = struct
    dict_json["adm_rea"]["values"] = [float(round(x, 1)) for x in df_new_france["incid_rea"].rolling(window=7).mean().dropna(0).values[-n:]]
    dict_json["adm_rea"]["dates"] = list(df_new_france["jour"].values[-n:])
    
    ## DC
    struct = {"dates": [], "values": []}
    dict_json["dc"] = struct
    dict_json["dc"]["values"] = [float(round(x, 1)) for x in df_new_france["incid_dc"].rolling(window=7).mean().fillna(0).values[-n:]]
    dict_json["dc"]["dates"] = list(df_france["jour"].values[-n:])
    
    ## Cas
    struct = {"date": "", "values": []}
    dict_json["cas"] = struct
    cas_rolling = df_incid_fra["P"].rolling(window=7, center=False).mean().dropna()
    
    dict_json["cas"]["values"] = [float(round(x, 1)) for x in cas_rolling.values[-n:]]
    dict_json["cas"]["dates"] = list(df_incid_fra.loc[cas_rolling.index.values[-n:], "jour"])
    
    ## Cas date publication
    struct = {"date": "", "values": []}
    dict_json["cas_spf"] = struct
    #cas_rolling = df_vue_ensemble["total_cas_confirmes"].diff().rolling(window=7, center=False).mean().fillna(0)
    cas_rolling = df_opendata_indicateurs["conf_j1"].rolling(window=7, center=False).mean().fillna(0)

    dict_json["cas_spf"]["values"] = [float(round(x, 1)) for x in cas_rolling.values[-n:]]
    dict_json["cas_spf"]["dates"] = list(df_opendata_indicateurs.loc[cas_rolling.index.values[-n:], "date"])
    
    with open(PATH_STATS + 'objectif_deconfinement.json', 'w') as outfile:
        json.dump(dict_json, outfile)
        
objectif_deconfinement()

