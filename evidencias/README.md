# Evidencia de ejecución local

- [Aplicación en Docker](streamlit-docker.png): captura real de la interfaz y alerta.
- [Pruebas automatizadas](pytest-local.xml): 23 aprobadas.
- [Regresión HTTP](regresion_docker_local.json): 452 noticias y métricas, tolerancia 1e-12.
- [Prueba HTTP básica](smoke_docker_local.json): salud, autenticación y 150 clientes.
- [Comunicación web → api](integracion-entre-contenedores.json): respuesta obtenida desde el contenedor web.
- [Estado de servicios](docker-services-local.json), [imagen](docker-image-local.json) y [dependencias instaladas](entorno-docker.txt).
- Las evidencias con nombre host_local_sin_docker y streamlit-integracion corresponden a la comprobación previa en el host.

Fecha: 30 de octubre de 2026. Docker Desktop local, Linux ARM64. No se presenta como despliegue en Google Cloud. Los resultados de CI, cuando existan, se consultan en Actions y sus artefactos.

## Ejecución automática adicional

[GitHub Actions 41163897429](https://github.com/eduardoaburtoa/fase2-despliegue-portafolios/actions/runs/41163897429) aprobó pruebas, Docker e integración sobre el commit 6e4cd061c05670497c3eac8d8a31b4fe78f0bf76. [Resumen verificable](github-actions.json). Los archivos con sufijo ci y docker-ci.log se extrajeron del artefacto real de esa ejecución; complementan la evidencia local.
