# Cierre de revisión · Fase II · 1.1.0

| Brecha | Estado | Evidencia y alcance |
|---|---|---|
| A · Arquitectura e integración | Resuelta | Figura 1 en ambos documentos; contrato de cinco endpoints y ejemplos reales en [ejemplos_api.json](../evidencias/ejemplos_api.json). El hash se verifica al arrancar; `/health` es público. |
| B · Comportamiento del modelo | Resuelta | [Análisis reproducible](../evidencias/comportamiento_modelo.json), histograma, errores concretos, sensibilidad 0.19/0.20/0.21. Se conserva el umbral operativo 0.20. |
| C · Replicabilidad | Resuelta en laboratorio | [Bitácora](../evidencias/replicabilidad.json) registra el fallo inicial y la corrección: Ubuntu limpio, daemon aislado, construcción, servicios healthy, 23 pruebas y 452 predicciones. Tres rutas cloud documentadas, ninguna desplegada. |
| D · Herramientas documentales | Resuelta | [OpenAPI](openapi.json), [referencia HTML](api-reference.html) y script exportador. Descargar el HTML para navegarlo; requiere internet para Swagger UI. |
| E · Continuidad | Resuelta | README y manual conservan las cifras suministradas de Fase I y delimitan Fase III. La ejecución técnica no demuestra el ROI proyectado. |
| F · Formatos y acceso | Resuelta | Markdown, Word, PDF y Google Docs; lectura anónima de ambos documentos comprobada en incógnito. [Evidencia](../evidencias/documentos_verificacion.json). |
| G · Higiene y capturas | Parcial | Ubuntu 24.04, acciones actualizadas, topics y CHANGELOG 1.1.0; Compose healthy y escenario Streamlit capturados. Falta la captura nueva de Swagger: el control automático de acceso rechazó abrir localhost:8000. Se conserva el contrato y las respuestas reales; no se inventó una captura. |

El modelo, su umbral, la lógica principal y las 23 pruebas originales se conservan. Las advertencias sobre idioma inglés, evaluación retrospectiva, meta conjunta no alcanzada, datos ficticios y costos didácticos permanecen en los documentos.

## Reproducir la validación local

Requisitos: Git, Python 3.12 y Docker con Compose funcionando; puertos locales 8000 y 8501 disponibles. En Ubuntu sin Docker, seguir primero el manual de instalación y sus requisitos de systemd.

```bash
git clone https://github.com/eduardoaburtoa/fase2-despliegue-portafolios.git
cd fase2-despliegue-portafolios
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
python -c "import secrets,pathlib; pathlib.Path('.env').write_text('API_TOKEN='+secrets.token_urlsafe(32)+'\n')"
chmod 600 .env
set -a
source .env
set +a
docker compose up --build -d --wait --wait-timeout 180
docker compose ps
python -m pytest pruebas -q --junitxml=evidencias/pytest-reproduccion.xml
TEST_ENV=reproduccion python scripts/smoke.py
TEST_ENV=reproduccion python scripts/regression_http.py
docker compose exec -T web python -c "from frontend.client import call; print(call('/v1/model')['sha256'])"
python scripts/analyze_behavior.py
python scripts/export_docs.py
docker compose down
```

Estas ejecuciones actualizan evidencias locales; no confundirlas con las mediciones históricas publicadas. La bitácora completa del laboratorio está en [Reproduccion_Ubuntu.md](Reproduccion_Ubuntu.md).
