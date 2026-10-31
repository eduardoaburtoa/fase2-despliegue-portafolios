# Cloud Run con API privada

Procedimiento preparado; requiere proyecto con facturación habilitada. No ejecutado en Google Cloud en esta revisión. Usa la misma API y una imagen web derivada para añadir identidad IAM sin modificar el frontend original.

```bash
export FASE2_PROJECT='MI_PROYECTO'
export FASE2_REGION='us-central1'
export FASE2_REG="$FASE2_REGION-docker.pkg.dev/$FASE2_PROJECT/vertice"
export FASE2_BASE="$FASE2_REG/api:1.1.0"
export FASE2_WEB="$FASE2_REG/web:1.1.0"
gcloud config set project "$FASE2_PROJECT"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create vertice --repository-format=docker --location="$FASE2_REGION"
gcloud auth configure-docker "$FASE2_REGION-docker.pkg.dev"
docker buildx build --platform linux/amd64 -t "$FASE2_BASE" --push .
docker buildx build --platform linux/amd64 -f deploy/cloudrun.Dockerfile \
  --build-arg BASE_IMAGE="$FASE2_BASE" -t "$FASE2_WEB" --push .
gcloud iam service-accounts create vertice-api
gcloud iam service-accounts create vertice-web
python3 -c "import secrets; print(secrets.token_urlsafe(32), end='')" | \
  gcloud secrets create vertice-api-token --data-file=-
for FASE2_SA in vertice-api vertice-web; do
  gcloud secrets add-iam-policy-binding vertice-api-token \
    --member="serviceAccount:$FASE2_SA@$FASE2_PROJECT.iam.gserviceaccount.com" \
    --role=roles/secretmanager.secretAccessor
done
gcloud run deploy vertice-api --image="$FASE2_BASE" \
  --region="$FASE2_REGION" --service-account="vertice-api@$FASE2_PROJECT.iam.gserviceaccount.com" \
  --no-allow-unauthenticated --port=8000 --set-env-vars=SERVICE=api \
  --set-secrets=API_TOKEN=vertice-api-token:1 --min-instances=0 --max-instances=1 \
  --memory=1Gi --cpu=1
export FASE2_API_URL="$(gcloud run services describe vertice-api --region="$FASE2_REGION" --format='value(status.url)')"
gcloud run services add-iam-policy-binding vertice-api --region="$FASE2_REGION" \
  --member="serviceAccount:vertice-web@$FASE2_PROJECT.iam.gserviceaccount.com" --role=roles/run.invoker
gcloud run deploy vertice-web --image="$FASE2_WEB" \
  --region="$FASE2_REGION" --service-account="vertice-web@$FASE2_PROJECT.iam.gserviceaccount.com" \
  --allow-unauthenticated --port=8080 --set-env-vars="CLOUD_RUN_API_URL=$FASE2_API_URL" \
  --set-secrets=API_TOKEN=vertice-api-token:1 --min-instances=0 --max-instances=1 \
  --memory=1Gi --cpu=1 --timeout=3600
```

Los nombres del ejemplo deben estar libres; si ya existen, revisar los recursos en vez de recrearlos. Cloud Run inyecta PORT según --port; el arranque de la API y del adaptador web lo respetan. El secreto se fija a la versión 1; una rotación exige desplegar ambos servicios con la nueva versión.

`--allow-unauthenticated` sólo se utiliza en web para que el docente pueda abrir la demostración en su navegador sin credenciales de Google Cloud. No es una obligación de Streamlit ni de Cloud Run: para un piloto privado se retira y se añade acceso autenticado. La API conserva IAM privado y X-API-Key. La pantalla pública permite usar el modelo a través de web; por tanto sólo se despliegan datos ficticios y no es una frontera de autorización bancaria.

El proxy local obtiene un ID token de la identidad vertice-web para la audiencia de la API. Una API key sola no satisface IAM. No se pone el secreto en Dockerfile, GitHub ni el navegador. La demostración pública no utiliza clientes reales y no ejecuta operaciones.

Para probar la API privada se necesita además un ID token autorizado en el cliente de prueba. scripts/smoke.py se conserva sin cambios y no implementa IAM: se usa contra la API pública de Render protegida con X-API-Key, o contra localhost. En Cloud Run se debe usar un cliente con Authorization Bearer y X-API-Key, además de comprobar la pantalla y los logs.
