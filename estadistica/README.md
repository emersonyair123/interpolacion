# Estadística Lab UNAJ · versión para GitHub Pages

Autor: Emerson Yair Peralta Gonzales · Software y Sistemas.

Esta versión funciona en el navegador de celulares y computadoras. No necesita que
la laptop esté encendida ni instalar Python. La primera carga descarga Pyodide y
sus bibliotecas desde jsDelivr; mantén conexión a internet y espera «Listo».
El código y los cálculos se ejecutan en el dispositivo, dentro de un Web Worker.
No se envían los datos ingresados a un servidor de cálculo.

## Funciones

- Tamaño de muestra para medias/proporciones, población finita o desconocida.
- Hipótesis Z, t, Welch, una/dos proporciones; tres alternativas y valor p.
- Gráficos en Matplotlib y procedimiento explicado en Python.
- Interpolación simple, inversa y doble.
- Descarga de gráficos PNG e impresión/guardar PDF según el navegador.

## Qué archivo modificar

| Archivo | Responsabilidad |
|---|---|
| calculos.py | Fórmulas, validaciones, decisiones y explicación |
| graficos.py | Curvas, regiones críticas y gráficos de interpolación |
| formularios.py | Autor, etiquetas y ejemplos iniciales |
| web.py | Une los módulos y genera HTML con Jinja2 |
| templates/index.html | Presentación de formularios y resultados |
| static/estilos.css | Diseño y adaptación al celular |
| python-worker.js | Carga Python y sus bibliotecas; no contiene fórmulas |
| navegador.js | Navegación y envío de datos al trabajador Python |
| index.html | Pantalla inicial mientras carga Python |

La lógica sigue en Python; JavaScript solo conecta el navegador con Pyodide.
El antiguo servidor Flask no se ejecuta en GitHub Pages. web.py lo sustituye como
adaptador, ejecutándose en el propio navegador. La versión local de laptop sigue
siendo un proyecto separado.

Para cambiar tu nombre, edita AUTOR en formularios.py; para cambiar las fórmulas,
edita calculos.py. Guarda el commit y espera la publicación de Pages. Actualiza
la página; las fuentes Python se descargan evitando caché al iniciar.
El logo se encuentra en static/logo_unaj.png; puedes reemplazar ese archivo.

## Ejemplos para explicar

- Media, confianza 95%, desviación 4000 y error 200: n=1537.
- Proporción, confianza 99%, p=0,5, error 0,02, Z a tres decimales: n=4148.
  Con Z exacta: n=4147. La diferencia es el redondeo del cuantil antes del techo.
- Hipótesis de proporción: n=500, éxitos=300, p₀=0,65, α=0,05, alternativa menor:
  Z≈−2,34404 y p≈0,009538; se rechaza H₀.

## Ejecución local de esta versión web

Desde esta carpeta ejecuta `python -m http.server 8000` y abre
http://localhost:8000. No abras index.html directamente como archivo: el navegador
necesita HTTP para cargar el trabajador y los archivos Python.

## Compatibilidad y límites

Necesita un navegador moderno con WebAssembly y Web Workers, y memoria suficiente
para NumPy, SciPy y Matplotlib. La primera carga puede tardar y consumir datos.
No es una APK ni garantiza uso sin internet. Si la carga falla, pulsa Reintentar.
La app no incluye pruebas pareadas, exactas, ANOVA ni historial persistente.

Logo de la UNAJ: https://portal.unaj.edu.pe/themes/custom/modins_sub/logo.png
Proyecto académico; no es una aplicación oficial de la universidad.
Pyodide: https://pyodide.org/en/0.27.7/usage/index.html
Versión fijada: 0.27.7 para que el entorno sea reproducible.
