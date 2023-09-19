from pymongo import MongoClient
import certifi

import asyncio
from bleak import BleakScanner
from bleak import BleakClient, BleakGATTCharacteristic
from bleak.exc import BleakDeviceNotFoundError, BleakError
import struct

import asyncio
import threading

from dash import html, dcc, register_page, callback
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_daq as daq

import numpy as np

import time
import datetime

from flask import request


register_page(__name__,path='/monitoring')


# ------------------------- Lectura del sensor con Bleak ----------------------------------------
addressNicla1 = "74:F2:72:F8:BC:7C"
addressNicla2 = "AC:1F:E2:88:87:FC"

oriVal = "1001"
oriUUID = "19b10000-"+oriVal+"-537e-4f6c-d104768a1214"
initial_value = 0
anglesValue = {"Nicla1":(initial_value,0,0), "Nicla2":(initial_value,0,0)}
anglesList = {"Nicla1":[], "Nicla2":[]} #[(t0,angle0),(t1,angle1),...]
buffer = {"Nicla1":[], "Nicla2":[]}
formatted_data = {"Nicla1":(0,0,0), "Nicla2":(0,0,0)}


enable=True
subidasYbajadas = {"Nicla1":0, "Nicla2":0}
repeticiones = {"Nicla1":0, "Nicla2":0}
maxValue,minValue = {"Nicla1":[0], "Nicla2":[0]}, {"Nicla1":[0], "Nicla2":[0]}
rango={"Nicla1":[1], "Nicla2":[1]}


lock = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()

timeStamp=0




def callback1(sender: BleakGATTCharacteristic, data: bytearray):
    global formatted_data
    formatted_data['Nicla1'] = struct.unpack('<3h',data)

def callback2(sender: BleakGATTCharacteristic, data: bytearray):
    global formatted_data
    formatted_data['Nicla2'] = struct.unpack('<3h',data)



monitorizando=0

async def ble(address, nicla: str):
    print('NICLA SENSE ME')
    print('Looking for BLESense Peripheral Device...')
    global enable,anglesValue,anglesList,monitorizando
    
    while enable:
        async with BleakClient(address) as client:
        
            try:
                print('Conectado al Nicla Sense ME. Dir:',address)
                callback = callback1 if nicla=="Nicla1" else callback2
                await client.start_notify(oriUUID, callback)
                monitorizando=1
                t0 = time.time()
                while enable:
                    anglesValue[nicla] = formatted_data[nicla]
                    anglesList[nicla].append((time.time()-t0, -anglesValue[nicla][0]))
                    await asyncio.sleep(0.05)
                    

                await client.stop_notify(oriUUID)

            except (BleakError,BleakDeviceNotFoundError) as e:
                print(e)
                await client.stop_notify(oriUUID)
                continue
            
            except KeyboardInterrupt as e:
                await client.stop_notify(oriUUID)




def readAngles(address, nicla):
    asyncio.run(ble(address, nicla))



t_buffer = 0.01 #seg

def contadores(nicla):
    
    global enable, subidasYbajadas, repeticiones, buffer, maxValue, minValue, rango

    size=1/t_buffer # Tomo muestras durante 1 segundo para el buffer

    while enable:

        with lock:
            buffer[nicla].append(-anglesValue[nicla][0])


        if len(buffer[nicla])>=size: 
           
            diffAngles0 = np.diff(buffer[nicla][int(-size):int(-size/2)]).mean()
            diffAngles1 = np.diff(buffer[nicla][int(-size/2):]).mean()
            
            if np.abs(diffAngles1)>1/10: #1/5 es un umbral. Ver el else de este if para entenderlo
                
                if diffAngles0<0 and diffAngles1>0: #Se actualiza sólo el min, el max es el del tiempo anterior
                    minValue[nicla].append(min(buffer[nicla]))
                elif diffAngles0>0 and diffAngles1<0: #Viceversa. Uno de los Values es el actual y el otro el anterior
                    maxValue[nicla].append(max(buffer[nicla]))
                
                if diffAngles0*diffAngles1 < 0 and np.cov(buffer[nicla])>0.1: #cov para no contar temblores como repeticiones
                    subidasYbajadas[nicla]+=1
                    if subidasYbajadas[nicla]%2 != 0:
                        with lock3:
                            repeticiones[nicla] += 1 
                        print(nicla, repeticiones[nicla])

                    rango[nicla].append(maxValue[nicla][-1]-minValue[nicla][-1]) #Rango de movimiento
                    #Rango: amplitud del movimiento. minValue o maxValue son los valores del ángulo en los picos

                buffer[nicla] = buffer[nicla][int(-size/2):]

            else:
                buffer[nicla] = buffer[nicla][int(-size):int(-size/2)] #Se descartan las 5 últimas si no hay movimiento
                                                        #para ver si sigue subiendo o si baja
        time.sleep(t_buffer)
      
        








