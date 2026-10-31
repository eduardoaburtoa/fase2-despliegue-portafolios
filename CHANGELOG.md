# Historial

## 1.0.0 — 30 de octubre de 2026

- Fase II: FastAPI, Streamlit y dos servicios Docker con comprobaciones de salud.
- Conservación del modelo SVM calibrado y umbral 0.20 de Actividad 6; sin reentrenamiento ni nueva selección sobre test.
- Validación de entradas, clave de acceso, integridad SHA256 del modelo y rechazo de textos fuera del vocabulario.
- Simulación separada de costos y perfiles para 150 clientes ficticios.
- Pruebas automatizadas, regresión de 452 predicciones y evidencias de integración HTTP.
- Manual de despliegue y validación. La nube se documenta como procedimiento preparado, no como despliegue ejecutado.
