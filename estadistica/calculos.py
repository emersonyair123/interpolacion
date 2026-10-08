"""Motor matemático: funciones independientes de la página web.

Aquí se modifican las FÓRMULAS. Los campos de pantalla están en formularios.py.
Las probabilidades provienen de scipy.stats, no de tablas interpoladas.
"""
from math import sqrt, ceil, isfinite
from scipy.stats import norm, t


def numero(datos, nombre, minimo=None, maximo=None, entero=False):
    """Lee un campo; admite coma decimal y rechaza vacíos, NaN e infinitos."""
    try:
        valor = float(str(datos.get(nombre, '')).strip().replace(',', '.'))
    except (ValueError, TypeError):
        raise ValueError(f'Completa {nombre} con un número válido.')
    if not isfinite(valor):
        raise ValueError(f'{nombre}: el número debe ser finito.')
    if minimo is not None and valor < minimo:
        raise ValueError(f'{nombre} debe ser mayor o igual a {minimo}.')
    if maximo is not None and valor > maximo:
        raise ValueError(f'{nombre} debe ser menor o igual a {maximo}.')
    if entero and not valor.is_integer():
        raise ValueError(f'{nombre} debe ser un número entero.')
    return int(valor) if entero else valor


def fmt(x):
    """Formato de lectura; no redondea los valores usados en los cálculos."""
    return f'{x:.6g}'


def dispersion(d, campo='dispersion'):
    valor = numero(d, campo, 1e-12)
    tipo = d.get('tipo_dispersion', 'desviacion')
    if tipo not in ('desviacion', 'varianza'):
        raise ValueError('Selecciona desviación o varianza.')
    return sqrt(valor) if tipo == 'varianza' else valor


def muestra(d):
    """n0=Z²pq/e² o n0=(Zσ/e)²; corrección finita y techo entero."""
    confianza = numero(d, 'confianza', 50, 99.99) / 100
    error = numero(d, 'error', 1e-12)
    z = float(norm.ppf((1 + confianza) / 2))
    if d.get('precision_z') == 'tabla':
        z = round(z, 3)
    if d.get('parametro') == 'proporcion':
        p = numero(d, 'p', 0.0001, 0.9999)
        if error >= 1:
            raise ValueError('En proporciones, ingresa el error como decimal: 0,02 equivale al 2%.')
        n0 = z*z*p*(1-p)/(error*error)
        formula = 'n₀ = Z² · p · (1 − p) / e²'
        sustitucion = f'n₀ = {fmt(z)}² × {fmt(p)} × {fmt(1-p)} / {fmt(error)}² = {fmt(n0)}'
    else:
        sigma = dispersion(d)
        n0 = (z*sigma/error)**2
        formula = 'n₀ = (Z · σ / e)²'
        sustitucion = f'n₀ = ({fmt(z)} × {fmt(sigma)} / {fmt(error)})² = {fmt(n0)}'
    pasos = [f'Confianza = {confianza:.2%}; α = {1-confianza:.4f}; Z = {fmt(z)}.', formula, sustitucion]
    N = None
    if str(d.get('poblacion', '')).strip():
        N = numero(d, 'poblacion', 2, entero=True)
        n_real = N*n0/(N-1+n0)
        pasos.append(f'Población finita: n = N·n₀/(N−1+n₀) = {fmt(n_real)}.')
    else:
        n_real = n0
        pasos.append('Población desconocida: se utiliza n₀ sin corrección finita.')
    n = ceil(n_real)
    pasos.append(f'Redondeo siempre hacia arriba: n = {n}.')
    return dict(titulo='Tamaño de muestra recomendado', valor=str(n), unidad='observaciones',
                pasos=pasos, conclusion=f'Se requieren al menos {n} observaciones bajo los supuestos indicados.',
                aviso='Supone muestreo aleatorio simple. Z usa la precisión elegida en el formulario; el redondeo de tablas puede cambiar el entero final.',
                grafico=dict(tipo='confianza', confianza=confianza, z=z, n=n),
                n=n, n_real=n_real)


def cola_resultado(estadistico, distribucion, alpha, cola):
    """Probabilidad y región crítica para las tres hipótesis alternativas."""
    if cola == 'mayor':
        pvalor = distribucion.sf(estadistico)
        criticos = [distribucion.ppf(1-alpha)]
    elif cola == 'menor':
        pvalor = distribucion.cdf(estadistico)
        criticos = [distribucion.ppf(alpha)]
    elif cola == 'diferente':
        pvalor = 2*distribucion.sf(abs(estadistico))
        criticos = [distribucion.ppf(alpha/2), distribucion.ppf(1-alpha/2)]
    else:
        raise ValueError('Selecciona una hipótesis alternativa válida.')
    return float(pvalor), [float(v) for v in criticos]


