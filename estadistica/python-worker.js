// Este puente solo mueve datos. Las fórmulas, decisiones y gráficos están en Python.
const VERSION = '0.27.7';
let python;
async function iniciar() {
  postMessage({tipo:'estado',texto:'Descargando el motor de Python…'});
  importScripts(`https://cdn.jsdelivr.net/pyodide/v${VERSION}/full/pyodide.js`);
  python = await loadPyodide({indexURL:`https://cdn.jsdelivr.net/pyodide/v${VERSION}/full/`});
  postMessage({tipo:'estado',texto:'Preparando estadística y gráficos. La primera carga puede tardar…'});
  await python.loadPackage(['scipy','matplotlib','jinja2']);
  python.FS.mkdirTree('/home/pyodide/templates');
  for (const archivo of ['calculos.py','graficos.py','formularios.py','web.py','templates/index.html']) {
    const respuesta=await fetch(new URL(archivo,self.location.href),{cache:'no-cache'});
    if(!respuesta.ok)throw new Error(`No se pudo cargar ${archivo}`);
    python.FS.writeFile('/home/pyodide/'+archivo,await respuesta.text());
  }
  await python.runPythonAsync('import os\nos.chdir("/home/pyodide")\nfrom web import responder');
  postMessage({tipo:'listo'});
}
self.onmessage=async ({data})=>{
  try {
    if(data.tipo==='iniciar'){await iniciar();return;}
    if(data.tipo==='renderizar'){
      python.globals.set('pedido_json',JSON.stringify(data.pedido));
      const html=await python.runPythonAsync('responder(pedido_json)');
      postMessage({tipo:'pagina',html,id:data.id});
    }
  } catch(error) {
    postMessage({tipo:'error',texto:error.message||String(error),id:data.id});
  }
};
