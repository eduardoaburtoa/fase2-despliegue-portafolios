## Comportamiento por segmentos

Definí tres tramos fijos de longitud: 1–15, 16–30 y 31 o más unidades léxicas (`\b\w+\b`). Son descripciones del test; no se eligieron para maximizar métricas. Precisión es acierto entre alertas; recall es detección entre noticias realmente negativas. Un denominador cero se informa como no definido.

| Longitud | n | Negativas | Precisión | Recall | FP | FN | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1–15 | 158 | 15 | 58.82 % | 66.67 % | 7 | 5 | 12 |
| 16–30 | 228 | 32 | 69.77 % | 93.75 % | 13 | 2 | 15 |
| 31 o más | 66 | 14 | 68.75 % | 78.57 % | 5 | 3 | 8 |

No interpreto las diferencias entre tramos como significativas: sus tamaños y números de negativas varían. Uso esta lectura para identificar dónde revisar errores, no para cambiar el modelo con el test.

### Franjas operativas

Los extremos inferiores son inclusivos y los superiores exclusivos, salvo 1.00. La fracción negativa observada es una frecuencia retrospectiva, no una probabilidad garantizada para una noticia futura.

| Probabilidad | Noticias | Negativas reales | Fracción negativa | Acción de revisión humana |
|---|---:|---:|---:|---|
| [0, 0.10) | 349 | 9 | 2.58 % | No priorizo sólo por esta salida; leo el contexto y mantengo controles humanos. |
| [0.10, 0.20) | 27 | 1 | 3.70 % | Reviso el contexto si hay otros indicios; no altero el umbral ni descarto riesgo. |
| [0.20, 0.50) | 29 | 11 | 37.93 % | Prioriza lectura humana; contrasto la noticia con la fuente antes de cualquier decisión. |
| [0.50, 1] | 47 | 40 | 85.11 % | Prioriza lectura humana; una probabilidad alta tampoco autoriza una orden ni garantiza acierto. |

### Consistencia entre entornos

La matriz se presenta como TN, FP, FN, TP. Cada tiempo corresponde a una corrida de 452 solicitudes en su entorno; no comparo velocidad sin igualar hardware, carga y protocolo.

| Entorno | Error absoluto máximo | Matriz TN FP FN TP | Tiempo total s | Evidencia |
|---|---:|---|---:|---|
| host_local_sin_docker | 1.11022e-16 | 366, 25, 10, 51 | 0.776614 | evidencias/regresion_host_local_sin_docker.json |
| docker_local | 2.77556e-16 | 366, 25, 10, 51 | 1.321525 | evidencias/regresion_docker_local.json |
| docker_ci | No medido | No disponible | No medido | sin medición completa disponible |
| ubuntu_limpio | 2.77556e-16 | 366, 25, 10, 51 | 0.866663 | evidencias/regresion_ubuntu_limpio.json |

Como banquero, confío en que la aplicación reproduce el artefacto evaluado; no convierto esa consistencia en confianza ciega sobre cada noticia. Reviso también las alertas con probabilidad alta y no considero una probabilidad baja como ausencia de riesgo. La IA no sustituye el criterio del banquero; lo aumenta. Fuente reproducible: scripts/analyze_segments.py y evidencias/analisis_segmentos.json.