# ----------------------------------- Conectarse a la DB con pymongo ------------------------------------------
usernameDB = 'carlos'
passwordDB = '4994xIWET66oFGOu'
MONGODB_URI = "mongodb+srv://"+usernameDB+":"+passwordDB+"@cluster0.avyshq1.mongodb.net/"
clientPatient = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())


db = clientPatient["Rehabilitación"]
registros = db['registros']
nombre = ""
apellidos = ""
ejercicio = ""
limites = [0,0] # Superior, inferior
#pacientes = db['pacientes']
'''
paciente = {"Nombre":nombre,
    "Apellidos": '',
    "Edad":'',
    "Cuadro":'',
    "Username":'',
    "Password":'',
    "Ejercicios propuestos": [],
    "Registros": []
}
'''
username = ""
password = ""





# ------------------------------------ Feedback paciente: barras -------------------------------------------

boton_iniciar = html.Button('Iniciar',id='start-stop',n_clicks=0)


layout = html.Div([
    
    html.Div([

        html.Div([
            html.Div([
                html.Div([
                    html.Div("Ángulo: 0",id='slider-output-'+str(device)),
                    html.Div("Repeticiones"),
                    html.Div(daq.LEDDisplay(id='reps-score-'+str(device),value="3")),
                    html.Div([
                        dcc.Slider(
                            id='my-slider-'+str(device),
                            min=-120, max=120, value=0, step=1,
                            marks={0: {'label': '0'}},
                            vertical=True,
                            tooltip={"placement": "left", "always_visible": True},
                            verticalHeight=300)
                    ], id='slider-div-'+str(device))
                ]) for device in [1,2]], id="slider-divs") #2 Niclas
        ]+[boton_iniciar], id="left-div-sliders"),    

        html.Div([
            html.Div(id='descripcion-ejercicio'),
            html.Div([
                dcc.Dropdown(['Guardar','Descartar'], placeholder='Guardar/descartar', id='save-selector'),
                html.Button(['Aceptar'], id='save-button')
            ], id='save-div'),
            html.Label('Pulsa "Iniciar" para comenzar el ejercicio', id='mensaje')
        ], id='right-div-information')

    ], id='layout-monitoring'),


    dcc.Location(id='url-monitoring', refresh=True),
    dcc.Interval(
        id='graph-update',
        interval=0.1*1000,  # Actualiza el gráfico cada interval milisegundos
        n_intervals=0,
    ),
])



# Actualizar barra
@callback(Output('my-slider-1', 'value'),
            Output('my-slider-2', 'value'),
            Output('slider-div-1', 'style'),
            Output('slider-output-1', 'children'),
            Output('slider-div-2', 'style'),
            Output('slider-output-2', 'children'),
            Output('reps-score-1','value',allow_duplicate=True),
            Output('reps-score-2','value',allow_duplicate=True),
            Input('graph-update', 'n_intervals'),
            State('start-stop','n_clicks'),
            prevent_initial_call=True
)    
def update_graph(n_intervals,clicks_start):
    
    with lock:
        angleX_1 = -anglesValue["Nicla1"][0]
        angleX_2 = -anglesValue["Nicla2"][0]

    salida = [angleX_1, angleX_2]

    for angleX in [angleX_1,angleX_2]:
        if int(angleX)>int(limites[0]) or int(angleX)<int(limites[1]):
            color, mensaje ='#9EFF9E', 'SUPERADO: '+str(angleX) #verde
        else:
            color, mensaje ='#FFB5B5', "Ángulo: "+str(angleX) #rosa
        estilo = {'background-color':color,'width':'55px','display':'flex','justify-content':'center'}
        mensaje = mensaje if clicks_start%2 != 0 else "Ángulo: 0"
        salida.extend([estilo,mensaje]) 

    with lock3:
        salida.extend([repeticiones['Nicla1'],repeticiones['Nicla2']])
    
    if clicks_start%2==0 and clicks_start>0: 
            return salida

    if clicks_start%2==0 and clicks_start>0:
        raise PreventUpdate

    return salida



