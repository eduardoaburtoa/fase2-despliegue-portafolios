# Anexo técnico · Lectura visual de la validación

Este complemento de revisión 1.1.1 facilita la lectura del informe de validación 1.1.0, que conserva su contenido en los cuatro formatos. No es un nuevo entrenamiento ni una nueva evaluación independiente. Analizo las mismas 452 noticias del test congelado; no uso estos resultados para modificar el modelo o el umbral.

## 1. Qué errores produce el modelo

![Matriz de confusión](../evidencias/matriz_confusion_revision.png)

Conservo el umbral 0.20. Hay 366 verdaderos negativos, 25 falsos positivos, 10 falsos negativos y 51 verdaderos positivos. La clase positiva del clasificador significa «noticia negativa»; las etiquetas originales positiva y neutral se agrupan como no negativa. Identifica 51 de las 61 noticias negativas, pero no elimina la necesidad de lectura humana. Los 25 falsos positivos implican carga de revisión; los 10 falsos negativos representan noticias que no serían priorizadas.

## 2. Dónde se sitúan las probabilidades

![Distribución de probabilidades](../evidencias/distribucion_probabilidades.png)

Cinco noticias están en la banda descriptiva inclusiva de 0.19 a 0.21. Bajar a 0.19 cambiaría dos decisiones y subir a 0.21 cambiaría tres. Es una comprobación de sensibilidad, no una búsqueda del mejor umbral sobre test. La banda no es un intervalo de confianza. El umbral operativo permanece en 0.20.

## 3. Longitud por etiqueta original

![Longitud por clase](../evidencias/longitud_por_clase.png)

| Etiqueta original | Noticias | Mediana de longitud | Mínimo–máximo |
|---|---:|---:|---:|
| Negativa | 61 | 21 | 4–45 |
| Neutral | 277 | 18 | 3–43 |
| Positiva | 114 | 20.5 | 5–48 |

La longitud cuenta coincidencias de la expresión `\b\w+\b`, no los tokens usados por TF-IDF. Las cajas representan el rango intercuartílico, la línea central es la mediana y los bigotes siguen la convención de 1.5 veces ese rango; los puntos exteriores no se eliminan. Los rangos se solapan: la longitud por sí sola no separa las clases. Tampoco atribuyo los errores a textos cortos o largos sin un análisis específico. El desbalance de tamaños debe tenerse presente al leer una exactitud global elevada.

## 4. Errores que sí conviene leer

| Caso | Error observado | Lectura del texto y consecuencia |
|---|---|---|
| FPB0382 | Falso negativo; probabilidad 0.0422 | El flujo de operación alcanza un mínimo de ocho años. Una probabilidad baja no garantiza ausencia de una noticia adversa. |
| FPB2012 | Falso negativo; probabilidad 0.0456 | La incertidumbre afecta la perspectiva de largo plazo. La alerta omite una formulación negativa que requiere contexto. |
| FPB0331 | Falso positivo; probabilidad 0.3571 | La pérdida neta disminuye respecto del periodo anterior. El texto describe una mejora aunque menciona pérdidas. |
| FPB0346 | Falso positivo; probabilidad 0.8882 | Los costos unitarios bajan 6.4 %. El descenso de costos es favorable, pero el modelo activa alerta con probabilidad alta. |

Son ejemplos seleccionados para ilustrar tipos de error, no una muestra representativa ni una explicación causal de los pesos del modelo. Los textos completos y los 35 errores se conservan en [comportamiento_modelo.json](../evidencias/comportamiento_modelo.json). No presento frecuencias de palabras como si fueran importancia o causalidad del modelo.

## 5. Reproducir y auditar

Desde la raíz del repositorio, con Python 3.12 y el entorno virtual activado:

```bash
pip install -r requirements-docs.txt
python scripts/analyze_behavior.py
python scripts/visualize_validation.py
```

El segundo script produce la matriz, el gráfico de longitud y [analisis_visual.json](../evidencias/analisis_visual.json), con conteos, definición de longitud y SHA-256 del CSV fuente. No llama a entrenamiento ni guarda un modelo. Los resultados de ejecución funcional se consultan por separado en [la bitácora Ubuntu](../evidencias/replicabilidad.json) y [las pruebas](../evidencias/pytest-ubuntu-limpio.xml).

Mi prioridad en esta Fase II es demostrar que la aplicación conserva el comportamiento del modelo, comunica correctamente sus componentes y permite repetir las pruebas. El contexto comercial permanece en [un anexo separado](Contexto_proyecto.md). La evaluación es retrospectiva y en inglés; no demuestra rentabilidad de fondos ni generalización a clientes reales.
