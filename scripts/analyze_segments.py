"""Segmentación descriptiva del test congelado y cotejo de evidencias por entorno."""
import csv
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def score(rows):
    tn=fp=fn=tp=0
    for row in rows:
        y=int(row['y']); pred=float(row['SVM_calibrada'])>=.20
        tn+=int(y==0 and not pred); fp+=int(y==0 and pred)
        fn+=int(y==1 and not pred); tp+=int(y==1 and pred)
    return {'n':len(rows),'negative_count':tp+fn,'predicted_negative_count':tp+fp,
            'TN':tn,'FP':fp,'FN':fn,'TP':tp,'errors':fp+fn,
            'recall':tp/(tp+fn) if tp+fn else None,
            'precision':tp/(tp+fp) if tp+fp else None}
def main():
    src=ROOT/'datos/predicciones_test.csv'
    with src.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    for row in rows:row['length']=len(re.findall(r'\b\w+\b',row['texto']))
    lengths=[('1–15',lambda r:r['length']<=15),('16–30',lambda r:16<=r['length']<=30),('31 o más',lambda r:r['length']>=31)]
    by_length=[{'segment':name,**score([r for r in rows if test(r)])} for name,test in lengths]
    ranges=[('[0, 0.10)',0,.10,'No priorizo sólo por esta salida; leo el contexto y mantengo controles humanos.'),
            ('[0.10, 0.20)',.10,.20,'Reviso el contexto si hay otros indicios; no altero el umbral ni descarto riesgo.'),
            ('[0.20, 0.50)',.20,.50,'Prioriza lectura humana; contrasto la noticia con la fuente antes de cualquier decisión.'),
            ('[0.50, 1]',.50,1.0000001,'Prioriza lectura humana; una probabilidad alta tampoco autoriza una orden ni garantiza acierto.')]
    bands=[]
    for name,low,high,action in ranges:
        group=[r for r in rows if low<=float(r['SVM_calibrada'])<high];n=len(group);negative=sum(int(r['y']) for r in group)
        bands.append({'band':name,'n':n,'actual_negative':negative,'negative_fraction':negative/n if n else None,'action':action})
    environments=[]
    for env in ['host_local_sin_docker','docker_local','docker_ci','ubuntu_limpio']:
        path=ROOT/f'evidencias/regresion_{env}.json'
        if not path.exists():
            environments.append({'environment':env,'status':'sin medición completa disponible','max_absolute_error':None,'matrix':None,'total_seconds':None});continue
        d=json.loads(path.read_text());environments.append({'environment':env,'status':'medido','source':str(path.relative_to(ROOT)),
            'evidence_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'n':d['n'],'max_absolute_error':d['max_error_absoluto'],
            'matrix':d['confusion_TN_FP_FN_TP'],'total_seconds':d['segundos_total']})
    assert sum(x['n'] for x in by_length)==len(rows)==sum(x['n'] for x in bands)
    assert sum(x['errors'] for x in by_length)==score(rows)['errors']
    result={'source':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'threshold':.20,'n':len(rows),'length_definition':r'Coincidencias de \b\w+\b; tramos fijos descriptivos, no optimizados.',
            'length_segments':by_length,'probability_bands':bands,'environments':environments,
            'limitations':'Test retrospectivo; segmentos pequeños, sin intervalos ni prueba de diferencias entre segmentos. Tiempos de entornos distintos no constituyen benchmark controlado. No cambia el umbral ni el modelo.'}
    (ROOT/'evidencias/analisis_segmentos.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    def pct(v):return 'No definido' if v is None else f'{100*v:.2f} %'
    text='## Comportamiento por segmentos\n\nDefiní tres tramos fijos de longitud: 1–15, 16–30 y 31 o más unidades léxicas (`\\b\\w+\\b`). Son descripciones del test; no se eligieron para maximizar métricas. Precisión es acierto entre alertas; recall es detección entre noticias realmente negativas. Un denominador cero se informa como no definido.\n\n'
    text+='| Longitud | n | Negativas | Precisión | Recall | FP | FN | Errores |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
    for d in by_length:text+=f"| {d['segment']} | {d['n']} | {d['negative_count']} | {pct(d['precision'])} | {pct(d['recall'])} | {d['FP']} | {d['FN']} | {d['errors']} |\n"
    text+='\nNo interpreto las diferencias entre tramos como significativas: sus tamaños y números de negativas varían. Uso esta lectura para identificar dónde revisar errores, no para cambiar el modelo con el test.\n\n### Franjas operativas\n\nLos extremos inferiores son inclusivos y los superiores exclusivos, salvo 1.00. La fracción negativa observada es una frecuencia retrospectiva, no una probabilidad garantizada para una noticia futura.\n\n| Probabilidad | Noticias | Negativas reales | Fracción negativa | Acción de revisión humana |\n|---|---:|---:|---:|---|\n'
    for d in bands:text+=f"| {d['band']} | {d['n']} | {d['actual_negative']} | {pct(d['negative_fraction'])} | {d['action']} |\n"
    text+='\n### Consistencia entre entornos\n\nLa matriz se presenta como TN, FP, FN, TP. Cada tiempo corresponde a una corrida de 452 solicitudes en su entorno; no comparo velocidad sin igualar hardware, carga y protocolo.\n\n| Entorno | Error absoluto máximo | Matriz TN FP FN TP | Tiempo total s | Evidencia |\n|---|---:|---|---:|---|\n'
    for d in environments:
        if d['status']!='medido':text+=f"| {d['environment']} | No medido | No disponible | No medido | {d['status']} |\n"
        else:text+=f"| {d['environment']} | {d['max_absolute_error']:.6g} | {', '.join(map(str,d['matrix']))} | {d['total_seconds']:.6f} | {d['source']} |\n"
    text+='\nComo banquero, confío en que la aplicación reproduce el artefacto evaluado; no convierto esa consistencia en confianza ciega sobre cada noticia. Reviso también las alertas con probabilidad alta y no considero una probabilidad baja como ausencia de riesgo. La IA no sustituye el criterio del banquero; lo aumenta. Fuente reproducible: scripts/analyze_segments.py y evidencias/analisis_segmentos.json.\n'
    (ROOT/'documentos/Analisis_segmentos.md').write_text(text)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
