from pymongo import MongoClient
import certifi
from bson.objectid import ObjectId

from dash import html, dcc, dash_table, register_page, callback, page_container, page_registry
from dash.dependencies import Output, Input, State
import dash_mantine_components as dmc

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

from funciones.funciones_auxiliares import usuario

from flask import request



register_page(__name__,path='/')


# ----------------------------------- Conectarse a la DB con pymongo ------------------------------------------

usernameDB = 'carlos'
passwordDB = '4994xIWET66oFGOu'
MONGODB_URI = "mongodb+srv://"+usernameDB+":"+passwordDB+"@cluster0.avyshq1.mongodb.net/?retryWrites=true&w=majority"
clientAdmin = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = clientAdmin["Rehabilitación"]






# ---------------------------------------- Layout principal -------------------------------------------------

pacientes = db["pacientes"]
nombre = ""
apellidos = ""
tipo_usuario = ""
ejercicio = ""
records = "-/-"



fig=go.Figure()

graficas_ejercicios =  html.Div([
    dcc.Graph(id='graph',figure=fig),
    dcc.Checklist(id='check-izq-dcha',options=['Izquierda','Derecha'],value=['Izquierda'],inline=True),
    dmc.MultiSelect(
        id="date-dropdown",
        label="Seleccionar día y fecha",
        placeholder="Día/fecha",
        style={'width':'600px','margin':'20px'}
    )], id='selector-entrenamiento')

tabla_ejercicios_registro = html.Div([
    dash_table.DataTable(
        id='tabla-ejercicios-registro',
        hidden_columns=['_id','Angulos'],
        style_table={'width':'40%'},
        style_cell={'width':'auto','textAlign':'center','verticalAlign':'center'},
        #export_format='none',
        css =[{"selector":".show-hide", "rule": "display: none"}]
    ),
    html.Button(html.I(className="fa fa-download"), n_clicks=0, id='download-data-button'),
    dcc.Download(id='download-data-csv')
])


df = pd.DataFrame() # df con los ejercicios propuestos. Se crea al introducir el nombre del paciente

tabla_ejercicios_propuestos = html.Div([
            dash_table.DataTable(
                id='tabla-ejercicios-propuestos',
                #style_table={'width':'100%'},
                style_cell={'width':'auto','height':'30px','whiteSpace': 'normal', 'wordWrap': 'break-word',
                            'textAlign':'center','verticalAlign':'center'},
                #export_format='none',
                ),
            html.Div([
                dcc.Link(
                    html.Button(html.I(className="fa fa-plus"), n_clicks=0, id='new-exercise'),
                    href=page_registry['pages.add-exercise']['relative_path'],
                    id='add-exercise-link'
                ),
                html.Button(html.I(className="fa fa-minus"),id='delete-exercise',n_clicks=0)
            ], id='buttons-add-delete'),
            dcc.Link(html.Button("Descripción gráfica de los ejercicios"),
                    href=page_registry['pages.description']['relative_path'],
                    id='graphic_description'
            )
],id='tabla-ejercicios-propuestos-div')


descripcion_ejercicios = html.Div(children=[], id='info', className='info-hidden')


heading_medico = html.Div([
            html.Div([
                html.Label('Paciente:'),
                dcc.Dropdown([paciente["Nombre"]+' '+paciente["Apellidos"] for paciente in list(db['pacientes'].find())],
                                placeholder='Nombre y apellidos',
                                id='name-input')
            ]),
            dcc.Link(html.Button("Nuevo paciente",n_clicks=0,id='new-patient'),
                        href=page_registry['pages.add-patient']['relative_path'],
                        id='add-patient-link')
], id='heading-medico', className='medico_component', style={'display':'none'})



layout = html.Div([
    heading_medico,
    html.Div([
        html.H3('Tabla de ejercicios', id='tabla-ejercicios-title'),
        #dcc.Interval(id='interval_db',interval = 86400000 * 7,n_intervals = 0),
        html.Div([tabla_ejercicios_propuestos, descripcion_ejercicios], 
                id='ejercicios-propuestos'),
        html.Hr(),
        html.H3('Entrenamientos realizados',style={'position':'relative','left':'40px'}),
        html.Div([tabla_ejercicios_registro, graficas_ejercicios], 
                style={'display':'none'},
                id='ejercicios-registro')
    ], style={'margin-top':'30px'}),
    dcc.Location(id='url-home', refresh=True)
], id='home-layout')





@callback(
        Output('name-input','options'),
        Input('url-home','pathname')
)
def ShowPatients(path):
    return [paciente["Nombre"]+' '+paciente["Apellidos"] for paciente in list(db['pacientes'].find())]


