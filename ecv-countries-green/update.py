#!/usr/bin/env python
# coding: utf-8

# In[1]:
#

# Includes correction for Kosovo with European CDC numbers
# New Zealand & Thailand updated to only include cases from local transmission


# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import csv
import json
import requests
import datetime
import urllib

import re
import requests
from io import StringIO
import matplotlib.dates as mdates
import time

import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


# In[3]:


df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
focus = df.copy().drop(['Lat','Long'], axis=1).set_index(['Country/Region','Province/State'])
confirm = focus.groupby('Country/Region').sum().reset_index()


# In[4]:


do_not_include = ['Antigua and Barbuda', 'Angola', 'Benin', 'Botswana', 
                  'Burundi', 'Cabo Verde', 'Chad', 'Comoros', 
                  'Congo (Brazzaville)', 'Congo (Kinshasa)',"Cote d'Ivoire", 'Central African Republic',
                  'Diamond Princess', 'Equatorial Guinea',
                  'Eritrea', 'Eswatini',   'Gabon', 
                  'Gambia', 'Ghana', 'Grenada', 'Guinea', 'Guinea-Bissau',
                  'Guyana', 'Lesotho', 'Liberia', 'Libya', 'Madagascar',
                  'Malawi', 'Maldives', 'Mauritania', 'Mozambique',
                  'MS Zaandam', 'Namibia', 'Nicaragua', 'Papua New Guinea',
                  'Rwanda',   'Saint Lucia', 
                  'Saint Vincent and the Grenadines', 'Sao Tome and Principe',
                  'Seychelles', 'Sierra Leone', 'South Sudan', 'Sudan', 'Suriname', 'Syria', 
                  'Tanzania', 'Tajikistan', 'Togo', 'Uganda', 'West Bank and Gaza',
                  'Yemen', 'Zambia', 'Zimbabwe']


# In[5]:


focus


# In[6]:


## replacing 0 total cases with nan
#confirm.replace(0, np.nan, inplace=True)


# In[7]:


confirm


# In[8]:


# convert "pivoted" data to "long form"
data = pd.melt(confirm, id_vars=['Country/Region'], var_name='date', value_name='cases')

data = data.rename(columns = {'Country/Region':'country'})

# convert date column
data['date'] = pd.to_datetime(data['date'], format= '%m/%d/%y')


# In[9]:


data


# In[10]:


# pivot data with countries as columns
pivot_cases = pd.pivot_table(data, index = "date", columns = "country", values= "cases")

# drop countries listed above
pivot_cases = pivot_cases.drop(columns=do_not_include)


# In[11]:


pivot_cases


# # Kosovo correction - ERROR since 12/18/2020, now file has only weekly data, commenting out..

# In[12]:


## Kosovo correction using European CDC data

# read in data
#eurocdc = pd.read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv")

# add date column from year, month & day columns
#eurocdc['date'] = pd.to_datetime(eurocdc[["year", "month", "day"]])


# In[13]:


# filter for Kosovo
#kosovo = eurocdc[eurocdc['countriesAndTerritories'] == 'Kosovo']


# In[14]:


#kosovo


# In[15]:


# only include date & cases columns ('cases' indicates daily new cases)
#kosovo = kosovo[['date', 'cases']]

# sort by date and set date as index
#kosovo = kosovo.sort_values('date').set_index('date')

# create new column 'Kosovo' with cumulative cases for the purpose of updating Kosovo column in pivot_cases
#kosovo['Kosovo'] = kosovo['cases'].cumsum()

# only include 'Kosovo' column
#kosovo = kosovo[['Kosovo']]


# In[16]:


#kosovo


# In[17]:


# update JHU values for Kosovo with European CDC values
# https://stackoverflow.com/questions/24768657/replace-column-values-based-on-another-dataframe-python-pandas-better-way
#pivot_cases.update(kosovo)


# In[18]:


#pivot_cases


# In[19]:


# check to see if cases were properly updated for each date
#pivot_cases['Kosovo']


# # New Zealand correction (only local transmission)

# In[20]:


# New Zealand data
t = requests.get('https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-data-and-statistics/covid-19-case-demographics').text
filename = re.findall('system(.+?)\.csv', t)
url = 'https://www.health.govt.nz/system'+filename[0]+'.csv'
urlData = requests.get(url).content
s=str(urlData,'utf-8')
data = StringIO(s)
df_nz=pd.read_csv(data)
df_nz['new']=1
df_nz = df_nz[df_nz['Overseas travel'] != 'Yes']
tod = pd.to_datetime('today')
idx = pd.date_range('02-26-2020', tod)
focus_nz = df_nz.groupby(['Report Date']).sum()
focus_nz.index = pd.to_datetime(focus_nz.index, dayfirst=True)
new_nz = focus_nz.reindex(idx, fill_value=0)


# In[21]:


# create new column 'New Zealand' with cumulative cases for the purpose of updating New Zealand column in pivot_cases
new_nz['New Zealand'] = new_nz['new'].cumsum()

# only include 'New Zealand' column
new_nz = new_nz[['New Zealand']]

pivot_cases.update(new_nz)


# In[22]:


# Check New Zealand update
pivot_cases['New Zealand']


# # Thailand correction (only local transmission)

# In[23]:


# Thailand data
url_s = 'https://data.go.th/dataset/covid-19-daily'
t = requests.get(url_s).text
filenames = re.findall('https:(.+?)\.csv', t)
url = 'https:' + filenames[0] + '.csv'
df_t = pd.read_csv(url)

## fix bad year from dates 2563-11-21 and 1963-10-17 to 2020
#df_t['announce_date'] = df_t['announce_date'].astype(str).replace({'[0-9][0-9][0-9][0-9]':'2020'},regex=True)
#df_t['announce_date'] = df_t['announce_date'].astype(str).replace({'15/15':'15/12'},regex=True)
df_t['announce_date'] = df_t['announce_date'].astype(str).replace({'2564':'2021'},regex=True)
df_t['announce_date'] = df_t['announce_date'].astype(str).replace({'2563':'2020'},regex=True)
df_t = df_t.set_index([df_t.columns[6]])
df_t.index.name = None

# The nationality column is not important
#df_t = df_t[df_t[df_t.columns[3]]=='Thailand']

df_t['new'] = 1
#df_t.loc[pd.isna(df_t[df_t.columns[8]]),'new'] = 1

df_t.loc[df_t[df_t.columns[8]]=='ผู้ที่เดินทางมาจากต่างประเทศ และเข้า OQ','new'] = 0
df_t.loc[df_t[df_t.columns[8]]=='ผู้ที่เดินทางมาจากต่างประเทศ และเข้า ASQ/ALQ','new'] = 0
df_t.loc[df_t[df_t.columns[8]]=='State Quarantine','new'] = 0
df_t.loc[df_t[df_t.columns[8]]=='คนต่างชาติเดินทางมาจากต่างประเทศ','new'] = 0


tod = pd.to_datetime('today')
idx = pd.date_range('01-22-2020', tod)
df_t = df_t.groupby(df_t.index).sum()
df_t.index = pd.to_datetime(df_t.index, dayfirst=True)
df_t = df_t[1:-1]
new_thailand = df_t.reindex(idx, fill_value=0)

# Oct 13 fix: 
# add in 3 cases of local transmission missing from our filter because "nationality" is Myanmar/Burma rather than "Thailand"
#man1 = pd.to_datetime('2020-10-13')
#new_thailand.loc[man1,'new'] = 3

# In[24]:


# create new column 'Thailand' with cumulative cases for the purpose of updating Thailand column in pivot_cases
new_thailand['Thailand'] = new_thailand['new'].cumsum()

# only include 'Thailand' column
new_thailand = new_thailand[['Thailand']]

pivot_cases.update(new_thailand)


# In[25]:


# Check Thailand update
pivot_cases['Thailand']


### Australia correction (only local transmission)


with urllib.request.urlopen('https://atlas.jifo.co/api/connectors/ba66fc4e-9f3a-43f7-bd7c-190a6f89f183') as url:
    data = json.loads(url.read().decode())
result = pd.DataFrame(data)

## Update to fix year for 2021:
## Idea to was to use date (day/month) from first row of each state w 2020 as year, then increment subsequent rows by 1 day
## Based on:
##    Rolling date: https://stackoverflow.com/questions/59864206/pandas-increment-rolling-date
##    Create date from y,m,d: https://stackoverflow.com/questions/58072683/combine-year-month-and-day-in-python-to-create-a-date
## Within for loop, parse day & month to new columns; change those columns to integers
## Set start_day & start_month based on date from each state's 1st row
## Create 'start_date' from start_day & start_month, using 2020 as year
## maxsize: Use len function to find number of rows in 'focus' (each state)
## Create a 'date' column using pd.date_range to fill rows with dates from start_date for maxsize number of periods 