# Inicializar medidas
@callback(
        Output('start-stop','children'),
        Output('save-div','style',allow_duplicate=True),
        Output('mensaje','children',allow_duplicate=True),
        Input('start-stop','n_clicks'),
        prevent_initial_call=True
)
def initialize(clicks_start):

    global enable, subidasYbajadas, repeticiones, buffer, maxValue, minValue, rango, monitorizando

    if clicks_start%2 != 0:
        enable=True
        print(clicks_start)
        thread = threading.Thread(target=readAngles, args=(addressNicla1,"Nicla1",)) # readAngles, no readAngles()
        thread2 = threading.Thread(target=readAngles, args=(addressNicla2,"Nicla2",)) # readAngles, no readAngles()
        thread.start()
        thread2.start()
        subidasYbajadas["Nicla1"] = 0
        subidasYbajadas["Nicla2"] = 0

        counter1 = threading.Thread(target=contadores, args=("Nicla1",))
        counter2 = threading.Thread(target=contadores, args=("Nicla2",))
        counter1.start()
        counter2.start()

        while not monitorizando:
            time.sleep(0.1)

        return 'Finalizar',{'display':'none'},'Realizando ejercicio... Pulsa "Finalizar" cuando hayas terminado'
    

    elif clicks_start%2 == 0:
        enable=False
        monitorizando=0
        #thread.join()
        return ['Iniciar',{'display':'flex','align-items':'center'},
                'Ejercicio completado. Selecciona "guardar" o "descartar"']
    


# Guardar registro
@callback(
        Output('save-div','style',allow_duplicate=True),
        Output('mensaje','children',allow_duplicate=True),
        Output('reps-score-1','value',allow_duplicate=True),
        Output('reps-score-2','value',allow_duplicate=True),
        Input('save-button','n_clicks'),
        State('save-selector','value'),
        #State('name-input-paciente','value'),
        prevent_initial_call=True
)
def save(clicks_aceptar,save_discard):
   
    global enable, subidasYbajadas, repeticiones, buffer, maxValue, minValue, rango
    global anglesValue, anglesList, registros
    #global pacientes

    if save_discard == 'Guardar':
        print("HIOLA")
        #paciente = pacientes.find_one({"Nombre":name})
        register = {
            "Nombre":nombre,
            "Apellidos":apellidos,
            "Ejercicio":ejercicio,
            "Repeticiones izq/dcha": " / ".join([str(value) for value in repeticiones.values()]),
            #"Series": "3", # Redundante al existir campos de fecha y hora. 1 registro = 1 serie
            #"Descanso":"60", # Tampoco es necesario
            "Máximo izq/dcha": " / ".join([str(max(maxValue[key])) for key in maxValue.keys()]),
            "Mínimo izq/dcha": " / ".join([str(min(minValue[key])) for key in minValue.keys()]),
            "Angulos": anglesList,
            "Fecha": datetime.datetime.now().date().strftime("%d/%m/%y"),
            "Hora":datetime.datetime.now().strftime("%H:%M")
        }
        registros.insert_one(register)
        #paciente["Registros"].append(register) 
        #pacientes.update_one({"Nombre": name}, {"$set": {"Registros": paciente["Registros"]}})
    
    
    for nicla in ['Nicla1','Nicla2']:
        anglesValue[nicla] = (-initial_value,0,0)
        anglesList[nicla].clear()
        buffer[nicla].clear()
        maxValue[nicla] = [0]
        minValue[nicla] = [0]
        rango[nicla] = [0]
        repeticiones[nicla] = 0
        subidasYbajadas[nicla] = 0
    
    if save_discard == 'Descartar':
        return {'display':'none'},'¿Repetimos? Pulsa "Iniciar"',0,0 
    elif save_discard == 'Guardar':
        return {'display':'none'},'Guardado con éxito',0,0

    

@callback(
    Output('descripcion-ejercicio','children'),
    Output('slider-div-1','children'),
    Output('slider-div-2','children'),
    Input('url-monitoring','pathname'),
    prevent_initial_call='initial_duplicate'
)
def funcion(path):
    from pages.home import descripcion_ejercicios
    from pages.home import ejercicio as exercise

    global nombre, apellidos, ejercicio,limites,anglesValue,initial_value
    username = request.authorization['username']
    password = request.authorization['password']

    paciente = db["pacientes"].find_one({"Username":username,"Password":password})
    nombre = paciente['Nombre']
    apellidos = paciente['Apellidos']
    ejercicio = exercise
    limites = [int(db['ejercicios'].find_one({'Ejercicio':ejercicio})[limite]) for limite in ["Superior","Inferior"]]
    
    marks = {mark:{'label':str(mark)} for mark in range(limites[1],limites[0]+1,10)}
    estilo = {'style':{'color':'green', 'font-weight':'bold'}}
    _ = [marks[mark].update(estilo) for mark in marks if mark in [limites[0],limites[1]]]

    sup = limites[0]+10
    inf = limites[1]-10
    initial_value = limites[1]
    print(limites,type(limites[0]))
    for nicla in anglesValue:
        anglesValue[nicla] = (-initial_value,0,0)

    sliders = [dcc.Slider(
            id='my-slider-'+str(device),
            min=inf, max=sup, value=initial_value, step=1,
            marks=marks,
            vertical=True,
            tooltip={"placement": "left", "always_visible": True},
            verticalHeight=300
        ) for device in [1,2]]

    return descripcion_ejercicios.children, [sliders[0]], [sliders[1]]


