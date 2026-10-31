# Validación y pruebas de Fase II

Eduardo Aburto Angulo · 30 de octubre de 2026 · Versión 1.0.0

## Conclusión y alcance

Comprobé que la API y Streamlit se comunican dentro de Docker y que el modelo conserva las predicciones históricas. La suite automatizada aprobó 23 pruebas; la regresión HTTP recorrió 452 noticias y obtuvo una diferencia máxima de 2.78 × 10⁻¹⁶ respecto al archivo de referencia, menor que la tolerancia de 10⁻¹². Ambos servicios alcanzaron estado healthy.

Esta conclusión acredita la integración y consistencia técnica del prototipo local. No equivale a una validación financiera, una prueba de carga ni un despliegue cloud completado. Como banquero Sr., mantengo la revisión humana: una alerta negativa no demuestra que migrar un fondo mejore el rendimiento.

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

## Riesgos residuales y siguiente paso

Antes de un uso real necesito validación temporal externa, licencia apta para el uso previsto, datos mexicanos y métricas por segmento. También necesito autenticación por usuario, secretos gestionados, TLS si se expone la aplicación, control de tasa y pruebas concurrentes. El hash protege la identidad del archivo, pero no vuelve seguro cargar artefactos joblib de terceros desconocidos.

La imagen permite una demostración local reproducible y la arquitectura está preparada para desplegarse. Mi decisión es conservarla como prototipo académico con revisión humana; no autorizo con ella operaciones, rotación de fondos para generar comisiones ni promesas de mejores rendimientos.

## Referencias y asistencia

Modelo y evaluación: https://github.com/eduardoaburtoa/actividad6-evaluacion-portafolios

Financial PhraseBank: Malo et al. (2014), corpus conservado bajo CC BY-NC-SA 3.0; licencia en modelos/LICENSE_DATASET.txt.

Normativa de fondos: https://www.bbva.mx/personas/productos/inversion/normativa-de-fondos.html

Rúbrica de Proyecto Fase II y temas 15 y 16 proporcionados por Universidad Tecmilenio. Programación, revisión y documentación con apoyo de ChatGPT/Codex; las métricas corresponden a ejecuciones, no a estimaciones generadas por el asistente.
