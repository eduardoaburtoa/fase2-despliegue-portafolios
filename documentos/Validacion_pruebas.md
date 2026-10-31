# Validación y pruebas de Fase II

Eduardo Aburto Angulo · 31 de octubre de 2026 · Versión 1.1.0

## Conclusión y alcance

Comprobé que la API y Streamlit se comunican dentro de Docker y que el modelo conserva las predicciones históricas. La suite automatizada aprobó 23 pruebas; la regresión HTTP recorrió 452 noticias y obtuvo una diferencia máxima de 2.78 × 10⁻¹⁶ respecto al archivo de referencia, menor que la tolerancia de 10⁻¹². Ambos servicios alcanzaron estado healthy.

Esta conclusión acredita la integración y consistencia técnica del prototipo local. No equivale a una validación financiera, una prueba de carga ni un despliegue cloud completado. Como banquero Sr., mantengo la revisión humana: una alerta negativa no demuestra que migrar un fondo mejore el rendimiento.

## Arquitectura e integración

![Arquitectura de la solución](../evidencias/arquitectura.png)

Figura 1. Arquitectura de la solución: navegador, Streamlit, FastAPI y modelo conservado.

El navegador conversa con Streamlit; sólo el servidor Streamlit conoce la clave y llama a FastAPI por la red de Compose. Al iniciar la API, antes de aceptar peticiones, se verifica el SHA256 del modelo contra el manifiesto. Esa comprobación ocurre al arranque, no en cada noticia. El archivo conservado se carga únicamente si coincide.

Secuencia de una revisión: (1) el banquero escribe una noticia en inglés; (2) Streamlit envía POST a http://api:8000/v1/predict con X-API-Key; (3) FastAPI valida el esquema, la credencial y la presencia de vocabulario conocido; (4) el modelo ya verificado produce la probabilidad; (5) la API compara con 0.20; (6) la pantalla muestra probabilidad, prioridad y la leyenda de revisión humana. Un error de red se presenta de forma comprensible y no se sustituye por una predicción inventada.

| Ruta y método | Autenticación | Entrada | Salida | Errores previstos |
|---|---|---|---|---|
| GET /health | Pública | Ninguna | Estado y disponibilidad del modelo | 503 |
| GET /v1/model | X-API-Key | Ninguna | Manifiesto, hash y limitaciones | 401 |
| POST /v1/predict | X-API-Key | texto; idioma en | Probabilidad, umbral y aviso | 401, 422, 503 |
| GET /v1/clients | X-API-Key | Ninguna | 150 clientes ficticios | 401 |
| POST /v1/scenario | X-API-Key | Cliente, proporción, mejora, meses, gastos, perfil | Compatibilidad y beneficio supuesto | 401, 404, 422 |

La ruta de salud es pública; las cuatro rutas de negocio requieren clave. El contrato completo de campos y restricciones está en documentos/openapi.json. Los errores no convierten la API en un sistema de autorización de operaciones.

### Peticiones y respuestas observadas

Ejecuté los cinco casos con FastAPI TestClient y su ciclo de arranque real, sin alterar la lógica. evidencias/ejemplos_api.json conserva las respuestas completas. Los siguientes extractos seleccionan campos de esas respuestas; no se presentan como cuerpos completos. En una llamada HTTP real se añade X-API-Key desde el entorno, sin publicar su valor.

GET /health — HTTP 200.

```json
{
  "entrada": null,
  "salida_extracto": {
    "status": "ok",
    "model_ready": true,
    "version": "1.0.0"
  }
}
```

GET /v1/model — HTTP 200.

```json
{
  "entrada": null,
  "salida_extracto": {
    "sha256": "f48c7496d5a12bd15d535721e3e83c6ef895b1ae7eaccbe7f4f4c60705bb1916",
    "notice": "Priorizar revisión humana; no es orden de inversión ni predicción de rendimiento.",
    "joint_target_met": false
  }
}
```

POST /v1/predict — HTTP 200.

```json
{
  "entrada": {
    "texto": "The company reported a decline in operating profit.",
    "idioma": "en"
  },
  "salida_extracto": {
    "probabilidad_negativa": 0.3544057081827505,
    "umbral": 0.2,
    "priorizar_revision": true,
    "idioma_declarado": "en",
    "notice": "Priorizar revisión humana; no es orden de inversión ni predicción de rendimiento.",
    "model_sha256": "f48c7496d5a12bd15d535721e3e83c6ef895b1ae7eaccbe7f4f4c60705bb1916"
  }
}
```

GET /v1/clients — HTTP 200.

