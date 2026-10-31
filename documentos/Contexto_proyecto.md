# Contexto complementario del proyecto

Este anexo conserva el contexto comercial y la continuidad solicitada. Para evaluar Fase II, consultar primero el manual, la validación y la evidencia de Docker/API.

## Qué podrás hacer

1. Analizar una noticia financiera **en inglés** y obtener su probabilidad de clase negativa.
2. Consultar 150 personajes ficticios con posiciones entre **$5 y $20 millones MXN**.
3. Simular una migración, sus costos y la compatibilidad del perfil, antes de llevarla a revisión humana.

Los personajes son un recurso didáctico para dar personalidad a los casos sin utilizar información real. No forman parte del entrenamiento del clasificador.

## Supuestos del escenario

El escenario supone **1 % por compra y 1 % por venta**, ambos sobre el mismo monto migrado. Sólo marca un caso como elegible para revisión cuando el perfil coincide y el beneficio incremental supuesto después de costos es positivo. La mejora de rendimiento la introduce el usuario como hipótesis; no la produce el modelo. No se incorporan impuestos ni capitalización. La elegibilidad no equivale a una recomendación.

Se conservan [61 fichas indexadas](../contexto/fichas_bbva.csv) y [693 registros por serie](../contexto/comisiones_por_serie.csv) de la actividad anterior, con corte del 22 de octubre de 2026. Antes de usar una comisión hay que comprobar vigencia, serie y periodicidad en la [fuente oficial BBVA](https://www.bbva.mx/personas/productos/inversion/normativa-de-fondos.html). No se presenta ese inventario como actualización de todas las fichas al 30 de octubre.


## Continuidad del proyecto

Mi proyecto parte del motor de señales de rotación de fondos de inversión con IA para banca patrimonial, privada y casa de bolsa. La Actividad 4 comparó modelos preentrenados de Hugging Face para leer notas de mercado; la Actividad 5 registró el entrenamiento en MLflow; la Actividad 6 evaluó la SVM calibrada con umbral 0.20. La Fase I construyó el business case y esta Fase II convierte el modelo conservado en una aplicación integrada y desplegable.

Conservo las cifras de mi business case sin recalcularlas: alcance de 24 asesores por 150 clientes, 3,600 clientes y AUM simulado de $54,397 millones; inversión del piloto de $9,083,448 en los meses 1 a 9 con seis asesores; operación anual de $4,769,996. El beneficio esperado a pleno funcionamiento es $40,540,443 al año, con ROI a tres años de 298.6 % y recuperación en el mes 13; el escenario conservador plantea 38.8 % y mes 25 (Aburto Angulo, 2026).

La razón económica del proyecto es que, bajo aquellos supuestos, los clientes pagarían $79.65 millones de corretaje y conservarían $82.72 millones de rendimiento adicional: $1.04 por cada peso de corretaje. El umbral de rotación planteado es una mejora de 3.0 puntos porcentuales frente al costo supuesto de 2 %. Los supuestos críticos son S-14, detección actual de 30 %; S-15, aceptación de 70 %; y S-16, seis rotaciones no justificadas al año. Son hipótesis del caso de negocio, no resultados de esta aplicación.

Materializo la lectura de noticias con PLN y un escenario que calcula el costo didáctico del 2 % y la compatibilidad del perfil antes de proponer una revisión. Quedan para Fase III la proyección de rendimiento por clase de activo, la combinación de señales con el umbral financiero de 3.0 puntos, la integración con órdenes y el tablero de KPI. El umbral financiero de 3.0 puntos no debe confundirse con la probabilidad 0.20 del clasificador.

El riesgo R-01 es el conflicto de interés: la institución gana cuando el cliente se mueve. El control previsto exige suspender y recalibrar el motor si más de 25 % de las rotaciones recomendadas no supera su costo a doce meses. Este control todavía no está automatizado. La Fase II acredita que la arquitectura funciona, no que el ROI de 298.6 % se vaya a materializar; eso se mide en el piloto de nueve meses. La IA no sustituye el criterio del banquero; lo aumenta.


