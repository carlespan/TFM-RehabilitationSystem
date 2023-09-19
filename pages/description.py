from dash import html, register_page

register_page(__name__,path='/description')

layout = html.Div([
    html.H2("Elevación frontal del brazo",className='img_title'),
    html.Div([
        html.Img(src='assets/images/ejercicio1.JPG',style={'width':'15%','padding-top':'2%'}),
        html.Img(src='assets/images/ejercicio1_dispositivo.JPG',style={'padding-top':'2%'})
    ],className='img_div'),
    html.H2("Flexión y extensión de tobillo",className='img_title'),
    html.Div([
        html.Img(src='assets/images/ejercicio2.JPG'),
        html.Img(src='assets/images/ejercicio2_dispositivo.JPG',style={'width':'10%'})
    ],className='img_div'),
    html.H2("Flexión y extensión de codo",className='img_title'),
    html.Div([
        html.Img(src='assets/images/ejercicio3.JPG',style={'width':'15%'}),
        html.Img(src='assets/images/ejercicio3_dispositivo.JPG',style={'width':'30%'})
    ],className='img_div'),
    html.H2("Rodilla al pecho",className='img_title'),
    html.Div([
        html.Img(src='assets/images/ejercicio4.JPG',style={'width':'30%'}),
        html.Img(src='assets/images/ejercicio4_dispositivo.JPG')
    ],className='img_div'),
], style={'margin':'3%'})