```json
{
  "entrada": null,
  "salida_extracto": {
    "simulados": true,
    "clientes": [
      {
        "cliente_id": "C001",
        "nombre": "Killer Croc",
        "arquetipo": "Villano",
        "perfil_riesgo": "Moderado",
        "posicion_mxn": 11858000,
        "fondo_actual": "BBVACR",
        "serie_actual": "P",
        "categoria_actual": "Fondos de Estrategias Pesos",
        "rend_1_anio_actual": 11.93,
        "clase_activo": "Deuda Corto Plazo",
        "meses_sin_revision": 6
      }
    ]
  }
}
```

POST /v1/scenario — HTTP 200.

```json
{
  "entrada": {
    "cliente_id": "C001",
    "proporcion": 0.35,
    "mejora_anual_pp": 3,
    "meses": 12,
    "gastos_adicionales_anuales_pp": 0,
    "perfil_destino": "Moderado"
  },
  "salida_extracto": {
    "simulado": true,
    "perfil_compatible": true,
    "monto_migrado_mxn": 4150299.9999999995,
    "mejora_supuesta_mxn": 124508.99999999999,
    "corretaje_supuesto_mxn": 83005.99999999999,
    "gastos_adicionales_mxn": 0.0,
    "beneficio_incremental_supuesto_mxn": 41503.0,
    "elegible_para_revision": true,
    "supuesto": "1 % compra + 1 % venta sobre el mismo nocional. Cálculo lineal, sin impuestos ni garantía. Gastos adicionales sólo si no están ya descontados del rendimiento. No equivale al ingreso neto del banco.",
    "notice": "Priorizar revisión humana; no es orden de inversión ni predicción de rendimiento."
  }
}
```


## Modelo y datos conservados

Uso SVM calibrada con umbral 0.20, procedente de la Actividad 6. El hash SHA256 del archivo es f48c7496d5a12bd15d535721e3e83c6ef895b1ae7eaccbe7f4f4c60705bb1916. La API verifica esa identidad al arrancar. No reentrené ni elegí un nuevo umbral sobre las noticias de prueba.

El conjunto retrospectivo contiene 452 noticias en inglés: 61 negativas y 391 no negativas. El resultado binario positivo es noticia negativa. El vocabulario TF-IDF y el modelo se cargan del artefacto validado; no se ajustan a lo que el usuario escribe. El control de idioma depende de la declaración en; no es un detector de idioma. Si no hay ningún término conocido, la API rechaza el texto.

Los 150 personajes de contexto no entrenan el modelo. Sus posiciones entre 5 y 20 millones MXN y perfiles Conservador, Moderado y Agresivo son simulados. El motor de escenarios calcula hipótesis lineales y las mantiene separadas de la inferencia de noticias.

## Entorno y protocolo

La aplicación se probó primero en Python 3.12 y después en Docker Desktop, con contenedores Linux ARM64 en el Mac local. Se conserva la imagen y sus metadatos en evidencias/docker-image-local.json. El Dockerfile instala las versiones directas de requirements.txt; la imagen es la unidad exacta ejecutada. Una reconstrucción futura puede resolver otras dependencias transitivas; por ello se registra también el entorno instalado.

Las pruebas de contrato usan FastAPI TestClient. La prueba adicional scripts/smoke.py utiliza HTTP real. scripts/regression_http.py envía las 452 noticias al puerto publicado del contenedor y compara sus probabilidades. Finalmente, el cliente de Streamlit se ejecuta dentro del contenedor web para consultar api:8000; eso comprueba la resolución de servicio, red y credencial entre componentes.

## Casos funcionales y extremos

| Grupo | Entrada o condición | Resultado esperado y observado |
|---|---|---|
| Disponibilidad | Modelo cargado y /health | HTTP 200 y model_ready verdadero |
| Contrato | OpenAPI y manifiesto | Rutas disponibles, umbral e identidad conservados |
| Autenticación | Clave ausente o incorrecta | HTTP 401 |
| Texto | Vacío, espacios, números, nulo o más de 4000 caracteres | HTTP 422 |
| Esquema | Idioma es o campo desconocido | HTTP 422 |
| Vocabulario | Texto sin términos conocidos | HTTP 422, sin predicción fiable |
| Regresión | Las 452 noticias congeladas | Probabilidades dentro de tolerancia 10⁻¹² |
| Contexto | Consulta de clientes | 150 ficticios, posiciones dentro de los límites |
| Escenario | Perfil compatible y beneficio neto positivo | Elegible sólo para revisión humana |
| Protección de perfil | Perfil diferente | No elegible |
| Costos | Beneficio insuficiente tras gastos | No elegible |
| Límites numéricos | Proporción cero o mayor que uno, meses cero o fraccionarios, gastos negativos | HTTP 422 |
| Identidad | Cliente simulado inexistente | HTTP 404 |
| Configuración | Arranque sin clave suficiente | Arranque rechazado |
| Fallo de red | Backend no disponible | Mensaje comprensible en Streamlit |

