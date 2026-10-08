"""Configuración de pantallas. Cambia aquí etiquetas y ejemplos, no fórmulas."""
AUTOR = 'Emerson Yair Peralta Gonzales'
CARRERA = 'Software y Sistemas'
NOMBRE_APP = 'Estadística Lab'

# Cada campo: nombre interno, etiqueta visible, valor inicial, explicación.
def campo(nombre, etiqueta, valor, ayuda=''):
    return dict(nombre=nombre,etiqueta=etiqueta,valor=valor,ayuda=ayuda)

def pantalla(modulo, variante):
    if modulo=='muestra':
        tipo='proporcion' if variante!='media' else 'media'
        campos=[campo('confianza','Confianza (%)',99 if tipo=='proporcion' else 95),
                campo('error','Margen de error',.02 if tipo=='proporcion' else 200,'Proporción: 0,02 = 2%. Media: utiliza la unidad del sueldo, peso, etc.'),
                campo('poblacion','Población N (opcional)','','Déjalo vacío si el tamaño de población es desconocido.')]
        if tipo=='proporcion':campos.append(campo('p','Proporción esperada p',.5,'Entre 0 y 1; usa 0,5 si no hay estimación previa.'))
        else:campos.append(campo('dispersion','Dispersión poblacional',4000,'Selecciona abajo si este dato es desviación o varianza.'))
        return dict(titulo='Tamaño de muestra',subtitulo='Planifica cuántas observaciones necesitas.',campos=campos,ocultos={'parametro':tipo},variantes=[('proporcion','Proporción'),('media','Media')],seleccion=tipo,dispersion=tipo=='media')
    if modulo=='hipotesis':
        caso=variante if variante in ('media','proporcion','dos_medias','dos_proporciones') else 'media'
        campos=[campo('alpha','Significancia α',.01 if caso=='media' else .05,'0,05 equivale al 5%.'),campo('n','Tamaño de muestra n₁',36 if caso=='media' else 500)]
        if caso in ('media','dos_medias'):
            campos += [campo('media','Media muestral x̄₁',2510),campo('dispersion','Dispersión de la muestra/población 1',300)]
            if caso=='media':campos += [campo('referencia','Media planteada μ₀',2500)]
            else:campos += [campo('n2','Tamaño de muestra n₂',40),campo('media2','Media muestral x̄₂',2500),campo('dispersion2','Dispersión de la muestra/población 2',400)]
        else:
            campos += [campo('exitos','Personas con la característica x₁',300,'Cantidad entera: por ejemplo, 60% de 500 = 300.')]
            if caso=='proporcion':campos += [campo('referencia','Proporción planteada p₀',.65)]
            else:campos += [campo('n2','Tamaño de muestra n₂',500),campo('exitos2','Personas con la característica x₂',325)]
        return dict(titulo='Pruebas de hipótesis',subtitulo='De la afirmación a una decisión sustentada.',campos=campos,ocultos={'caso':caso},variantes=[('media','Una media'),('proporcion','Una proporción'),('dos_medias','Dos medias'),('dos_proporciones','Dos proporciones')],seleccion=caso,dispersion=caso in ('media','dos_medias'))
    modo=variante if variante in ('simple','inversa','doble') else 'simple'
    campos=[campo('x1','X₁',10),campo('x2','X₂',20),campo('y1','Y₁',100),campo('y2','Y₂',200),campo('x','Y a consultar' if modo=='inversa' else 'X a consultar',150 if modo=='inversa' else 15)]
    if modo=='doble':campos += [campo('y','Y a consultar',150),campo('z11','Z en (X₁,Y₁)',20),campo('z21','Z en (X₂,Y₁)',40),campo('z12','Z en (X₁,Y₂)',60),campo('z22','Z en (X₂,Y₂)',100)]
    return dict(titulo='Interpolación',subtitulo='Explora cómo cambia un valor entre datos conocidos.',campos=campos,ocultos={'modo':modo},variantes=[('simple','Simple'),('inversa','Inversa'),('doble','Doble')],seleccion=modo,dispersion=False)
