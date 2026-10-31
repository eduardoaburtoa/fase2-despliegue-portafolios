"""Análisis retrospectivo reproducible; no carga ni modifica el modelo."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'datos/predicciones_test.csv';d=pd.read_csv(p);s=d.SVM_calibrada
base=s.ge(.20)
result={'source':'datos/predicciones_test.csv','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'n':len(d),'production_threshold':.20,'boundary_definition':'0.19 <= p <= 0.21 (banda descriptiva, no intervalo de confianza)','near_boundary_count':int(s.between(.19,.21).sum()),'threshold_sensitivity':[],'errors':{}}
for t in [.19,.20,.21]:
 pred=s.ge(t)
 result['threshold_sensitivity'].append({'threshold':t,'changed_vs_020':int((pred!=base).sum()),'alerts':int(pred.sum()),'TN':int(((d.y==0)&~pred).sum()),'FP':int(((d.y==0)&pred).sum()),'FN':int(((d.y==1)&~pred).sum()),'TP':int(((d.y==1)&pred).sum()),'changed_ids':d.loc[pred!=base,'id'].tolist()})
for name,mask in [('false_negative',(d.y==1)&~base),('false_positive',(d.y==0)&base)]:
 result['errors'][name]=d.loc[mask,['id','texto','etiqueta','y','SVM_calibrada']].to_dict('records')
counts,edges=np.histogram(s,bins=np.linspace(0,1,21));result['histogram']={'counts':counts.tolist(),'edges':edges.tolist()}
r=json.loads((ROOT/'evidencias/regresion_docker_local.json').read_text());result['latency']={'source':'evidencias/regresion_docker_local.json','total_seconds':r['segundos_total'],'amortized_ms_per_request':1000*r['segundos_total']/r['n'],'scope':'Promedio amortizado del recorrido completo; no latencias individuales ni percentiles.'}
(ROOT/'evidencias/comportamiento_modelo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
ax.hist([s[d.y==0],s[d.y==1]],bins=edges,stacked=True,color=['#004481','#2DCCCD'],label=['No negativa (391)','Negativa (61)'])
ax.axvline(.2,color='#B92A45',linewidth=2,label='Umbral operativo 0.20');ax.axvspan(.19,.21,color='#B92A45',alpha=.14)
ax.set(xlabel='Probabilidad de noticia negativa',ylabel='Número de noticias',title='Distribución retrospectiva de las 452 noticias');ax.legend();ax.spines[['top','right']].set_visible(False)
fig.savefig(ROOT/'evidencias/distribucion_probabilidades.png',dpi=180);plt.close(fig)
print(json.dumps({k:v for k,v in result.items() if k not in ['errors','histogram']},ensure_ascii=False,indent=2))
for k,v in result['errors'].items():print(k,json.dumps(v[:3],ensure_ascii=False))