# empty dataframe with columns to append state data
oz_states = pd.DataFrame(columns = ['Overseas','Known Local','Unknown Local (Community)','Interstate travel','Under investigation','state'])

ab = 0
for d in data['sheetNames']:
    df = result[result['sheetNames']==d]
    focus = pd.DataFrame(df['data'][ab],columns=df['data'][ab][0])
    ab = ab + 1
    focus = focus.iloc[1:].set_index('')
    focus.index.name = None
    #focus = focus.rename({focus.columns(0): 'Overseas', focus.columns(1): 'Known Local', focus.columns(2): 'Unknown Local (Community)', focus.columns(3): 'Interstate travel', focus.columns(4): 'Under investigation'}, axis=1)
    focus.columns = ['Overseas','Known Local','Unknown Local (Community)','Interstate travel','Under investigation']
    focus.replace('', 0, inplace=True)
    focus = focus.astype(float)
    focus['state'] = d
    ## reset index & parse day/month to new columns
    focus = focus.reset_index()
    focus['day'], focus['month'] = focus['index'].str.split('/', 1).str
    focus[['day', 'month']] = focus[['day', 'month']].astype(int)
    start_day = focus['day'].head(1)
    start_month = focus['month'].head(1)
    ## Create date from y,m,d: https://stackoverflow.com/questions/58072683/combine-year-month-and-day-in-python-to-create-a-date
    start_date = datetime.datetime(2020, start_month, start_day)
    ## Rolling date: https://stackoverflow.com/questions/59864206/pandas-increment-rolling-date
    maxsize = len(focus)
    focus['date'] = pd.date_range(pd.to_datetime(start_date),periods=maxsize)
    oz_states = oz_states.append(focus)

# drop extra columns
oz_states.drop(columns = ['index', 'day', 'month'], inplace = True)

# group by date for Australia-wide cases
oz_total = oz_states.groupby('date').sum()


# all cases
oz_total['all_cases'] = oz_total.sum(axis=1)

# all cases not imported from overseas
oz_total['no_overseas'] = oz_total['all_cases'] - oz_total['Overseas']

## local cases excluding cases from interstate travel
#oz_total['local_no_interstate'] = oz_total['no_overseas']-oz_total['Interstate travel']

## only local cases with unknown origin or those under investigation (i.e. excluding known local cases)
#oz_total['unknown_ui'] = oz_total['local_no_interstate']-oz_total['Known Local']


# cumulative sum of non-overseas cases
oz_total['Australia'] = oz_total['no_overseas'].cumsum()

new_oz = oz_total['Australia']

pivot_cases.update(new_oz)

# Check Australia update
pivot_cases['Australia']


# ## End of countries corrections

# In[26]:


# new dataframe to store "daily new cases"
pivot_newcases = pivot_cases.copy()

# calculate "daily new cases"
for column in pivot_newcases.columns[0:]:
    DailyNewCases = column
    pivot_newcases[DailyNewCases] = pivot_newcases[column].diff()


# In[27]:


# fill NaN in pivot_newcases (first row) with values from pivot_cases
pivot_newcases.fillna(pivot_cases, inplace=True)


# In[28]:


pivot_newcases


# In[29]:


# replace negative daily values by setting 0 as the lowest value
pivot_newcases = pivot_newcases.clip(lower=0)


# In[30]:


# new dataframe to store "avg new cases"
pivot_avgnewcases = pivot_newcases.copy()

# calculate 7-day averages of new cases
for column in pivot_avgnewcases.columns[0:]:
    DaySeven = column
    pivot_avgnewcases[DaySeven] = pivot_avgnewcases[column].rolling(window=7, center=False).mean()


# In[31]:


# fill NaN in pivot_avgnewcases (first 6 rows) with values from pivot_newcases
pivot_recentnew = pivot_avgnewcases.fillna(pivot_newcases)


# In[32]:


pivot_recentnew


# In[33]:


# new dataframe to store "avg new cases" with centered average
pivot_avgnewcases_center = pivot_newcases.copy()

# calculate 7-day averages of new cases with centered average
for column in pivot_avgnewcases_center.columns[0:]:
    DaySeven = column
    pivot_avgnewcases_center[DaySeven] = pivot_avgnewcases_center[column].rolling(window=7, min_periods=4, center=True).mean()


