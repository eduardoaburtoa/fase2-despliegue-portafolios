# Adaptador Cloud Run

`cloudrun_web.py` agrega un proxy HTTP de loopback para que el cliente original de Streamlit permanezca intacto. El proxy obtiene un ID token del metadata server con audience igual a la URL de la API e incluye Authorization: Bearer junto a X-API-Key. La cuenta de servicio web debe tener roles/run.invoker sobre la API.

No basta con `--no-allow-unauthenticated` y una API key: IAM rechazaría la llamada antes de que FastAPI la recibiera. El adaptador resuelve esa separación de controles. Es configuración preparada para Cloud Run; no se afirma una ejecución cloud de este adaptador sin evidencia.

El Dockerfile principal, el clasificador, el umbral y las 23 pruebas originales no cambian. La imagen web derivada se construye con deploy/cloudrun.Dockerfile. El manual contiene los comandos.