def hipotesis(d):
    """Pruebas de una media/proporción y de dos muestras independientes.

    Media: Z con σ conocida; t con s; Z aproximada por opción del curso.
    Dos medias: Welch con varianzas desconocidas; Z si conocidas.
    Dos proporciones: proporción combinada bajo H0:p1=p2.
    """
    alpha = numero(d, 'alpha', 0.0001, 0.5)
    cola = d.get('cola', 'diferente')
    op = {'mayor':'>', 'menor':'<', 'diferente':'≠'}.get(cola)
    if op is None: raise ValueError('Hipótesis alternativa inválida.')
    caso = d.get('caso', 'media')
    n = numero(d, 'n', 2, entero=True)
    gl = None
    avisos = []
    if caso == 'media':
        media = numero(d, 'media')
        referencia = numero(d, 'referencia')
        sd = dispersion(d)
        metodo = d.get('metodo', 't')
        if metodo not in ('t', 'z', 'z_aprox'): raise ValueError('Método inválido.')
        if metodo == 'z_aprox' and n < 30:
            raise ValueError('La aproximación Z del curso requiere n ≥ 30. Usa t con s desconocida.')
        gl = n-1 if metodo == 't' else None
        ee = sd/sqrt(n)
        estadistico = (media-referencia)/ee
        parametro = f'μ {op} {fmt(referencia)}'
        h0 = f'μ = {fmt(referencia)}'
        formula = '(media muestral − μ₀) / (desviación / √n)'
        sustitucion = f'({fmt(media)} − {fmt(referencia)}) / ({fmt(sd)} / √{n})'
        if metodo == 'z_aprox': avisos.append('Z aproximada con s: opción pedagógica del curso. Si σ es desconocida, t es la prueba habitual.')
        avisos.append('Requiere muestra aleatoria independiente y normalidad poblacional o una aproximación adecuada para la media.')
    elif caso == 'proporcion':
        referencia = numero(d, 'referencia', 0.0001, .9999)
        x = numero(d, 'exitos', 0, n, entero=True)
        p = x/n
        ee = sqrt(referencia*(1-referencia)/n)
        estadistico = (p-referencia)/ee
        parametro = f'p {op} {fmt(referencia)}';h0=f'p = {fmt(referencia)}'
        formula = '(p̂ − p₀) / √[p₀(1−p₀)/n]'
        sustitucion = f'({fmt(p)} − {fmt(referencia)}) / √[{fmt(referencia)} × {fmt(1-referencia)} / {n}]'
        avisos.append(f'p̂ = {x}/{n} = {fmt(p)}. Éxitos/fracasos esperados: {fmt(n*referencia)} y {fmt(n*(1-referencia))}.')
        if min(n*referencia, n*(1-referencia)) < 10:
            raise ValueError('Aproximación normal insuficiente: np₀ y n(1−p₀) deben ser ≥ 10. Se necesita una prueba binomial exacta (no incluida).')
    elif caso == 'dos_medias':
        n2=numero(d,'n2',2,entero=True)
        m1=numero(d,'media');m2=numero(d,'media2')
        s1=dispersion(d);s2=dispersion(d,'dispersion2')
        v1=s1*s1/n;v2=s2*s2/n2
        ee=sqrt(v1+v2);estadistico=(m1-m2)/ee
        if d.get('metodo') == 't':
            gl=(v1+v2)**2/(v1*v1/(n-1)+v2*v2/(n2-1))
        elif d.get('metodo') != 'z': raise ValueError('Método inválido.')
        h0='μ₁ − μ₂ = 0';parametro=f'μ₁ − μ₂ {op} 0'
        formula='(media₁ − media₂) / √(s₁²/n₁ + s₂²/n₂)'
        sustitucion=f'({fmt(m1)} − {fmt(m2)}) / √({fmt(s1)}²/{n} + {fmt(s2)}²/{n2})'
        avisos.append('Muestras independientes; con σ desconocidas se aplica t de Welch, sin asumir varianzas iguales. No sirve para datos pareados.')
    elif caso == 'dos_proporciones':
        n2=numero(d,'n2',2,entero=True)
        x1=numero(d,'exitos',0,n,entero=True);x2=numero(d,'exitos2',0,n2,entero=True)
        p1=x1/n;p2=x2/n2;pc=(x1+x2)/(n+n2)
        if min(n*pc,n*(1-pc),n2*pc,n2*(1-pc)) < 10:
            raise ValueError('Frecuencias esperadas menores de 10: esta aproximación Z no es adecuada.')
        ee=sqrt(pc*(1-pc)*(1/n+1/n2));estadistico=(p1-p2)/ee
        h0='p₁ − p₂ = 0';parametro=f'p₁ − p₂ {op} 0'
        formula='(p̂₁ − p̂₂) / √[p̂c(1−p̂c)(1/n₁+1/n₂)]'
        sustitucion=f'({fmt(p1)} − {fmt(p2)}) / √[{fmt(pc)} × {fmt(1-pc)} × (1/{n}+1/{n2})]'
        avisos.append('Muestras independientes y proporción combinada bajo H₀: p₁ = p₂.')
    else: raise ValueError('Tipo de prueba inválido.')
    dist=t(df=gl) if gl is not None else norm
    nombre='t' if gl is not None else 'Z'
    pvalor, criticos=cola_resultado(estadistico,dist,alpha,cola)
    rechaza=pvalor<=alpha
    decision='Se rechaza H₀' if rechaza else 'No se rechaza H₀'
    conclusion=(f'Al {alpha:.2%} de significancia, hay evidencia a favor de {parametro}.' if rechaza else
                f'Al {alpha:.2%} de significancia, no hay evidencia suficiente a favor de {parametro}. No demuestra que H₀ sea verdadera.')
    pasos=[f'H₀: {h0}. H₁: {parametro}.', f'α = {fmt(alpha)}. Distribución {nombre}'+(f'; grados de libertad = {fmt(gl)}.' if gl is not None else '.'),
           f'Error estándar = {fmt(ee)}.',f'{nombre} = {formula}',f'{nombre} = {sustitucion} = {fmt(estadistico)}',
           f'Valor(es) crítico(s): {", ".join(fmt(c) for c in criticos)}.',f'Valor p = {fmt(pvalor)}. Rechazar H₀ si p ≤ α.',decision+'.']
    return dict(titulo=decision,valor=fmt(estadistico),unidad=f'Estadístico {nombre}',pasos=pasos,
                conclusion=conclusion,aviso=' '.join(avisos),pvalor=pvalor,estadistico=estadistico,rechaza=rechaza,
                grafico=dict(tipo='hipotesis',nombre=nombre,gl=gl,cola=cola,alpha=alpha,criticos=criticos,estadistico=estadistico))


