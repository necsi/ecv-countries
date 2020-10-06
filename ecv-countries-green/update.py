#!/usr/bin/env python
# coding: utf-8

# In[149]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


# In[150]:


df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
focus = df.copy().drop(['Lat','Long'], axis=1).set_index(['Country/Region','Province/State'])
confirm = focus.groupby('Country/Region').sum().reset_index()


# In[205]:


date = pd.to_datetime("today").strftime('%B %d')
print('Latest update time is:',date)


# In[151]:


do_not_include = ['Antigua and Barbuda', 'Angola', 'Benin', 'Botswana', 
                  'Burundi', 'Cabo Verde', 'Chad', 'Comoros', 
                  'Congo (Brazzaville)', 'Congo (Kinshasa)',"Cote d'Ivoire", 'Central African Republic',
                  'Diamond Princess', 'Equatorial Guinea',
                  'Eritrea', 'Eswatini',   'Gabon', 'Kosovo',
                  'Gambia', 'Grenada', 'Guinea', 'Guinea-Bissau',
                  'Guyana', 'Lesotho', 'Liberia', 'Libya', 'Madagascar',
                  'Malawi', 'Maldives', 'Mauritania', 'Mozambique',
                  'MS Zaandam', 'Namibia', 'Nicaragua', 'Papua New Guinea',
                   'Saint Lucia', 
                  'Saint Vincent and the Grenadines', 'Sao Tome and Principe',
                  'Seychelles', 'Sierra Leone', 'South Sudan', 'Suriname', 'Syria', 
                  'Tanzania',   'Togo', 'West Bank and Gaza',
                  'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe']


# In[152]:


focus


# In[153]:


## replacing 0 total cases with nan
#confirm.replace(0, np.nan, inplace=True)


# In[154]:


confirm


# In[155]:


# convert "pivoted" data to "long form"
data = pd.melt(confirm, id_vars=['Country/Region'], var_name='date', value_name='cases')

data = data.rename(columns = {'Country/Region':'country'})

# convert date column
data['date'] = pd.to_datetime(data['date'], format= '%m/%d/%y')


# In[156]:


data


# In[157]:


# pivot data with countries as columns
cases = pd.pivot_table(data, index = "date", columns = "country", values= "cases")

# drop countries listed above
cases = cases.drop(columns=do_not_include)


# In[158]:


cases


# In[159]:


# new dataframe to store "daily new cases"
newcases = cases.copy()

# calculate "daily new cases"
for column in newcases.columns[0:]:
    DailyNewCases = column
    newcases[DailyNewCases] = newcases[column].diff()


# In[160]:


# fill NaN in pivot_newcases (first row) with values from pivot_cases
newcases.fillna(cases, inplace=True)


# In[161]:


newcases


# In[162]:


# replace negative daily values by setting 0 as the lowest
newcases = newcases.clip(lower=0)


# In[163]:


# new dataframe to store "avg new cases"
avgnewcases = newcases.copy()

# calculate 7-day averages of new cases
for column in avgnewcases.columns[0:]:
    DaySeven = column
    avgnewcases[DaySeven] = avgnewcases[column].rolling(window=7, center=False).mean()


# In[164]:


# fill NaN in pivot_avgnewcases (first 6 rows) with values from pivot_newcases
recentnew = avgnewcases.fillna(newcases)


# In[165]:


recentnew


# In[166]:


# new dataframe to store "avg new cases" with centered average
avgnewcases_center = newcases.copy()

# calculate 7-day averages of new cases with centered average
for column in avgnewcases_center.columns[0:]:
    DaySeven = column
    avgnewcases_center[DaySeven] = avgnewcases_center[column].rolling(window=7, min_periods=4, center=True).mean()


# In[167]:


avgnewcases_center


# In[168]:


## new dataframe to store "avg new cases" with centered average
#pivot_recentnew_peaktodate = pivot_recentnew.copy()

## calculate 7-day averages of new cases with centered average
#for column in pivot_recentnew_peaktodate.columns[0:]:
#    DaySeven = column
#    pivot_recentnew_peaktodate[DaySeven] = pivot_recentnew_peaktodate[column].cummax()


# In[169]:


#pivot_recentnew_peaktodate


# In[170]:


# new dataframe to store peak 7-day average to date 
recentnew_peaktodate = recentnew.cummax()


# In[171]:


recentnew_peaktodate


# In[172]:


# reset indexes of "pivoted" data
cases = cases.reset_index()
newcases = newcases.reset_index()
recentnew = recentnew.reset_index()
avgnewcases_center = avgnewcases_center.reset_index()
recentnew_peaktodate = recentnew_peaktodate.reset_index()