La ejecución local aprobó 23 pruebas. Son 23 casos de pytest, no 452 casos adicionales de pytest: una de las pruebas recorre todo el test histórico. El informe JUnit conserva el detalle. Se observó una advertencia de deprecación de Starlette sobre TestClient y httpx; no produjo un fallo, pero se registra como deuda de actualización antes de futuras versiones.

Durante la inspección del navegador detecté que una expresión condicional de Streamlit mostraba la descripción interna de un objeto. La sustituí por un bloque if/else, reconstruí la imagen y repetí la interacción. La probabilidad y la alerta permanecieron correctas y desapareció el texto técnico innecesario.

## Resultados del modelo dentro de Docker

| Métrica | Resultado |
|---|---|
| Verdaderos negativos | 366 |
| Falsos positivos | 25 |
| Falsos negativos | 10 |
| Verdaderos positivos | 51 |
| Accuracy | 0.9226 |
| Precisión | 0.6711 |
| Recall | 0.8361 |
| F1 | 0.7445 |
| ROC AUC | 0.9548 |

Se generan 76 alertas: 51 noticias negativas recuperadas y 25 falsas alertas. Persisten 10 omisiones. La meta conjunta de recall y precisión de Actividad 6 no se alcanza. Empaquetar el modelo en Docker no elimina esa limitación ni demuestra generalización a noticias mexicanas.

La regresión HTTP inicial tardó aproximadamente 1.32 segundos para las 452 solicitudes secuenciales en este equipo. Es una observación de comprobación, no un SLA, percentil de latencia, prueba concurrente ni comparación válida de proveedores cloud.

## Análisis del comportamiento del modelo

![Distribución de probabilidades](../evidencias/distribucion_probabilidades.png)

Figura 2. Distribución retrospectiva de probabilidades en las 452 noticias conservadas.

Defino cerca del umbral como la banda descriptiva de 0.19 a 0.21, inclusive: contiene 5 noticias. No es un intervalo de confianza. En la frontera, una variación pequeña de puntuación puede cambiar la prioridad de lectura sin que cambie el riesgo económico del cliente. Por ello no uso la alerta como instrucción de inversión. El histograma y los conteos se regeneran con scripts/analyze_behavior.py y quedan respaldados por evidencias/comportamiento_modelo.json, que identifica el CSV mediante SHA256.

| Umbral exploratorio | Alertas | Cambios frente a 0.20 | FP | FN |
|---|---|---|---|---|
| 0.19 | 78 | 2 | 27 | 10 |
| 0.20 operativo | 76 | 0 | 25 | 10 |
| 0.21 | 73 | 3 | 22 | 10 |

Bajar a 0.19 agrega dos falsas alertas; subir a 0.21 retira tres falsas alertas en este conjunto. Ninguna de las dos alternativas recupera los diez falsos negativos. Es un diagnóstico retrospectivo, no una selección válida de un nuevo umbral: mantengo 0.20 y reservo cualquier decisión futura para validación independiente.

### Lectura de errores concretos

Seleccioné los primeros tres errores de cada tipo en el orden del CSV, sin presentarlos como una muestra aleatoria ni una explicación causal del modelo. Los textos originales completos están en el JSON de evidencia; aquí resumo su contenido (Malo et al., 2014).

| Caso | Probabilidad | Lectura del texto y consecuencia operativa |
|---|---|---|
| FN FPB0374 | 0.0481 | Descenso de inventarios de pulpa en Norteamérica. El corpus lo etiqueta negativo; el significado económico depende del contexto sectorial. La ausencia de alerta no descarta un cambio relevante. |
| FN FPB0382 | 0.0422 | Flujo operativo en mínimo de ocho años. Omite un deterioro financiero explícito que yo sí revisaría al preparar una reunión. |
| FN FPB2012 | 0.0456 | Incertidumbres que afectan la perspectiva de largo plazo. La formulación breve no activa la alerta; necesito contexto adicional. |
| FP FPB0056 | 0.2150 | Expectativa de crecimiento de ventas y retorno a beneficios. La alerta contradice la etiqueta positiva y genera trabajo de revisión innecesario. |
| FP FPB0203 | 0.2392 | Aumento de utilidad neta de 15 %. La clasificación negativa no equivale a deterioro del emisor. |
| FP FPB0331 | 0.3571 | Reducción de la pérdida frente al año previo. Sigue mencionando una pérdida, pero el corpus valora la mejora; el contexto comparativo importa. |