def interpolar(x1,y1,x2,y2,x):
    if x1==x2: raise ValueError('Los dos valores de X deben ser distintos.')
    return y1+(y2-y1)*(x-x1)/(x2-x1)


def interpolacion(d):
    """Interpolación lineal directa/inversa o bilineal en un rectángulo."""
    modo=d.get('modo','simple')
    x1=numero(d,'x1');x2=numero(d,'x2');x=numero(d,'x')
    if modo=='doble':
        y1=numero(d,'y1');y2=numero(d,'y2');y=numero(d,'y')
        z11=numero(d,'z11');z21=numero(d,'z21');z12=numero(d,'z12');z22=numero(d,'z22')
        a=interpolar(x1,z11,x2,z21,x);b=interpolar(x1,z12,x2,z22,x)
        valor=interpolar(y1,a,y2,b,y)
        pasos=['Primero se interpola en X sobre cada fila.',f'Fila y₁: zA = {fmt(a)}.',f'Fila y₂: zB = {fmt(b)}.',
               'Después se interpola entre las dos filas: z = zA + (zB−zA)(y−y₁)/(y₂−y₁).',f'z = {fmt(valor)}.']
        fuera=not(min(x1,x2)<=x<=max(x1,x2) and min(y1,y2)<=y<=max(y1,y2))
        grafico=dict(tipo='doble',x1=x1,x2=x2,y1=y1,y2=y2,x=x,y=y,z11=z11,z21=z21,z12=z12,z22=z22,valor=valor)
    else:
        y1=numero(d,'y1');y2=numero(d,'y2')
        if modo=='inversa':x1,y1,x2,y2=y1,x1,y2,x2
        valor=interpolar(x1,y1,x2,y2,x)
        pasos=['y = y₁ + (y₂−y₁)(x−x₁)/(x₂−x₁).',f'y = {fmt(y1)} + ({fmt(y2)}−{fmt(y1)})({fmt(x)}−{fmt(x1)})/({fmt(x2)}−{fmt(x1)}).',f'Resultado = {fmt(valor)}.']
        if modo=='inversa':pasos.insert(0,'Se intercambian X e Y para estimar X a partir de Y.')
        fuera=not min(x1,x2)<=x<=max(x1,x2)
        grafico=dict(tipo='lineal',x1=x1,y1=y1,x2=x2,y2=y2,x=x,valor=valor,inversa=modo=='inversa')
    return dict(titulo='Valor estimado',valor=fmt(valor),unidad='Interpolación',pasos=pasos,
                conclusion='El valor solicitado está fuera del intervalo: el resultado es una extrapolación.' if fuera else 'El valor solicitado se encuentra dentro del intervalo de los datos.',
                aviso='La interpolación supone variación lineal entre los puntos conocidos.',grafico=grafico)
