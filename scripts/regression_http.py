"""Verifica las 452 predicciones mediante HTTP real; no reentrena."""
import os,json,time
from pathlib import Path
import pandas as pd,requests
from sklearn.metrics import confusion_matrix,accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
base=os.getenv('API_URL','http://127.0.0.1:8000');h={'X-API-Key':os.environ['API_TOKEN']}
d=pd.read_csv('datos/predicciones_test.csv');scores=[];start=time.perf_counter()
for row in d.itertuples():
    res=requests.post(base+'/v1/predict',headers=h,json={'texto':row.texto},timeout=20);res.raise_for_status();scores.append(res.json()['probabilidad_negativa'])
error=max(abs(a-b) for a,b in zip(scores,d.SVM_calibrada));assert error<1e-12
pred=[p>=.2 for p in scores]
out={'entorno':os.getenv('TEST_ENV','docker_local'),'n':len(d),'max_error_absoluto':error,'segundos_total':time.perf_counter()-start,'confusion_TN_FP_FN_TP':confusion_matrix(d.y,pred).ravel().tolist(),'accuracy':accuracy_score(d.y,pred),'precision':precision_score(d.y,pred),'recall':recall_score(d.y,pred),'f1':f1_score(d.y,pred),'auc':roc_auc_score(d.y,scores)}
Path('evidencias/regresion_'+out['entorno']+'.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
