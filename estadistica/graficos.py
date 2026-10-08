"""Gráficos calculados completamente en Python con Matplotlib."""
import base64
from io import BytesIO
import numpy as np
from scipy.stats import norm, t
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

AZUL = '#174b70'
DORADO = '#c59235'
ROJO = '#be4351'


def crear_grafico(g):
    fig=Figure(figsize=(8.4,4.6),layout='constrained',facecolor='#ffffff')
    FigureCanvasAgg(fig)
    ax=fig.add_subplot(111)
    if g['tipo'] in ('hipotesis','confianza'):
        if g['tipo']=='confianza':
            dist=norm;lim=4
            criticos=[-g['z'],g['z']]
        else:
            dist=t(df=g['gl']) if g['gl'] is not None else norm
            criticos=g['criticos']
            lim=max(4,abs(dist.ppf(.001)),abs(g['estadistico'])*1.15,max(abs(c) for c in criticos)*1.15)
        # Malla densa cerca del origen, incluso con un estadístico muy lejano.
        x=np.unique(np.r_[np.linspace(-lim,lim,1800),np.linspace(-4,4,1200)])
        y=dist.pdf(x)
        ax.plot(x,y,color=AZUL,lw=2)
        if g['tipo']=='confianza':
            ax.fill_between(x,y,where=(x>=criticos[0])&(x<=criticos[1]),color=AZUL,alpha=.2,label=f"Área central: {g['confianza']:.1%}")
            ax.set_title(f"Confianza y límites Z · n = {g['n']}")
            ax.set_xlabel('Z estandarizado (no representa el tamaño de muestra)')
        else:
            cola=g['cola']
            mask=(x<=criticos[0]) if cola=='menor' else (x>=criticos[-1])
            if cola=='diferente':mask=(x<=criticos[0])|(x>=criticos[-1])
            ax.fill_between(x,y,where=mask,color=ROJO,alpha=.4,label=f"Rechazo de H₀ · α = {g['alpha']}")
            ax.axvline(g['estadistico'],color=DORADO,lw=2.5,label=f"Calculado: {g['estadistico']:.4f}")
            ax.set_title('Distribución bajo la hipótesis nula')
            ax.set_xlabel(g['nombre'])
        for c in criticos:ax.axvline(c,color=ROJO,ls='--',label=f'Crítico: {c:.4f}')
        ax.set_ylabel('Densidad');ax.legend(fontsize=8,loc='upper right')
    elif g['tipo']=='lineal':
        x1,y1,x2,y2,x,v=[g[k] for k in ('x1','y1','x2','y2','x','valor')]
        lo=min(x1,x2,x);hi=max(x1,x2,x);xx=np.linspace(lo,hi,100)
        ax.plot(xx,y1+(y2-y1)*(xx-x1)/(x2-x1),color=AZUL,label='Modelo lineal')
        ax.scatter([x1,x2],[y1,y2],s=65,color=AZUL,label='Datos conocidos')
        ax.scatter([x],[v],s=90,color=DORADO,zorder=3,label=f'Estimación: {v:.5g}')
        ax.axvline(x,color=DORADO,ls=':',alpha=.6)
        ax.set_xlabel('Y conocida' if g['inversa'] else 'X');ax.set_ylabel('X estimada' if g['inversa'] else 'Y')
        ax.set_title('Interpolación lineal');ax.legend()
    else:
        xs=np.linspace(min(g['x1'],g['x2'],g['x']),max(g['x1'],g['x2'],g['x']),80)
        ys=np.linspace(min(g['y1'],g['y2'],g['y']),max(g['y1'],g['y2'],g['y']),80)
        X,Y=np.meshgrid(xs,ys)
        u=(X-g['x1'])/(g['x2']-g['x1']);v=(Y-g['y1'])/(g['y2']-g['y1'])
        Z=(1-u)*(1-v)*g['z11']+u*(1-v)*g['z21']+(1-u)*v*g['z12']+u*v*g['z22']
        mapa=ax.contourf(X,Y,Z,levels=16,cmap='Blues');fig.colorbar(mapa,ax=ax,label='Z estimada')
        ax.scatter([g['x1'],g['x2'],g['x1'],g['x2']],[g['y1'],g['y1'],g['y2'],g['y2']],c=AZUL,edgecolors='white',s=80)
        ax.scatter(g['x'],g['y'],color=DORADO,edgecolors='black',s=90,label=f"z = {g['valor']:.5g}")
        ax.set(xlabel='X',ylabel='Y',title='Interpolación doble · mapa de valores');ax.legend()
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.15)
    archivo=BytesIO();fig.savefig(archivo,format='png',dpi=140)
    return base64.b64encode(archivo.getvalue()).decode('ascii')
