"""
Plotly color sequence
https://plotly.com/python/discrete-color/#color-sequences-in-plotly-express

Matplotlib colormap
https://matplotlib.org/stable/gallery/color/colormap_reference.html
"""

import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas as pd
import seaborn as sns
import random

from dash_scripts.dash_style import (SIDEBAR_STYLE, SIDEBAR_HIDDEN,
                                     CONTENT_STYLE_PARTIAL, CONTENT_STYLE_FULL,
                                     DATATABLE_TITLE_STYLE, INPUT_NUMBER_STYLE,
                                     HOME_TEXT, CELL_STYLE,
                                     PAGE_SIZE_SM, PAGE_SIZE_LG)
import dash_scripts.dash_functions as dun
                           
##############################################################################

with open('data/apps.txt') as fileIn:
    apps = dict(line.strip().split(',') for line in fileIn)

reviews = None
palette = None

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'style.css'],
                suppress_callback_exceptions=True)
app.title = 'Dashboard Demo'

navbar = dbc.NavbarSimple(
    children=[dbc.Button('Sidebar', outline=True, color='secondary', className='mr-1', id='btn_sidebar'),],
    brand='Dashboard Demo',
    color='dark',
    dark=True,
    fluid=True,
)

sidebar = html.Div(
    [
        html.P(''),
        html.P('Navigation', className='lead'),
        dbc.Nav(
            [
                dbc.NavLink('Home', href='/', active='exact'),
                dbc.NavLink('Data', href='/data', active='exact'),
                dbc.NavLink('Analysis', href='/analysis', active='exact'),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id='sidebar',
    style=SIDEBAR_STYLE,
)

content = html.Div(
    id='page-content',
    style=CONTENT_STYLE_PARTIAL
)

content_home = html.Div([
    dcc.Markdown(HOME_TEXT),
    html.Ol([html.Li(app_name + ' (ID: ' + app_id + ')') for (app_name, app_id) in apps.items()])
])

def content_data():
    global reviews
    global palette
    
    reviews = pd.read_csv('data/all_reviews_topics.csv', encoding='utf8')
    reviews['index'] = range(1, len(reviews)+1)
    reviews['date'] = reviews['date'].astype(str)
    reviews['version_lvl1'] = reviews['version_lvl1'].astype(str).astype(int)
    reviews = reviews[['index','title','review','username',
                       'app_name','country',
                       'rating','sentiment',
                       'date','day',
                       'version_lvl1','version_lvl2','version_lvl3',
                       'topic_id', 'topic_keywords']]

    palette = sns.color_palette('rainbow', reviews['topic_id'].nunique())
    random.shuffle(palette)

    return html.Div([
        dt.DataTable(
            id='table-reviews',
            columns=[{'name':i, 'id':i} for i in reviews.columns],
            
            page_current=0,
            page_size=PAGE_SIZE_LG,
            page_action='custom',
            
            sort_action='custom',
            sort_mode='multi',
            sort_by=[],
            
            filter_action='custom',
            filter_query='',
            
            style_cell=CELL_STYLE,
            
            # vertical scroll
            style_table={'height':'80vh','overflowY':'scroll'},
            
            # wrap cell
            style_data_conditional=(
                [
                    {
                        'if': {'column_id':'title'},
                            'whiteSpace': 'normal',
                            'height': 'auto'
                    },
                    {
                        'if': {'column_id':'review'},
                            'whiteSpace': 'normal',
                            'height': 'auto'
                    },
                    {
                        'if': {'column_id':'translated_review'},
                            'whiteSpace': 'normal',
                            'height': 'auto'
                    },
                    {
                        'if': {'column_id':'topic_keywords'},
                            'whiteSpace': 'normal',
                            'height': 'auto'
                    },
                ] +
                [
                    {
                        'if': {
                            'column_id':'topic_id',
                            'filter_query':'{{topic_id}}={}'.format(id),
                        },
                        'backgroundColor': 'rgba({},{},{},{})'.format(palette[index][0]*255, palette[index][1]*255, palette[index][2]*255, 0.3),
                    }
                    for index, id in enumerate(reviews['topic_id'].unique())
                ]
            ),
            
            # fixed column width
            style_cell_conditional=[
                {'if': {'column_id': 'index'},
                 'width': '50px'},
                {'if': {'column_id': 'date'},
                 'width': '58px'},
                {'if': {'column_id': 'topic_id'},
                 'width': '50px'},
                {'if': {'column_id': 'rating'},
                 'width': '40px'},
                {'if': {'column_id': 'sentiment'},
                 'width': '57px'},
                {'if': {'column_id': 'version_lvl1'},
                 'width': '66px'},
                {'if': {'column_id': 'version_lvl2'},
                 'width': '66px'},
                {'if': {'column_id': 'version_lvl3'},
                 'width': '66px'},
            ]
        ),
        html.Div(id='data_info'),
    ])

content_analysis = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': app_name, 'value': app_name} for (app_name,_) in apps.items()],
        value=next(iter(apps)),
        clearable=False,
    ),
    html.Br(),
    
    # tabs for various analysis
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(id='tab1', label='Ratings', value='tab-1', children=[
            dcc.Graph(id='bar-rating')
        ]),
        dcc.Tab(id='tab2', label='Sentiment', value='tab-2', children=[
            dcc.Graph(id='bar-sentiment')
        ]),
        dcc.Tab(id='tab3', label='Version', value='tab-3', children=[
            dcc.Graph(id='bar-ver1'),
            dcc.Graph(id='bar-ver2'),
            dcc.Graph(id='bar-ver3')
        ]),
        dcc.Tab(id='tab4', label='Semantic', value='tab-4', children=[
            html.Br(),
            
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Row(
                            dbc.Col(html.Div(html.P('Top Link Words', style=DATATABLE_TITLE_STYLE))),
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div([
                                    dt.DataTable(id='table-linkwords',	
                                        page_current=0,									
                                        page_size=PAGE_SIZE_SM,
                                        page_action='custom',
                                        
                                        sort_action='custom',
                                        sort_mode='multi',
                                        sort_by=[],
                                        
                                        filter_action='custom',
                                        filter_query='',
                                        
                                        # styling
                                        style_cell=CELL_STYLE,
                                        style_table={'height': '55vh', 'overflowY': 'auto'},
                                        
                                        # fixed column width
                                        style_cell_conditional=[
                                            {'if': {'column_id': 'index'},
                                             'width': '50px'},
                                            {'if': {'column_id': 'count'},
                                             'width': '50px'},
                                            {'if': {'column_id': 'rating'},
                                             'width': '60px'},
                                            {'if': {'column_id': 'sentiment'},
                                             'width': '65px'},
                                        ]
                                    ),
                                    html.Div(id='lw1_info'),
                                ])
                            ),
                        ),
                    ]),
                    dbc.Col([
                        dbc.Row(
                            dbc.Col(html.Div(html.P('Top Topics', style=DATATABLE_TITLE_STYLE))),
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div([
                                    dt.DataTable(id='table-topics',		
                                        page_current=0,
                                        page_size=PAGE_SIZE_SM,
                                        page_action='custom',
                                        
                                        sort_action='custom',
                                        sort_mode='multi',
                                        sort_by=[],
                                        
                                        filter_action='custom',
                                        filter_query='',
                                        
                                        # styling
                                        style_cell=CELL_STYLE,
                                        style_table={'height': '55vh', 'overflowY': 'auto'}
                                    ),
                                    html.Div(id='topic_info'),
                                ])
                            ),
                        ),
                    ]),
                ]),
                dbc.Row(
                    dbc.Col([
                        dbc.Row(
                            dbc.Col(html.Div(html.P('Link Words Breakdown', style=DATATABLE_TITLE_STYLE)),),
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div([
                                    dt.DataTable(id='table-lw-all',
                                        page_current=0,
                                        page_size=PAGE_SIZE_LG,
                                        page_action='custom',
                                        
                                        sort_action='custom',
                                        sort_mode='multi',
                                        sort_by=[],
                                        
                                        filter_action='custom',
                                        filter_query='',
                                        
                                        # styling
                                        style_cell=CELL_STYLE,
                                        
                                        # vertical scrolling
                                        style_table={'height': '60vh', 'overflowY': 'auto'},
                                        
                                        # wrap cell
                                        style_data_conditional=[
                                            {'if': {'column_id':'title'},
                                                'whiteSpace': 'normal',
                                                'height': 'auto'},
                                            {'if': {'column_id':'review'},
                                                'whiteSpace': 'normal',
                                                'height': 'auto'},
                                            {'if': {'column_id':'translated_review'},
                                                'whiteSpace': 'normal',
                                                'height': 'auto'},
                                        ],
                                        
                                        # fixed column width
                                        style_cell_conditional=[
                                            {'if': {'column_id': 'index'},
                                             'width': '50px'},
                                            {'if': {'column_id': 'date'},
                                             'width': '58px'},
                                            {'if': {'column_id': 'topic_id'},
                                             'width': '50px'},
                                            {'if': {'column_id': 'rating'},
                                             'width': '40px'},
                                            {'if': {'column_id': 'sentiment'},
                                             'width': '57px'},
                                            {'if': {'column_id': 'version_lvl1'},
                                             'width': '66px'},
                                            {'if': {'column_id': 'version_lvl2'},
                                             'width': '66px'},
                                            {'if': {'column_id': 'version_lvl3'},
                                             'width': '66px'},
                                        ]
                                    ),
                                    html.Div(id='lw2_info'),
                                ])
                            ),
                        ),
                    ])
                )
            ]),
        ]),
    ]),
])


