"""Prueba HTTP real reutilizable en el host y en CI con Docker."""
import json,os,time,requests
from pathlib import Path
base=os.environ.get('API_URL','http://127.0.0.1:8000')
headers={'X-API-Key':os.environ['API_TOKEN']}
for i in range(60):
    try:
        if requests.get(base+'/health',timeout=2).status_code==200:break
    except requests.RequestException:pass
    time.sleep(1)
else:raise SystemExit('API no disponible')
r=requests.post(base+'/v1/predict',json={'texto':'The company reported a decline in operating profit.','idioma':'en'},headers=headers,timeout=20);r.raise_for_status()
assert r.json()['priorizar_revision']
assert requests.get(base+'/v1/clients',timeout=5).status_code==401
c=requests.get(base+'/v1/clients',headers=headers,timeout=5);c.raise_for_status();assert len(c.json()['clientes'])==150
result={'entorno':os.environ.get('TEST_ENV','host_local_sin_docker'),'fecha_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'health':True,'auth_401':True,'clientes':150,'prediccion':r.json()}
Path('evidencias').mkdir(exist_ok=True);Path('evidencias/smoke_'+result['entorno']+'.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