# Ejercicios propuestos: Tabla al introducir el nombre del paciente
@callback(
    Output('tabla-ejercicios-propuestos','data'),
    Output('tabla-ejercicios-propuestos-div','style'),
    Input('name-input','value'),
    Input('url-home','pathname')
)
def ShowTable(patient_selected,path):

    # A LOS PACIENTES NO LES SALE TABLA POR CULPA DEL IF FULLNAME. PERO ME INTERESA TENERLO,
    # PORQUE ASÍ DIFERENCIO AL USUARIO DEL MÉDICO QUE VARÍA LOS NOMBRES DEL USUARIO DEL PACIENTE
    # QUE EL NOMBRE SIEMPRE ES EL MISMO. NO PREOCUPARSE, PORQUE SI PONGO FULLNAME=DAVID MUÑOZ CALVO 
    # ME SALE LA TABLA SIN PROBLEMA

    global df, nombre, apellidos, tipo_usuario
    
    username = request.authorization['username']
    password = request.authorization['password']
    name, surname, tipo_usuario = usuario(username,password)
    print(name,surname,tipo_usuario)
    
    if tipo_usuario=='Paciente':
        fullname = name+' '+surname
    elif tipo_usuario=='Medico' or tipo_usuario=='Administrador':
        fullname = patient_selected
    
    
    if fullname: # nombre introducido por el médico
        nombre = [paciente['Nombre'] for paciente in list(db['pacientes'].find()) 
                if paciente['Nombre']+' '+paciente["Apellidos"]==fullname][0]
        apellidos = [paciente['Apellidos'] for paciente in list(db['pacientes'].find()) 
                    if paciente['Nombre']+' '+paciente["Apellidos"]==fullname][0]
        #paciente = pacientes.find_one({"Nombre":nombre})
        ejercicios_paciente = list(db['ejercicios'].find({"Nombre":nombre, "Apellidos":apellidos}))
        if ejercicios_paciente:
            df = pd.DataFrame(ejercicios_paciente)
            df['_id'] = df['_id'].astype(str) # Los datos de la tabla deben ser str
            #df['Extremidad'] = [" y ".join(df['Extremidad'][i]) for i in range(df.shape[0])]
            hidden_cols = ['_id','Nombre','Apellidos','Descripción','Hora','Repeticiones','Series','Descanso','Superior','Inferior']
            data = df[[col for col in df.columns if col not in hidden_cols]].to_dict('records')
            
            return data, {'display':'inline-block','width':'600px'}
        
        return [{'Ejercicio':'-','Extremidad':'-','Fecha':'-'}],{'display':'inline-block','width':'600px'}
    
    else:
        return [{'Ejercicio':'-','Extremidad':'-','Fecha':'-'}],{'display':'inline-block','width':'600px'}




# Eliminar ejercicio
@callback(
        Output('tabla-ejercicios-propuestos','data',allow_duplicate=True),
        Input('delete-exercise','n_clicks'),
        State('tabla-ejercicios-propuestos','active_cell'),
        prevent_initial_call='initial_duplicate'
)
def deleteExercise(click_delete, active_cell):
    global df, records
    
    if active_cell:
        db['ejercicios'].delete_one({'Ejercicio':ejercicio})
        db['registros'].delete_many({'Ejercicio':ejercicio})

    ejercicios_paciente = list(db['ejercicios'].find({"Nombre":nombre, "Apellidos":apellidos}))
    if ejercicios_paciente:
        df = pd.DataFrame(ejercicios_paciente)
        df['_id'] = df['_id'].astype(str) # Los datos de la tabla deben ser str
        #df['Extremidad'] = [" y ".join(df['Extremidad'][i]) for i in range(df.shape[0])]
        hidden_cols = ['_id','Nombre','Apellidos','Descripción','Hora','Repeticiones','Series','Descanso','Superior','Inferior']
        data = df[[col for col in df.columns if col not in hidden_cols]].to_dict('records')
    else:
        data = [{'Ejercicio':'-','Extremidad':'-','Fecha':'-'}]
    
    return data




