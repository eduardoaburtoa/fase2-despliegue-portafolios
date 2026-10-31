"""Mide la regresión HTTP en host sin Docker, con servidor temporal en loopback."""
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parents[1]
def main():
    # Puerto efímero sólo para prueba local; no expone el servidor en la red.
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    env=dict(os.environ, API_TOKEN=secrets.token_urlsafe(32), API_URL=f'http://127.0.0.1:{port}', TEST_ENV='host_local_sin_docker')
    log=ROOT/'evidencias/host_regression_server.log'
    with log.open('w') as stream:
        server=subprocess.Popen([sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(port),'--no-access-log'],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                if server.poll() is not None:raise RuntimeError('El servidor de prueba no pudo arrancar; revisar log local.')
                try:
                    if requests.get(env['API_URL']+'/health',timeout=1).ok:break
                except requests.RequestException:pass
                time.sleep(.1)
            else:raise TimeoutError('API de prueba sin salud después de 30 segundos')
            subprocess.run([sys.executable,'scripts/regression_http.py'],cwd=ROOT,env=env,check=True)
        finally:
            server.terminate()
            try:server.wait(timeout=10)
            except subprocess.TimeoutExpired:server.kill();server.wait()
if __name__=='__main__':main()