# In[34]:


pivot_avgnewcases_center


# In[35]:


## new dataframe to store "avg new cases" with centered average
#pivot_recentnew_peaktodate = pivot_recentnew.copy()

## calculate 7-day averages of new cases with centered average
#for column in pivot_recentnew_peaktodate.columns[0:]:
#    DaySeven = column
#    pivot_recentnew_peaktodate[DaySeven] = pivot_recentnew_peaktodate[column].cummax()


# In[36]:


#pivot_recentnew_peaktodate


# In[37]:


# new dataframe to store peak 7-day average to date 
pivot_recentnew_peaktodate = pivot_recentnew.cummax()


# In[38]:


pivot_recentnew_peaktodate


# In[39]:


# reset indexes of "pivoted" data
pivot_cases = pivot_cases.reset_index()
pivot_newcases = pivot_newcases.reset_index()
pivot_recentnew = pivot_recentnew.reset_index()
pivot_avgnewcases_center = pivot_avgnewcases_center.reset_index()
pivot_recentnew_peaktodate = pivot_recentnew_peaktodate.reset_index()


# In[40]:


# convert "pivot" of total cases to "long form"
country_cases = pd.melt(pivot_cases, id_vars=['date'], var_name='country', value_name='cases')


# In[41]:


country_cases


# In[42]:


# convert "pivot" of daily new cases to "long form"
country_newcases = pd.melt(pivot_newcases, id_vars=['date'], var_name='country', value_name='new_cases')


# In[43]:


country_newcases


# In[44]:


# convert "pivot" of recent new cases to "long form" (7-day avg w first 6 days from "new cases")
country_recentnew = pd.melt(pivot_recentnew, id_vars=['date'], var_name='country', value_name='recent_new')


# In[45]:


country_recentnew


# In[46]:


# convert "pivot" of centered average new cases to "long form"
country_avgnewcases_center = pd.melt(pivot_avgnewcases_center, id_vars=['date'], var_name='country', value_name='avg_cases')


# In[47]:


country_avgnewcases_center


# In[48]:


# convert "pivot" of centered average new cases to "long form"
country_recentnew_peaktodate = pd.melt(pivot_recentnew_peaktodate, id_vars=['date'], var_name='country', value_name='peak_recent_new')


# In[49]:


country_recentnew_peaktodate


# In[50]:


# merge the 5 "long form" dataframes based on index
country_merge = pd.concat([country_cases, country_newcases, country_avgnewcases_center, country_recentnew, country_recentnew_peaktodate], axis=1)


# In[51]:


# NOTE:
# original code uses integer from latest 7-day average in country color logic

# take integer from "recent_new"
country_merge['recent_new_int'] = country_merge['recent_new'].astype(int)


# In[52]:


# remove duplicate columns
country_merge = country_merge.loc[:,~country_merge.columns.duplicated()]


# In[53]:


country_merge


# In[54]:


## UPDATE 9/25/20 - modified green logic due to quirk caused by original logic on countries page
## original logic caused Uruguay with avg ~16 cases to appear red because 16 > 50% of its low peak of 24

## Orignial green logic:
## if state_color_test['recent_new_int'] <= n_0*f_0 or state_color_test['recent_new_int'] <= n_0 and state_color_test['recent_new_int'] <= f_0*state_color_test['peak_recent_new']:

#choosing colors
n_0 = 20
f_0 = 0.5
f_1 = 0.2

# https://stackoverflow.com/questions/49586471/add-new-column-to-python-pandas-dataframe-based-on-multiple-conditions/49586787
def conditions(country_merge):
    if country_merge['recent_new_int'] <= n_0:
        return 'green'
    elif country_merge['recent_new_int'] <= 1.5*n_0 and country_merge['recent_new_int'] <= f_0*country_merge['peak_recent_new'] or country_merge['recent_new_int'] <= country_merge['peak_recent_new']*f_1:
        return 'orange'
    else:
        return 'red'

country_merge['color_historical'] = country_merge.apply(conditions, axis=1)


# In[55]:


country_merge


# In[56]:


# dataframe with only the most recent date for each country
# https://stackoverflow.com/questions/23767883/pandas-create-new-dataframe-choosing-max-value-from-multiple-observations
country_latest = country_merge.loc[country_merge.groupby('country').date.idxmax().values]


# In[57]:


country_latest


# In[58]:


# dataframe with just country, total cases, and color
country_total_color = country_latest[['country','cases','color_historical']]

# rename cases to total_cases and color_historical to color for the purpose of merging
country_total_color = country_total_color.rename(columns = {'cases':'total_cases', 'color_historical':'color'})


# In[59]:


country_total_color


# In[60]:


# merging total cases onto the merged dataframe
country_final = country_merge.merge(country_total_color, on='country', how='left')


# In[61]:


## drop rows where cumulative cases is NaN (dates before reported cases)
#country_final = country_final.dropna(subset=['cases']) 


# In[62]:


country_final


# # Add country population

# In[63]:


# csv with population for each country/province in JHU global cases dataset
#jhu_pop = pd.read_csv('JHU_country_province_population.csv')


# In[64]:


# group by country
#country_pop = jhu_pop.groupby('Country/Region').sum().reset_index()
#country_pop = country_pop.rename(columns = {'Country/Region':'country'})


# In[65]:


# merge population onto final dataframe
#country_final = country_final.merge(country_pop, on='country', how='left')


# In[66]:


#country_final


# ## End of country population merge

# In[67]:


#correcting country names
countryrename = {'Taiwan*' : 'Taiwan',
                 'Korea, South' : 'South Korea',
                 'United Arab Emirates' : 'U.A.E.',
                 'Bosnia and Herzegovina' : 'Bosnia'}

country_final['country'] = country_final['country'].replace(countryrename)

#adding 1 day to reflect latest data

country_final['date'] = country_final['date'] + datetime.timedelta(days=1)

# In[68]:


## Remove the 'cases' column to match format of Era's state result file 
result = country_final[['country','date','new_cases','avg_cases','total_cases','recent_new','color']]

result.to_csv(r'ecv-countries-green/result.csv', index=False)

result.to_csv(r'ecv-countries-orange/result.csv', index=False)

result.to_csv(r'ecv-countries-red/result.csv', index=False)


# In[69]:


# dataframe with just country and color
country_color = country_total_color[['country','color']]

# creates csv similar to USStateColors.csv
#country_color.to_csv('CountryColors.csv', index=False)


# In[70]:


# count number of countries by color by date
color_by_date = pd.crosstab(index = country_final['date'], columns=country_final['color_historical'])


# In[71]:


color_by_date


# In[72]:


#color_by_date.to_csv('color_by_date.csv')


# # Plotly chart for number of countries by color

# In[73]:


green = go.Scatter(
    x=color_by_date.index,
    y=color_by_date.green, name = 'Winning', marker_color = px.colors.qualitative.D3[2], line = dict(width=4), 
)
orange = go.Scatter(
    x=color_by_date.index,
    y=color_by_date.orange, name = 'Nearly There', marker_color = px.colors.qualitative.G10[2],line = dict(width=4)
)
red = go.Scatter(
    x=color_by_date.index,
    y=color_by_date.red, name = 'Needs Action', marker_color = px.colors.qualitative.G10[1],line = dict(width=4)
)

data = [green, orange, red]
layout = dict(template="simple_white",xaxis = dict(showgrid=False, ticks='outside', mirror=True,showline=True, tickformat = '%d-%b'),
                yaxis = dict(showgrid=False, ticks='outside', mirror = True, showline = True, title = 'Number of Countries'),
                font=dict(size=18),showlegend = True, legend=dict(x=0.77, y=1,traceorder='normal'))
fig = go.Figure(data=data, layout=layout)


# In[74]:


fig.write_html(r'countries.html',config=dict(
               displayModeBar=False), default_height = '550px', default_width = '900px' )


# # Population of countries by color

# In[75]:


# pivot data with countries as columns
#pop_by_color = pd.pivot_table(country_final, index = "date", columns = "color_historical", values= "Population", aggfunc='sum')

# rename color columns
#pop_by_color = pop_by_color.rename(columns = {'green':'pop_green', 'orange':'pop_orange', 'red':'pop_red'})


# In[76]:


#pop_by_color


# In[77]:


# dataframe with count of countries by color by and population of countries by color by date
#color_by_date_pop = pd.concat([color_by_date, pop_by_color], axis=1, sort=False)


# In[78]:


#color_by_date_pop


# In[79]:


# create csv
#color_by_date_pop.to_csv('color_by_date_pop.csv')


# In[80]:


print('Compiled Successfully!')

