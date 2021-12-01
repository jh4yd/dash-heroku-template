import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


external_stylesheets = [dbc.themes.CYBORG]

## download GSS data
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

## Generate the individual tables and figures

### Markdown text

markdown_text = '''
The [The Gneral Socail Survey](http://www.gss.norc.org/) (GSS) is a nationally representative survey of adults in the United States conducted since 1972. The GSS collects data on contemporary American society in order to monitor and explain trends in opinions, attitudes and behaviors. The GSS has adapted questions from earlier surveys, thereby allowing researchers to conduct comparisons for up to 80 years. The GSS contains a standard core of demographic, behavioral, and attitudinal questions, plus topics of special interest. Among the topics covered are civil liberties, crime and violence, intergroup tolerance, morality, national spending priorities, psychological well-being, social mobility, and stress and traumatic events.

The gender pay gap in the United States is the ratio of female-to-male median or average (depending on the source) yearly earnings among full-time, year-round workers. according to the US census bureau, women's median yearly earnings relative to men's rose rapidly from 1980 to 1990 (from 60.2% to 71.6%), and less rapidly from 1990 to 2000 (from 71.6% to 73.7%), from 2000 to 2009 (from 73.7% to 77.0%),and from 2009 to 2018 (from 77.0% to 81.1%). Since 2018 however, no progress has been made since. (https://en.wikipedia.org/wiki/Gender_pay_gap_in_the_United_States)

Here we used GSS data to represent the difference, and to understand the features and the values the nature of the difference. 

'''

### Table

gss_table = gss_clean.groupby('sex').agg({'income':'mean', 
                                          'job_prestige':'mean', 
                                          'socioeconomic_index' : 'mean',
                                          'education': 'mean'}).reset_index()
gss_table = round(gss_table, 2)

table = ff.create_table(gss_table)
#table.show()

### Barplot
bread_df = gss_clean.groupby(by=['sex', 'male_breadwinner']).agg({'id': 'size'}).reset_index()
bread_df = bread_df.rename({'id': 'count'}, axis=1)

fig_bar = px.bar(bread_df, x='male_breadwinner', y='count', color='sex', 
            labels={'male_breadwinner':'level of agreement', 'id':'number of count'},
            text='count', width=800, height=500,
            barmode = 'group'
            )
fig_bar.update(layout=dict(title=dict(x=0.5)))
fig_bar.update_layout(showlegend=False)

#fig_bar.show()

### scatterplot
prestige_df = gss_clean.loc[:,['job_prestige','income','sex','education', 'socioeconomic_index']]
fig_scatter = px.scatter(prestige_df, x='job_prestige', y='income', color='sex', 
                 height=500, width=800,
                 trendline='ols',
                 hover_data=['education', 'socioeconomic_index']
                )
#fig_scatter.show()

### Boxplots
fig_box = px.box(prestige_df, x='sex', y = 'income', labels={'sex':''}, color= 'sex', height=500, width=500)
fig_box2 = px.box(prestige_df, x='sex', y = 'job_prestige', labels={'sex':''}, color= 'sex', height=500, width=500)
fig_box.update_layout(showlegend = False)
fig_box2.update_layout(showlegend = False)
#fig_box.show()
#fig_box2.show()

###facet plot
prestige_df['job_pre_cat'] = pd.cut(prestige_df.job_prestige, 6)
prestige_df = prestige_df.dropna()
fig_group = px.box(prestige_df, x='sex', y = 'income', color='sex', 
             facet_col='job_pre_cat', facet_col_wrap= 2,
             labels={'sex':''},
             color_discrete_map = {'male':'blue', 'female':'red'},
             height=1000, width=1000  )
#fig_group.show()

### Create app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    [
        html.H1("Exploring Gender Pay Gap in the US"),
        
        dcc.Markdown(children = markdown_text),
        
        html.H3("Table of mean income, occupational prestige, socioeconomic index, and years of education for men and for women"),
        
        dcc.Graph(figure=table),
        
        html.H3('The number of men and women who respond with each level of agreement to "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."'),
        
        dcc.Graph(figure=fig_bar),

        html.H3("Scatterplot with 'job_prestige' and 'income' between men and women"),
        
        dcc.Graph(figure=fig_scatter),

        html.Div([
            
            html.H3("Income distributions between women and men"),
            
            dcc.Graph(figure=fig_box)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H3("Job prestige score distributions between women and men"),
            
            dcc.Graph(figure=fig_box2)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H3("Income distribution of women and men within six categories of equally sized range of job prestige scores"),
        
        dcc.Graph(figure=fig_group),

        html.Div([
        html.H5("x-axis feature"),
        dcc.Dropdown(
        id='my-dropdown1',
        options=[
            {'label': 'satjob', 'value': 'satjob'},
            {'label': 'relationship', 'value': 'relationship'},
            {'label': 'male_breadwinner', 'value': 'male_breadwinner'},
            {'label': 'men_bettersuited', 'value': 'men_bettersuited'},
            {'label': 'child_suffer', 'value': 'child_suffer'},
            {'label': 'men_overwork', 'value': 'men_overwork'}
            ],
            value='satjob'
        ),
        html.H5("groupping feature"),
        dcc.Dropdown(
        id='my-dropdown2',
            options=[
                {'label': 'sex', 'value': 'sex'},
                {'label': 'region', 'value': 'region'},
                {'label': 'education', 'value': 'education'}
            ],
            value='sex'
        ),

        html.H4("Interactive Barplot"),
        dcc.Graph(id='my-graph')], style={"width": "50%"},
        )
    ],
)

@app.callback(Output('my-graph', 'figure'),
             [Input('my-dropdown1', 'value'), Input('my-dropdown2','value')])
def update_graph(my_dropdown1_value, my_dropdown2_value):
    my_df = gss_clean.groupby([my_dropdown2_value,my_dropdown1_value]).agg({'id': 'size'}).reset_index()
    my_df = my_df.rename({'id': 'count'}, axis=1)

    fig_bar = px.bar(my_df, x=my_dropdown1_value, y='count', color=my_dropdown2_value,
            labels={my_dropdown1_value:'level of agreement', 'count':'number of count'},
            title = 'Interactive Barplot', width=900, height=600,
            barmode = 'group'
            )
    fig_bar.update(layout=dict(title=dict(x=0.5)))
    fig_bar.update_layout(showlegend=True)

    return fig_bar

if __name__ == '__main__':
    app.run_server(debug=True, port=8051, host='0.0.0.0')
