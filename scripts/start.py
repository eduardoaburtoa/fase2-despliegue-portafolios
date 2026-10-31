import os,sys
service=os.environ.get('SERVICE','api')
port=os.environ.get('PORT','8000' if service=='api' else '8501')
if service=='api':args=[sys.executable,'-m','uvicorn','backend.main:app','--host','0.0.0.0','--port',port]
elif service=='web':args=[sys.executable,'-m','streamlit','run','frontend/app.py','--server.address=0.0.0.0','--server.port='+port]
else:raise SystemExit('SERVICE debe ser api o web')
os.execv(sys.executable,args)
