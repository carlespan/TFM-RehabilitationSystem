# Añadir ejercicio

from pymongo import MongoClient
import certifi

from dash import html, dcc, register_page, callback
from dash.dependencies import Output, Input, State
import pandas as pd

import datetime



register_page(__name__,path='/add-exercise')



# ----------------------------------- Conectarse a la DB con pymongo ------------------------------------------

username = 'carlos'
password = '4994xIWET66oFGOu'
#username = 'medico'
#password = 'IS6uafvwyP6cBRcu'
MONGODB_URI = "mongodb+srv://"+username+":"+password+"@cluster0.avyshq1.mongodb.net/?retryWrites=true&w=majority"
clientAdmin = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = clientAdmin["Rehabilitación"]

ejercicios = db['ejercicios']

nombre = ""
apellidos = ""



layout = html.Div([
    html.Div(children=[
        html.H3('Añadir ejercicio'),
        html.Div([
            html.Label('Ejercicio: '),
            dcc.Dropdown(['Elevación frontal del brazo', 'Flexión y extensión de tobillo','Flexión y extensión de codo','Rodilla al pecho'],
                        style={'width':'300px'},id='selector-ejercicio'),
            html.Label('Extremidad: '),
            dcc.Checklist(id='selector-izq-dcha',options=['Izquierda','Derecha'],value=['Izquierda'],inline=True)
        ], id='exercise_selection', style={'display':'flex','align-items':'center'}),
        html.Div([
                html.Label('Descripción: '),
                dcc.Textarea(placeholder='Descripción del ejercicio',id='descripcion-input',style={'width':'600px','height':'100px'}),
            ]),
        html.Br(),
        html.Div([
            html.Div([
                html.Label('Número de repeticiones'),
                dcc.Input(value='10', type='number',id='reps-input'),
            ]),
            html.Div([
                html.Label('Número de series'),
                dcc.Input(value='2', type='number',id='series-input'),
            ]),
            html.Div([
                html.Label('Descanso entre series (segundos)'),
                dcc.Input(value='5', type='number',id='descanso-input'),
            ])
        ],style={'display': 'flex', 'flex-direction': 'row'}),
    
        html.Div([
            html.Div(
                [html.Label('Ángulo superior'),
                dcc.Input(value='90', type='number',id='max-angle-input'),
            ]),
            html.Div([
                html.Label('Ángulo inferior'),
                dcc.Input(value='-90', type='number',id='min-angle-input')
            ]),
            
        ], style={'display': 'flex', 'flex-direction': 'row'}),
        html.Br(),
        html.Button('Añadir ejercicio', id='add-exercise', n_clicks=0),
        html.Div(id='mensaje-confirmacion'),       
        dcc.Interval(
            id='interval-confirmacion',
            interval=3000,
            n_intervals=0,
            disabled=False,
        )         
    ], style={'padding':'10px 50px', 'flex': 1}),

    dcc.Location(id='url-addExercise', refresh=True),
    html.Div(id='dummy-div')

], style={'display': 'flex', 'flex-direction': 'row'})



@callback(
    Output('mensaje-confirmacion','children',allow_duplicate=True),
    Output('interval-confirmacion','n_intervals',allow_duplicate=True),
    Input('add-exercise','n_clicks'),
    State('selector-ejercicio','value'),
    State('selector-izq-dcha','value'),
    State('descripcion-input','value'),
    State('reps-input','value'),
    State('series-input','value'),
    State('descanso-input','value'),
    State('max-angle-input','value'),
    State('min-angle-input','value'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def addExercise(n_clicks,ejer,extremidad,descripcion,reps,series,desc,maximo,minimo):
    global ejercicios
    if n_clicks>0:
        pacientes = db["pacientes"]
        paciente = pacientes.find_one({"Nombre":nombre, "Apellidos":apellidos})
        newExercise = {"Nombre":nombre,
            "Apellidos": apellidos,
            "Ejercicio":ejer,
            "Extremidad":" y ".join(extremidad),
            "Descripción":descripcion,
            "Repeticiones": reps,
            "Series":series,
            "Descanso":desc,
            "Superior":maximo,
            "Inferior":minimo,
            "Fecha": datetime.datetime.now().date().strftime("%d/%m/%y"),
            "Hora":datetime.datetime.now().strftime("%H:%M")
        }
        ejercicios.insert_one(newExercise)
        paciente["Ejercicios propuestos"].append(newExercise)
        pacientes.update_one({"Nombre": nombre, "Apellidos":apellidos}, {"$set": {"Ejercicios propuestos": paciente["Ejercicios propuestos"]}})
        
        return 'Ejercicio añadido',0
    else:
        return '',0

@callback(
    Output('mensaje-confirmacion','style',allow_duplicate=True),
    Input('interval-confirmacion','n_intervals'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def hideConfirmationMessage(n):
    if n<1:
        return {'display':'block'}
    else:
        return {'display':'none'}
    

@callback(
    Output('dummy-div','style'),
    Input('url-addExercise','pathname'),
)
def importName(pathname):
    from pages.home import nombre as name
    from pages.home import apellidos as surname
    global nombre, apellidos
    nombre = name
    apellidos = surname


