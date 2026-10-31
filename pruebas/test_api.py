import json,hashlib,os
from pathlib import Path
import numpy as np,pandas as pd,pytest
from fastapi.testclient import TestClient
from backend.main import app,ROOT
TOKEN='token-solo-para-pruebas-locales'
@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv('API_TOKEN',TOKEN)
    with TestClient(app) as c:yield c
@pytest.fixture
def headers():return {'X-API-Key':TOKEN}
def test_health_y_contrato(api,headers):
    assert api.get('/health').json()['model_ready']
    spec=api.get('/openapi.json').json()
    assert {'/v1/predict','/v1/scenario','/v1/clients'}<=set(spec['paths'])
    assert api.get('/v1/model',headers=headers).json()['threshold']==.2
@pytest.mark.parametrize('key',['','incorrecta'])
def test_auth(api,key):assert api.get('/v1/clients',headers={'X-API-Key':key}).status_code==401
@pytest.mark.parametrize('payload',[{}, {'texto':''},{'texto':'   '},{'texto':'1234'},{'texto':'x'*4001},{'texto':'noticia','idioma':'es'},{'texto':'profits','extra':True},{'texto':None},{'texto':'zzzxqwwqq'}])
def test_entradas_extremas(api,headers,payload):
    assert api.post('/v1/predict',headers=headers,json=payload).status_code==422

def test_modelo_452_predicciones(api,headers):
    data=pd.read_csv(ROOT/'datos/predicciones_test.csv');observed=[]
    for row in data.itertuples():
        r=api.post('/v1/predict',headers=headers,json={'texto':row.texto,'idioma':'en'})
        assert r.status_code==200,r.text
        p=r.json();observed.append(p['probabilidad_negativa'])
        assert p['priorizar_revision']==(p['probabilidad_negativa']>=.2)
    np.testing.assert_allclose(observed,data.SVM_calibrada,rtol=0,atol=1e-12)
    pred=np.array(observed)>=.2;y=data.y.to_numpy()
    assert (int(((y==0)&~pred).sum()),int(((y==0)&pred).sum()),int(((y==1)&~pred).sum()),int(((y==1)&pred).sum()))==(366,25,10,51)

def test_clientes_y_costos(api,headers):
    clients=api.get('/v1/clients',headers=headers).json()['clientes'];assert len(clients)==150
    assert all(5e6<=c['posicion_mxn']<=20e6 for c in clients)
    c=clients[0];payload=dict(cliente_id=c['cliente_id'],proporcion=.35,mejora_anual_pp=3,meses=12,gastos_adicionales_anuales_pp=0,perfil_destino=c['perfil_riesgo'])
    r=api.post('/v1/scenario',headers=headers,json=payload).json();amount=c['posicion_mxn']*.35
    assert r['corretaje_supuesto_mxn']==pytest.approx(amount*.02)
    assert r['beneficio_incremental_supuesto_mxn']==pytest.approx(amount*.01)
    assert r['elegible_para_revision']
    payload['perfil_destino']='Agresivo' if c['perfil_riesgo']!='Agresivo' else 'Conservador'
    assert not api.post('/v1/scenario',headers=headers,json=payload).json()['elegible_para_revision']
    payload['perfil_destino']=c['perfil_riesgo'];payload['mejora_anual_pp']=-3
    assert not api.post('/v1/scenario',headers=headers,json=payload).json()['elegible_para_revision']
@pytest.mark.parametrize('field,value,code',[('cliente_id','C999',404),('proporcion',0,422),('proporcion',1.1,422),('meses',0,422),('meses',1.5,422),('gastos_adicionales_anuales_pp',-1,422)])
def test_escenarios_extremos(api,headers,field,value,code):
    p=dict(cliente_id='C001',proporcion=.35,mejora_anual_pp=3,meses=12,gastos_adicionales_anuales_pp=0,perfil_destino='Moderado');p[field]=value
    assert api.post('/v1/scenario',headers=headers,json=p).status_code==code

def test_falla_segura_sin_token(monkeypatch):
    monkeypatch.delenv('API_TOKEN',raising=False)
    with pytest.raises(RuntimeError,match='API_TOKEN'):
        with TestClient(app):pass
