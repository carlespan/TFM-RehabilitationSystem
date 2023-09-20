# Añadir ejercicio

from pymongo import MongoClient
import certifi

from dash import html, dcc, register_page, callback
from dash.dependencies import Output, Input, State
import json



register_page(__name__,path='/add-patient')



# ----------------------------------- Conectarse a la DB con pymongo ------------------------------------------

with open("config.json","r") as config_file:
    config = json.load(config_file)

usernameDB = config["db_user"]
passwordDB = config["db_password"]

MONGODB_URI = "mongodb+srv://"+usernameDB+":"+passwordDB+"@cluster0.avyshq1.mongodb.net/?retryWrites=true&w=majority"
clientAdmin = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = clientAdmin["Rehabilitación"]





layout = html.Div([
    html.Div(children=[
        html.H3('Añadir paciente'),
        html.Br(),
        html.Div([
            html.Div([
                html.Div([
                    html.Label('Nombre'),
                    dcc.Input(placeholder='Nombre',id='nombre-input'),
                ], style={'margin':'0px 10px 0px'}),
                html.Div([
                    html.Label('Apellidos'),
                    dcc.Input(placeholder='Apellidos',id='apellidos-input'),
                ], style={'margin':'0px 10px 0px'}),
                html.Div([
                    html.Label('Edad'),
                    dcc.Input(placeholder='Edad',id='edad-input',style={'width':'60px'})
            ], style={'margin-left':'10px','width':'20px'}),
            ], style={'display': 'flex', 'flex-direction': 'row','margin':'0px 0px 15px'}),
            html.Div([
                html.Label('Cuadro clínico'),
                dcc.Textarea(placeholder='Descripción',id='cuadro-input',style={'width':'520px','height':'100px'}),
            ], style={'margin':'10px'}),
            html.Div([
                html.Div([
                    html.Label('Nombre de usuario'),
                    dcc.Input(placeholder='Usuario',id='username-input'),
                ], style={'margin':'0px 10px 0px'}),
                html.Div([
                    html.Label('Contraseña'),
                    dcc.Input(placeholder='Contraseña',id='password-input'),
                ], style={'margin':'0px 10px 0px'})
            ], style={'display': 'flex', 'flex-direction': 'row'})
        ]),

        html.Br(),
        html.Button('Añadir paciente', id='add-patient', n_clicks=0),
        html.Div(id='mensaje-confirmacion-patient'),       
        dcc.Interval(
            id='interval-confirmacion-patient',
            interval=3000,
            n_intervals=0,
            disabled=False,
        )         
    ], style={'padding': 30, 'flex': 1}),
])



@callback(
    Output('mensaje-confirmacion-patient','children',allow_duplicate=True),
    Output('interval-confirmacion-patient','n_intervals',allow_duplicate=True),
    Input('add-patient','n_clicks'),
    State('nombre-input','value'),
    State('apellidos-input','value'),
    State('edad-input','value'),
    State('cuadro-input','value'),
    State('username-input','value'),
    State('password-input','value'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def addPatient(n_clicks,nombre,apellidos,edad,cuadro,username,password):
    if n_clicks>0:
        pacientes = db["pacientes"]
        paciente = {"Nombre":nombre,
            "Apellidos": apellidos,
            "Edad":edad,
            "Cuadro":cuadro,
            "Username":username,
            "Password":password,
            #"Ejercicios propuestos": []
            #"Registros": []
        }
        pacientes.insert_one(paciente)
        
        return 'Paciente añadido',0
    else:
        return '',0

@callback(
    Output('mensaje-confirmacion-patient','style',allow_duplicate=True),
    Input('interval-confirmacion-patient','n_intervals'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def hideConfirmationMessage(n):
    if n<1:
        return {'display':'block'}
    else:
        return {'display':'none'}
    