# Registro de ejercicios: Datos, tabla y gráficas al hacer click en la tabla de ejercicios propuestos
@callback(
    Output('ejercicios-registro','style',allow_duplicate=True),
    Output('info','className'),
    Output('delete-exercise','style',allow_duplicate=True),
    Output('tabla-ejercicios-registro','data'),
    Output('info','children'),
    Output('date-dropdown','data'),
    Output('graph','figure',allow_duplicate=True),
    Input('tabla-ejercicios-propuestos','active_cell'),
    prevent_initial_call=True
)
def ShowExerciseData(active_cell):
    global fig, ejercicio, descripcion_ejercicios, records
    if active_cell:
        row = active_cell['row']
        ejercicio = df['Ejercicio'][row]
        #registros = pacientes.find_one({"Nombre":nombre})["Registros"]
        registros = list(db['registros'].find({'Nombre':nombre, 'Ejercicio':ejercicio}))
        if len(registros):
            df_reg = pd.DataFrame(registros)
            maximos = [str(max([int(reg['Máximo izq/dcha'].split(' / ')[i]) for reg in registros])) for i in range(2)]
            minimos = [str(min([int(reg['Mínimo izq/dcha'].split(' / ')[i]) for reg in registros])) for i in range(2)]
            records = "Máx: "+"/".join(maximos)+" || Mín: "+"/".join(minimos)
        else:
            df_reg = pd.DataFrame({'_id':[],'Angulos':[]})
            records = "- / -"
        df_reg['_id'] = df_reg['_id'].astype(str)
        df_reg['Angulos'] = df_reg['Angulos'].astype(str)

        datos = df_reg[[col for col in df_reg.columns if col not in ['_id','Nombre','Apellidos','Ejercicio','Angulos']]].to_dict('records')

        #df["Descripción"][row] = "-" if df["Descripción"][row] is None else df["Descripción"]

        info = [html.H4("Ejercicio: "+ejercicio), html.Strong("Descripción: "+df["Descripción"][row])]
        hidden_cols = ['_id','Nombre','Apellidos','Ejercicio','Descripción','Fecha','Hora']
        info.extend([html.Label(col+': '+str(df[col][row])) 
                     for col in df.columns if col not in hidden_cols])
        info.extend([html.Div([html.I(className="fa fa-star"), " Récord personal izq/dcha: ",
                               html.Div(records, id='personal_records')],
                              style={'margin-top':'10px'})])

        info.extend([
                html.Div([
                    dcc.Link(["Entrenar ",
                        html.I(className="fa fa-play fa-lg", style={'margin-left':'10px'})],
                        href=page_registry['pages.monitoring']['relative_path'])
                ], id='training-access', className='patient-component', style={'display':'none'})
        ])
      
        descripcion_ejercicios.children = info # Para importar en Paciente.py

        fig.layout={
                    #'colorway':['red','green']
                    'title':{'text':'Ejercicio: '+ejercicio, 'x':0.5},
                    'xaxis':{'title':'Tiempo(s)'},
                    'yaxis':{'title':'Ángulo'}
                }
        limites = [db['ejercicios'].find_one({'Ejercicio':ejercicio})[limite] for limite in ["Superior","Inferior"]]
        fig.add_hline(limites[0])
        fig.add_hline(limites[1])
        fig.data=[]

        dates = [{"label":df_reg['Fecha'][i]+'-'+df_reg['Hora'][i], 
                  "value":df_reg['_id'][i]} for i in df_reg.index]
      
        register_style = {'display':'flex','justify-content':'center','margin-left':'50px'}
        delete_button_style = {'display':'none'} if tipo_usuario=='Paciente' else {'display':'inline-block'}

        return register_style,'info-shown',delete_button_style,datos,info,dates,fig
        



# Descarga
@callback(
        Output('download-data-csv','data'),
        Input('download-data-button','n_clicks'),
        prevent_initial_call=True
)
def download(click_download):
    data = db['registros'].find({'Nombre':nombre,'Apellidos':apellidos,'Ejercicio':ejercicio})
    df_dowload = pd.DataFrame(data)
    return dcc.send_data_frame(df_dowload.to_csv, nombre+"_"+apellidos+"_"+ejercicio+".csv")




# Herramientas de selección en la gráfica
@callback(
    Output('graph','figure',allow_duplicate=True),
    Input('check-izq-dcha','value'),
    Input('date-dropdown','value'),
    prevent_initial_call=True
)
def ShowGraphics(extremidades,IDs):

    global fig
    
    fig.data=[]

    for num in IDs:
        doc = db['registros'].find_one({"_id":ObjectId(num)})
        oriDICT = doc['Angulos']
        for extremidad in extremidades:
            nicla = "Nicla1" if extremidad=="Izquierda" else "Nicla2"
            name = doc["Fecha"]+'-'+doc["Hora"] if len(IDs)>1 else extremidad
            fig.add_traces([
                go.Scatter(x=[puntos[0] for puntos in oriDICT[nicla]], y=[puntos[1] for puntos in oriDICT[nicla]],
                        name=name)
                ])
        
    return fig