app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id='url'),
        navbar,
        sidebar,
        content,
    ]
)


@app.callback(
    [
        Output('sidebar', 'style'),
        Output('page-content', 'style'),
        Output('side_click', 'data'),
    ],
    [
        Input('btn_sidebar', 'n_clicks'),
        State('side_click', 'data')
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == 'SHOW':
            sidebar_style = SIDEBAR_HIDDEN
            content_style = CONTENT_STYLE_FULL
            cur_nclick = 'HIDDEN'
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE_PARTIAL
            cur_nclick = 'SHOW'
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE_PARTIAL
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page_content(pathname):
    if pathname == '/':
        return content_home
    elif pathname == '/data':
        return content_data()
    elif pathname == '/analysis':
        return content_analysis


@app.callback(
    [
        Output('bar-rating', 'figure'),
        Output('bar-sentiment', 'figure'),
        Output('bar-ver1', 'figure'),
        Output('bar-ver2', 'figure'),
        Output('bar-ver3', 'figure'),
        
        Output('table-linkwords', 'data'),
        Output('table-linkwords', 'columns'),
        Output('lw1_info', 'children'),
        
        Output('table-lw-all', 'data'),
        Output('table-lw-all', 'columns'),
        Output('lw2_info', 'children'),
        
        Output('table-topics', 'data'),
        Output('table-topics', 'columns'),
        Output('topic_info', 'children'),
    ],
    [
        Input('dropdown', 'value'),
        
        Input('table-linkwords', 'filter_query'),
        Input('table-linkwords', 'page_current'),
        Input('table-linkwords', 'sort_by'),
        Input('table-linkwords', 'page_size'),
        
        Input('table-lw-all', 'filter_query'),
        Input('table-lw-all', 'page_current'),
        Input('table-lw-all', 'sort_by'),
        Input('table-lw-all', 'page_size'),
        
        Input('table-topics', 'filter_query'),
        Input('table-topics', 'page_current'),
        Input('table-topics', 'sort_by'),
        Input('table-topics', 'page_size'),
    ]
)
def update_charts(app_name,
                  filter_lw1, page_lw1, sort_lw1, size_lw1,
                  filter_lw2, page_lw2, sort_lw2, size_lw2,
                  filter_topic, page_topic, sort_topic, size_topic,
                  ):
    # filter dataframe for an app
    mask = reviews[reviews['app_name'] == app_name]
    app = app_name.lower()
    
    fig1 = dun.bar_rating(mask)
    fig2 = dun.bar_sentiment(mask)
    fig3 = dun.bar_version(mask, 'version_lvl1', 'Average Rating by App Version Level 1')
    fig4 = dun.bar_version(mask, 'version_lvl2', 'Average Rating by App Version Level 2')
    fig5 = dun.bar_version(mask, 'version_lvl3', 'Average Rating by App Version Level 3')
    
    ################################ SEMANTIC ################################
    
    # link words summary
    lw1 = pd.read_csv('data/linkwords/linkwords_summary_{}.csv'.format(app), encoding='utf8')
    lw1['index'] = range(1, len(lw1) + 1)
    lw1 = lw1[['index','link_words','count','rating','sentiment']]
    col_lw1 = [{'name':i, 'id':i} for i in lw1.columns]
    search_lw1 = dun.search_filter_sm(filter_lw1, lw1)
    search_lw1 = dun.multi_sort(search_lw1, sort_lw1)
    PAGE_LW1 = page_lw1
    SIZE_LW1 = size_lw1
    info_lw1 = dun.table_info(search_lw1, PAGE_LW1, SIZE_LW1)
    
    # link words table
    lw2 = pd.read_csv('data/linkwords/linkwords_{}.csv'.format(app), encoding='utf8')
    lw2['index'] = range(1, len(lw2) + 1)
    lw2 = lw2[['index','title','review','username','app_name',
               'country','rating','sentiment',
               'date','day',
               'version_lvl1','version_lvl2','version_lvl3',
               'link_words']]
    col_lw2 = [{'name':i, 'id':i} for i in lw2.columns]
    search_lw2 = dun.search_filter_lg(filter_lw2, lw2)
    search_lw2 = dun.multi_sort(search_lw2, sort_lw2)
    PAGE_LW2 = page_lw2
    SIZE_LW2 = size_lw2
    info_lw2 = dun.table_info(search_lw2, PAGE_LW2, SIZE_LW2)
    
    # topics table
    topics = pd.read_csv('data/topics/topics_{}.csv'.format(app), encoding='utf8')
    topics = topics.iloc[1:]
    topics['index'] = range(1, len(topics) + 1)
    topics = topics[['index','topic_id','topic_keywords','count']]
    col_topic = [{'name':i, 'id':i} for i in topics.columns]
    search_topic = dun.search_filter_sm(filter_topic, topics)
    search_topic = dun.multi_sort(search_topic, sort_topic)
    PAGE_TOPIC = page_topic
    SIZE_TOPIC = size_topic
    info_topic = dun.table_info(search_topic, PAGE_TOPIC, SIZE_TOPIC)
    
    return fig1, fig2, fig3, fig4, fig5, \
           search_lw1.iloc[PAGE_LW1*SIZE_LW1 : (PAGE_LW1+1)*SIZE_LW1].to_dict('records'), col_lw1, info_lw1, \
           search_lw2.iloc[PAGE_LW2*SIZE_LW2 : (PAGE_LW2+1)*SIZE_LW2].to_dict('records'), col_lw2, info_lw2, \
           search_topic.iloc[PAGE_TOPIC*SIZE_TOPIC : (PAGE_TOPIC+1)*SIZE_TOPIC].to_dict('records'), col_topic, info_topic


@app.callback(
    [
        Output('table-reviews', 'data'),
        Output('data_info', 'children'),
    ],
    [
        Input('table-reviews', 'page_current'),
        Input('table-reviews', 'page_size'),
        Input('table-reviews', 'sort_by'),
        Input('table-reviews', 'filter_query'),
    ]
)
def update_main_table(page_current, page_size, sort_by, filter):
    dff = dun.search_filter_lg(filter, reviews)
    dff = dun.multi_sort(dff, sort_by)

    page = page_current
    size = page_size
    info = dun.table_info(dff, page, size)
    
    return dff.iloc[page*size : (page+1)*size].to_dict('records'), info


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)