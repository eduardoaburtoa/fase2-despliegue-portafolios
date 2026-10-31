"""Adaptador de despliegue: IAM entre servicios sin cambiar frontend/client.py.
El proxy sólo escucha en loopback y no registra encabezados ni texto.
"""
import os,sys,json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import requests
UPSTREAM=os.environ['CLOUD_RUN_API_URL'].rstrip('/')
if not UPSTREAM.startswith('https://'):raise RuntimeError('CLOUD_RUN_API_URL requiere HTTPS')
ALLOWED={'/health','/v1/model','/v1/predict','/v1/clients','/v1/scenario'}
def token():
    r=requests.get('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity',params={'audience':UPSTREAM,'format':'full'},headers={'Metadata-Flavor':'Google'},timeout=5)
    r.raise_for_status();return r.text
class Proxy(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def relay(self):
        if self.path not in ALLOWED:self.send_error(404);return
        n=int(self.headers.get('Content-Length','0'))
        if n<0 or n>20000:self.send_error(413);return
        try:
            r=requests.request(self.command,UPSTREAM+self.path,data=self.rfile.read(n) if n else None,headers={'Authorization':'Bearer '+token(),'X-API-Key':os.environ['API_TOKEN'],'Content-Type':'application/json'},timeout=(5,20),allow_redirects=False)
            self.send_response(r.status_code);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(r.content)
        except requests.RequestException:
            self.send_response(502);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps({'detail':'No se pudo autenticar o conectar con la API privada'}).encode())
    do_GET=relay
    do_POST=relay
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',8081),Proxy)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    os.environ['API_URL']='http://127.0.0.1:8081'
    from streamlit.web import cli
    sys.argv=['streamlit','run','frontend/app.py','--server.address=0.0.0.0','--server.port='+os.environ.get('PORT','8080')]
    sys.exit(cli.main())