Estas lecturas describen el contenido observado; no demuestran qué palabras causaron cada decisión. El análisis no sustituye una explicación formal del estimador.

### Rechazo y tiempos de respuesta

Cuando ninguno de los vocabularios TF-IDF de los tres calibradores reconoce términos, la API devuelve HTTP 422 en lugar de una probabilidad. Evito así presentar una salida sin soporte léxico como si fuera evidencia para el banquero. El rechazo exige lectura humana; no significa que la noticia sea neutral. Tampoco valida el idioma: declarar en sigue siendo responsabilidad del usuario.

La evidencia original de Docker registra 1.321524792 segundos para 452 solicitudes secuenciales: 2.923727 ms por solicitud como promedio amortizado del recorrido. Incluye el trabajo del cliente y del bucle; no se guardaron duraciones individuales y no puedo atribuir percentiles ni un máximo por petición. No es un SLA ni una prueba de carga.

Como banquero Sr., confío en esta capa para ordenar una lectura inicial, siempre que la noticia esté dentro del alcance en inglés. No confío en la ausencia de alerta para descartar deterioro ni en una alerta para justificar una migración. Los diez falsos negativos y las veinticinco falsas alertas explican por qué conservo supervisión humana y por qué la meta conjunta sigue sin alcanzarse.

## Escenario económico y controles

Para C001, con posición de $11,858,000, migrar 35 % supone $4,150,300. Una mejora anual hipotética de 3 puntos a 12 meses representa $124,509; el corretaje supuesto del 2 % asciende a $83,006 y deja $41,503 antes de impuestos y otros gastos. El ejemplo sólo puede marcarse elegible para revisión si el destino conserva el perfil Moderado y el beneficio neto supuesto es positivo.

El 1 % por compra y 1 % por venta no se presenta como tarifa general de BBVA. El índice de fondos heredado tiene corte al 22 de octubre de 2026; hay que confirmar cada serie, periodicidad y vigencia en el original. Las comisiones de fondos no equivalen al ingreso neto del banco. Si el rendimiento introducido ya es neto, no descuento de nuevo el mismo gasto.

## Evidencia y criterios de aceptación

| Criterio de la rúbrica | Evidencia verificable |
|---|---|
| Docker y ejecución local, 25 % | Dockerfile, compose.yaml, estado healthy, ID y arquitectura de imagen |
| Integración API y frontend, 25 % | backend/main.py, frontend/client.py, smoke HTTP y respuesta entre contenedores |
| Pruebas y casos extremos, 25 % | pruebas/, JUnit, regresión HTTP de 452 noticias y resultados de este documento |
| Documentación y repositorio, 25 % | README, manual, configuración, fuentes y registro de cambios |

Los archivos de evidencia están en evidencias/. Las capturas muestran la aplicación local; los JSON y JUnit permiten revisar el resultado sin depender de una imagen. El workflow de GitHub está configurado para repetir pruebas y construcción y conservar artefactos; el estado de una ejecución cloud/CI debe comprobarse en Actions y no se infiere de la validación local.

La repetición completó las 23 pruebas en Ubuntu limpio. Después de registrar el fallo por ausencia de systemd, continué en un contenedor de laboratorio con daemon Docker propio y almacenamiento vfs, sin montar el socket ni carpetas del host. Ese contenedor externo necesita privilegios sólo para Docker anidado; no cambia el usuario ni los controles de los servicios de la aplicación. Se construyó la imagen, ambos servicios alcanzaron healthy, las 452 llamadas reprodujeron las predicciones y el cliente Streamlit consultó la API por nombre de servicio. Este modo es una comprobación de laboratorio y no una recomendación de despliegue productivo. Las bitácoras y los tiempos están en evidencias/replicabilidad.json; la regresión está en evidencias/regresion_ubuntu_limpio.json.

## Riesgos residuales y siguiente paso

Antes de un uso real necesito validación temporal externa, licencia apta para el uso previsto, datos mexicanos y métricas por segmento. También necesito autenticación por usuario, secretos gestionados, TLS si se expone la aplicación, control de tasa y pruebas concurrentes. El hash protege la identidad del archivo, pero no vuelve seguro cargar artefactos joblib de terceros desconocidos.

La imagen permite una demostración local reproducible y la arquitectura está preparada para desplegarse. Mi decisión es conservarla como prototipo académico con revisión humana; no autorizo con ella operaciones, rotación de fondos para generar comisiones ni promesas de mejores rendimientos.

