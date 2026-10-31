"""Genera contrato y ejemplos reales sin alterar el modelo ni la API."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.main import app
from fastapi.testclient import TestClient
os.environ.setdefault('API_TOKEN','ejemplo-local-documentacion-no-productivo')
headers={'X-API-Key':os.environ['API_TOKEN']}
cases=[('GET','/health',None),('GET','/v1/model',None),('POST','/v1/predict',{'texto':'The company reported a decline in operating profit.','idioma':'en'}),('GET','/v1/clients',None),('POST','/v1/scenario',{'cliente_id':'C001','proporcion':.35,'mejora_anual_pp':3,'meses':12,'gastos_adicionales_anuales_pp':0,'perfil_destino':'Moderado'})]
with TestClient(app) as client:
 schema=client.get('/openapi.json').json();examples=[]
 for method,path,payload in cases:
  response=client.request(method,path,json=payload,headers=headers);response.raise_for_status()
  examples.append({'method':method,'path':path,'request':payload,'status':response.status_code,'response':response.json()})
(ROOT/'documentos/openapi.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n')
(ROOT/'evidencias/ejemplos_api.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n')
html='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Vértice AI · Contrato API</title></head><body><header style="padding:20px;font-family:Arial;color:#004481"><h1>Referencia de la API de Fase II</h1><p>Contrato generado por FastAPI. Versión de aplicación 1.0.0; documentación de entrega 1.1.0. No incluye claves. Requiere Internet para cargar Swagger UI.</p></header><div id="swagger-ui"></div><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"><script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script><script>window.onload=()=>SwaggerUIBundle({spec:SPEC,dom_id:'#swagger-ui',supportedSubmitMethods:[]});</script></body></html>'''
(ROOT/'documentos/api-reference.html').write_text(html.replace('SPEC',json.dumps(schema,ensure_ascii=False).replace('</','<\\/')))
print('Contrato y cinco ejemplos generados. No contiene credenciales.')
