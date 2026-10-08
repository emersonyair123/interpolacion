"""Adaptador web para GitHub Pages: se ejecuta en Python dentro del navegador.
No requiere un servidor Flask ni mantener encendida una laptop.
"""
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from calculos import muestra, hipotesis, interpolacion
from graficos import crear_grafico
from formularios import pantalla, AUTOR, CARRERA, NOMBRE_APP

env=Environment(loader=FileSystemLoader('templates'),autoescape=select_autoescape(['html']))

def url_for(tipo,filename):
    return 'static/'+filename

def responder(pedido_json):
    pedido=json.loads(pedido_json)
    modulo=pedido.get('modulo','muestra')
    if modulo not in ('muestra','hipotesis','interpolacion'):modulo='muestra'
    config=pantalla(modulo,pedido.get('variante',''))
    valores=pedido.get('datos') or {}
    resultado=None;grafico=None;error=None
    if pedido.get('calcular'):
        try:
            resultado={'muestra':muestra,'hipotesis':hipotesis,'interpolacion':interpolacion}[modulo](valores)
            grafico=crear_grafico(resultado['grafico'])
        except (ValueError,OverflowError,ZeroDivisionError) as exc:
            error=str(exc) or 'Los valores no permiten realizar este cálculo.'
    return env.get_template('index.html').render(modulo=modulo,config=config,valores=valores,
        resultado=resultado,grafico=grafico,error=error,autor=AUTOR,carrera=CARRERA,
        nombre_app=NOMBRE_APP,url_for=url_for)
