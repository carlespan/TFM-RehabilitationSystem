from flask import request
from pymongo import MongoClient
import certifi

import pandas as pd

usernameDB = 'carlos'
passwordDB = '4994xIWET66oFGOu'
MONGODB_URI = "mongodb+srv://"+usernameDB+":"+passwordDB+"@cluster0.avyshq1.mongodb.net/?retryWrites=true&w=majority"
clientAdmin = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = clientAdmin["Rehabilitación"]



PATIENTS_CREDENTIALS = {paciente['Username']:paciente['Password'] for paciente in db['pacientes'].find()}
MEDICOS_CREDENTIALS = {}

def usuario(username,password):
    paciente = db['pacientes'].find_one({"Username":username,"Password":password})
    medico = db['medicos'].find_one({"Username":username,"Password":password})
    if paciente:
        nombre = paciente['Nombre']
        apellidos = paciente['Apellidos']
        tipo_usuario = 'Paciente'
    elif medico:
        nombre = medico['Nombre']
        apellidos = medico['Apellidos']
        tipo_usuario = 'Medico'
    elif username=='carlos' and password=='administrador':
        nombre = 'Carlos'
        apellidos = 'Admin'
        tipo_usuario = 'Administrador'
    
    return nombre, apellidos, tipo_usuario
    

def get_exercise_data(nombre,ejercicio):
    registros = list(db['registros'].find({'Nombre':nombre, 'Ejercicio':ejercicio}))
    if len(registros):
        df_reg = pd.DataFrame(registros)
    else:
        df_reg = pd.DataFrame({'_id':[],'Angulos':[]})
    df_reg['_id'] = df_reg['_id'].astype(str)
    df_reg['Angulos'] = df_reg['Angulos'].astype(str)

    return df_reg
