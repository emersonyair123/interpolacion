// Navegación y estado de carga. No implementa ninguna fórmula estadística.
let worker, listo=false, ocupado=false, secuencia=0;
const aviso=document.createElement('div');
aviso.className='estado-motor';aviso.setAttribute('role','status');aviso.setAttribute('aria-live','polite');
const estado=document.createElement('span');
const reintentar=document.createElement('button');reintentar.textContent='Reintentar';reintentar.hidden=true;
aviso.append(estado,reintentar);document.body.append(aviso);
function mensaje(texto,error=false){estado.textContent=texto;aviso.classList.toggle('fallo',error);reintentar.hidden=!error;}
function bloquear(valor){ocupado=valor;document.querySelectorAll('form button[type="submit"]').forEach(b=>b.disabled=valor||!listo);}
function pedidoActual(){const q=new URLSearchParams(location.search);return {modulo:q.get('modulo')||'muestra',variante:q.get('variante')||''};}
function renderizar(datos){if(!listo||ocupado)return;bloquear(true);mensaje(datos?'Calculando y dibujando…':'Abriendo módulo…');worker.postMessage({tipo:'renderizar',id:++secuencia,pedido:{...pedidoActual(),datos,calcular:!!datos}});}
function iniciar(){
 if(worker)worker.terminate();listo=false;bloquear(true);mensaje('Iniciando Python. Mantén la conexión a internet durante la carga.');
 worker=new Worker('./python-worker.js');
 worker.onerror=()=>{bloquear(false);mensaje('No se pudo iniciar el motor. Comprueba la conexión y vuelve a intentar.',true);};
 worker.onmessage=({data})=>{
  if(data.tipo==='estado')mensaje(data.texto);
  if(data.tipo==='listo'){listo=true;bloquear(false);renderizar();}
  if(data.tipo==='pagina'){
   const pagina=new DOMParser().parseFromString(data.html,'text/html');
   document.querySelector('.layout').replaceWith(pagina.querySelector('.layout'));
   document.title=pagina.title;bloquear(false);mensaje('Listo · cálculos y gráficos en Python');
  }
  if(data.tipo==='error'){bloquear(false);mensaje('No se pudo completar: '+data.texto,true);}
 };
 worker.postMessage({tipo:'iniciar'});
}
reintentar.addEventListener('click',iniciar);
document.addEventListener('submit',event=>{
 if(!event.target.matches('form'))return;event.preventDefault();
 if(!listo){mensaje('Espera a que termine de cargar Python.');return;}
 renderizar(Object.fromEntries(new FormData(event.target)));
});
document.addEventListener('click',event=>{
 const a=event.target.closest('a[href^="?modulo="]');if(!a)return;
 event.preventDefault();if(ocupado)return;
 history.pushState(null,'',a.href);if(listo)renderizar();
});
window.addEventListener('popstate',()=>{if(listo&&!ocupado)renderizar();});
iniciar();