## Referencias y asistencia

Modelo y evaluación: https://github.com/eduardoaburtoa/actividad6-evaluacion-portafolios

Financial PhraseBank: Malo et al. (2014), corpus conservado bajo CC BY-NC-SA 3.0; licencia en modelos/LICENSE_DATASET.txt.

Normativa de fondos: https://www.bbva.mx/personas/productos/inversion/normativa-de-fondos.html

Rúbrica de Proyecto Fase II y temas 15 y 16 proporcionados por Universidad Tecmilenio. Programación, revisión y documentación con apoyo de ChatGPT/Codex; las métricas corresponden a ejecuciones, no a estimaciones generadas por el asistente.

## Conclusiones

Conservo el ánimo de llevar la IA al trabajo cotidiano del banquero con evidencia verificable. La integración funciona y las predicciones se conservan, pero los errores observados exigen lectura humana. Mi siguiente paso es medir generalización y utilidad en un piloto controlado; no usar estas cifras retrospectivas para prometer rendimiento. El alcance de validación responde a la rúbrica y al material de despliegue del curso (Universidad Tecmilenio, 2026a, 2026b, 2026c).

Docker separa servicios y controla el arranque (Docker, Inc., s. f.-a); FastAPI documenta el contrato (FastAPI, s. f.) y Streamlit organiza la interacción (Streamlit, s. f.). El procedimiento cloud permanece preparado y depende de identidad y secretos adecuados (Google Cloud, s. f.-c, s. f.-d). Antes de cualquier recomendación revisaría costos reales y vigencia por serie en BBVA México (s. f.).


## Cobertura textual de la rúbrica

Los cuatro criterios tienen ponderación de 25 % (Universidad Tecmilenio, 2026c). Las páginas corresponden al PDF de esta revisión; Google Docs puede repaginar según su configuración.

| Criterio | Sección verificable | Página del PDF |
|---|---|---|
| Contenerización y despliegue local | Entorno y protocolo; evidencia Docker | 6 |
| Integración técnica (API, frontend/backend) | Arquitectura e integración | 3–5 |
| Pruebas y validación del modelo | Casos extremos; resultados y análisis del comportamiento | 6–9 |
| Documentación y repositorio | Evidencia y criterios; conclusiones y referencias | 9–11 |

## Referencias

Aburto Angulo, E. (2026). Fase I Business case del motor de señales de rotación de fondos de inversión con IA [Trabajo académico, Universidad Tecmilenio]. Cifras conservadas del caso de negocio y de las instrucciones de continuidad del autor.

BBVA México. (s. f.). Normativa de fondos. https://www.bbva.mx/personas/productos/inversion/normativa-de-fondos.html

Docker, Inc. (s. f.-a). Control startup and shutdown order in Compose. https://docs.docker.com/compose/how-tos/startup-order/

Docker, Inc. (s. f.-b). Install Docker Engine on Ubuntu. https://docs.docker.com/engine/install/ubuntu/

FastAPI. (s. f.). Extending OpenAPI. https://fastapi.tiangolo.com/how-to/extending-openapi/

Google Cloud. (s. f.-a). General-purpose machine family pricing. https://cloud.google.com/products/compute/pricing/general-purpose

Google Cloud. (s. f.-b). Cloud Run pricing. https://cloud.google.com/run/pricing

Google Cloud. (s. f.-c). Authenticating service-to-service. https://docs.cloud.google.com/run/docs/authenticating/service-to-service

Google Cloud. (s. f.-d). Configure secrets for services. https://docs.cloud.google.com/run/docs/configuring/services/secrets

Hugging Face. (s. f.). Spaces overview. https://huggingface.co/docs/hub/en/spaces-overview

Malo, P., Sinha, A., Korhonen, P., Wallenius, J., & Takala, P. (2014). Good debt or bad debt: Detecting semantic orientations in economic texts. Journal of the Association for Information Science and Technology, 65(4), 782–796. https://doi.org/10.1002/asi.23062

Render. (s. f.). Deploy for free. https://render.com/docs/free

Streamlit. (s. f.). Streamlit Community Cloud. https://docs.streamlit.io/deploy/streamlit-community-cloud

Universidad Tecmilenio. (2026a). Tema 15 [Material del curso Gestión de Proyectos de Inteligencia Artificial].

Universidad Tecmilenio. (2026b). Tema 16 [Material del curso Gestión de Proyectos de Inteligencia Artificial].

Universidad Tecmilenio. (2026c). Rúbrica del Proyecto Fase II [Instrumento de evaluación].

Este documento fue estructurado precisamente para cubrir esos 4 apartados de forma explícita y verificable.
