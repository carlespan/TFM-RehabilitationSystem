from pymongo import MongoClient
import certifi

from dash import Dash, html, dcc, page_registry, page_container, register_page
from dash.dependencies import Output, Input, State
import dash_auth
#import dash_enterprise_auth as auth

from flask import render_template
from flask import request




# ------------------------------- CONECTARSE A MONGODB -------------------------------------
usernameDB = 'carlos'
passwordDB = '4994xIWET66oFGOu'
MONGODB_URI = "mongodb+srv://"+usernameDB+":"+passwordDB+"@cluster0.avyshq1.mongodb.net/?retryWrites=true&w=majority"
clientAdmin = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = clientAdmin["Rehabilitación"]




# ------------------------------------- DASH --------------------------------------------
external_stylesheets = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
                        "https://codepen.io/chriddyp/pen/bWLwgP.css"]

"""
server = flask.Flask(__name__)
@server.route('/pages')
def page1():
    return render_template('index.html')
"""


app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
           use_pages=True)




PATIENTS_CREDENTIALS = {paciente['Username']:paciente['Password'] for paciente in db['pacientes'].find()}
MEDICOS_CREDENTIALS = {medico['Username']:medico['Password'] for medico in db['medicos'].find()}


VALID_USERNAME_PASSWORD_PAIRS = PATIENTS_CREDENTIALS | MEDICOS_CREDENTIALS
VALID_USERNAME_PASSWORD_PAIRS.update({"carlos":"administrador"})

authentication = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)





# ----------------------------------- Conectarse a la DB con pymongo ------------------------------------------
usernameDB = 'carlos'
passwordDB = '4994xIWET66oFGOu'

MONGODB_URI = "mongodb+srv://"+usernameDB+":"+passwordDB+"@cluster0.avyshq1.mongodb.net/?retryWrites=true&w=majority"
clientAdmin = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = clientAdmin["Rehabilitación"]

pacientes = db['pacientes']






# ---------------------------------------- Layout principal -------------------------------------------------

layout_exercises =  html.Div([
    dcc.Location(id='url', refresh=True),
    page_container
], id='home', style={'display':'none'})


    
app.layout = layout_exercises


username = ''
password = ''



# Mostrar pantalla principal al inciar sesión
@app.callback(
    Output('home','style'),
    Input('url', 'pathname')
)
def update_output_div(n):
    global username,password
    username = request.authorization['username']
    password = request.authorization['password']
    if username in VALID_USERNAME_PASSWORD_PAIRS.keys() and VALID_USERNAME_PASSWORD_PAIRS[username]==password:
        return {'display':'block'}


# Mostrar interfaz del médico/paciente según el tipo de usuario
@app.callback(
    Output('heading-medico','children'),
    Output('heading-medico','style'),
    Output('new-exercise','style'),
    Output('delete-exercise','style'),
    State('new-exercise','style'),
    State('delete-exercise','style'),
    State('heading-medico','children'),
    Input('url','pathname')
)
def Heading(new_exercise,delete_exercise,heading_medico,url):

    administrador = username=='carlos' and password=='administrador'

    if (username in MEDICOS_CREDENTIALS.keys() and MEDICOS_CREDENTIALS[username]==password) or administrador:
        heading = heading_medico
        add_exer_button = new_exercise
        delete_exer_button = delete_exercise

    elif username in PATIENTS_CREDENTIALS.keys() and PATIENTS_CREDENTIALS[username]==password:
        nombre = pacientes.find_one({'Username':username,'Password':password})['Nombre']
        bienvenida = html.H2('Hola, '+nombre, style={'position':'absolute','top':'10px','right':'50px'})
        heading_paciente = html.Div([bienvenida,dcc.Dropdown(value=nombre, id='name-input',style={'display':'none'})])
        heading = heading_paciente
        add_exer_button = {'display':'none'}
        delete_exer_button = {'display':'none'}

    
    salida = [heading, {'display':'flex','align-items':'center','padding':'10px 20px'}, add_exer_button, delete_exer_button]
    return salida


@app.callback(
    Output('training-access','style'),
    Input('tabla-ejercicios-propuestos','active_cell')
)
def TrainingButton(active_cell):

    if username in MEDICOS_CREDENTIALS.keys() and MEDICOS_CREDENTIALS[username]==password:
        return {'display':'none'}
    else:
        return {'position':'absolute', 'bottom':'25px','right':'25px'}





if __name__ == '__main__':
    app.run(debug=True)