# In[173]:


# convert "pivot" of total cases to "long form"
country_cases = pd.melt(cases, id_vars=['date'], var_name='country', value_name='cases')


# In[174]:


cases


# In[175]:


# convert "pivot" of daily new cases to "long form"
country_newcases = pd.melt(newcases, id_vars=['date'], var_name='country', value_name='new_cases')


# In[176]:


country_newcases


# In[177]:


# convert "pivot" of recent new cases to "long form" (7-day avg w first 6 days from "new cases")
country_recentnew = pd.melt(recentnew, id_vars=['date'], var_name='country', value_name='recent_new')


# In[178]:


country_recentnew


# In[179]:


# convert "pivot" of centered average new cases to "long form"
country_avgnewcases_center = pd.melt(avgnewcases_center, id_vars=['date'], var_name='country', value_name='avg_cases')


# In[180]:


country_avgnewcases_center


# In[181]:


# convert "pivot" of centered average new cases to "long form"
country_recentnew_peaktodate = pd.melt(recentnew_peaktodate, id_vars=['date'], var_name='country', value_name='peak_recent_new')


# In[182]:


country_recentnew_peaktodate


# In[183]:


# merge the 5 "long form" dataframes based on index
country_merge = pd.concat([country_cases, country_newcases, country_avgnewcases_center, country_recentnew, country_recentnew_peaktodate], axis=1)


# In[184]:


# NOTE:
# original code uses integer from latest 7-day average in country color logic

# take integer from "recent_new"
country_merge['recent_new_int'] = country_merge['recent_new'].astype(int)


# In[185]:


# remove duplicate columns
country_merge = country_merge.loc[:,~country_merge.columns.duplicated()]


# In[186]:


country_merge


# In[187]:


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


# In[188]:


country_merge


# In[189]:


# dataframe with only the most recent date for each country
# https://stackoverflow.com/questions/23767883/pandas-create-new-dataframe-choosing-max-value-from-multiple-observations
country_latest = country_merge.loc[country_merge.groupby('country').date.idxmax().values]


# In[190]:


country_latest


# In[191]:


# dataframe with just country, total cases, and color
country_total_color = country_latest[['country','cases','color_historical']]

# rename cases to total_cases and color_historical to color for the purpose of merging
country_total_color = country_total_color.rename(columns = {'cases':'total_cases', 'color_historical':'color'})


# In[192]:


country_total_color


# In[193]:


# merging total cases onto the merged dataframe
country_final = country_merge.merge(country_total_color, on='country', how='left')


# In[194]:


## drop rows where cumulative cases is NaN (dates before reported cases)
#country_final = country_final.dropna(subset=['cases']) 


# In[195]:


country_final


# In[196]:


#correcting country names
countryrename = {'Taiwan*' : 'Taiwan',
                 'Korea, South' : 'South Korea',
                 'United Arab Emirates' : 'U.A.E.',
                 'Bosnia and Herzegovina' : 'Bosnia'}

country_final['country'] = country_final['country'].replace(countryrename)


# In[197]:


## Remove the 'cases' column to match format of Era's state result file 
result = country_final[['country','date','new_cases','avg_cases','total_cases','recent_new','color']]

result.to_csv(r'C:\Users\Administrator\Desktop\country_plots_green\result.csv' , index=False)

result.to_csv(r'C:\Users\Administrator\Desktop\country_plots_orange\result.csv' , index=False)

result.to_csv(r'C:\Users\Administrator\Desktop\country_plots_red\result.csv' , index=False)


# In[198]:


# dataframe with just country and color
country_color = country_total_color[['country','color']]

# creates csv similar to USStateColors.csv
#country_color.to_csv('CountryColors.csv', index=False)


# In[199]:


# count number of countries by color by date
color_by_date = pd.crosstab(index = country_final['date'], columns=country_final['color_historical'])


# In[200]:



# In[201]:





# In[204]:


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

#fig.show()


# In[83]:


#fig.write_html("countries.html",config=dict(
#              displayModeBar=False), default_height = '550px', default_width = '900px' )

#fig.write_html(r'C:\Users\Administrator\Desktop\country_colors\countries.html',config=dict(
#               displayModeBar=False), default_height = '550px', default_width = '900px' )
fig.write_html(r'ecv-countries-green/index.html',config=dict(
               displayModeBar=False), default_height = '550px', default_width = '900px' )


print('Compiled Successfully!')





