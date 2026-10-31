# Bitácora de reproducción en Ubuntu 24.04

Los comandos siguientes se ejecutaron en el orden registrado. Los nombres identifican recursos de laboratorio de esta sesión. Requieren Docker operativo en el host. El daemon anidado usa un contenedor privilegiado sin montar archivos ni socket del host; no es configuración productiva. No ejecutar sobre recursos homónimos preexistentes.

## 01_ubuntu_limpio

Duración 0.174 s; código de salida 0.

```bash
docker run -d --name fase2-replica-medida-v110 ubuntu:24.04 sleep infinity
```

## 02_prerrequisitos

Duración 13.580 s; código de salida 0.

```bash
docker exec fase2-replica-medida-v110 bash -lc 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 ca-certificates curl'
```

## 03_clonar

Duración 1.523 s; código de salida 0.

```bash
docker exec fase2-replica-medida-v110 git clone https://github.com/eduardoaburtoa/fase2-despliegue-portafolios.git /tmp/proyecto
```

## 04_instalador_docker

Duración 15.074 s; código de salida 1.

```bash
docker exec fase2-replica-medida-v110 bash /tmp/proyecto/scripts/install_docker_ubuntu.sh
```

## 05_versiones

Duración 0.075 s; código de salida 0.

```bash
docker exec fase2-replica-medida-v110 bash -lc 'cat /etc/os-release; docker --version; docker compose version; ps -p 1 -o comm='
```

## 06_configurar

Duración 0.072 s; código de salida 0.

```bash
docker exec fase2-replica-medida-v110 bash -lc 'cd /tmp/proyecto && python3 -c "import secrets,pathlib;pathlib.Path('"'"'.env'"'"').write_text('"'"'API_TOKEN='"'"'+secrets.token_urlsafe(32)+'"'"'\n'"'"')" && chmod 600 .env && docker compose config --quiet'
```

## 07_construir

Duración 0.061 s; código de salida 1.

```bash
docker exec fase2-replica-medida-v110 bash -lc 'cd /tmp/proyecto && docker compose up --build -d --wait --wait-timeout 180'
```

## 08_detener_entorno

Duración 3.204 s; código de salida 0.

```bash
docker stop fase2-replica-medida-v110
```

## 09_reanudar

Duración 0.091 s; código de salida 0.

```bash
docker start fase2-replica-medida-v110
```

## 10_python

Duración 34.250 s; código de salida 0.

```bash
docker exec fase2-replica-medida-v110 bash -lc 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv && cd /tmp/proyecto && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt'
```

## 11_pruebas

Duración 4.288 s; código de salida 0.

```bash
docker exec fase2-replica-medida-v110 bash -lc 'cd /tmp/proyecto && .venv/bin/python -m pytest pruebas -q --junitxml=/tmp/pytest-ubuntu.xml'
```

## 12_copiar_junit

Duración 0.030 s; código de salida 0.

```bash
docker cp fase2-replica-medida-v110:/tmp/pytest-ubuntu.xml work/fase2/v110/repo/evidencias/pytest-ubuntu-limpio.xml
```

## 13_detener

Duración 3.352 s; código de salida 0.

```bash
docker stop fase2-replica-medida-v110
```

## 14_snapshot_ubuntu

Duración 18.381 s; código de salida 0.

```bash
docker commit fase2-replica-medida-v110 fase2-ubuntu-replica:1.1.0
```

## 15_daemon_aislado

Duración 0.429 s; código de salida 0.

```bash
docker run -d --privileged --name fase2-replica-dind-v110 fase2-ubuntu-replica:1.1.0 dockerd --storage-driver=vfs --host=unix:///var/run/docker.sock
```

## 16_esperar_daemon

Duración 0.333 s; código de salida 0.

```bash
docker exec fase2-replica-dind-v110 bash -lc 'for i in $(seq 1 30); do docker info >/dev/null 2>&1 && exit 0; sleep 1; done; exit 1'
```

## 17_compose_limpio

Duración 99.908 s; código de salida 0.

```bash
docker exec fase2-replica-dind-v110 bash -lc 'cd /tmp/proyecto && docker compose up --build -d --wait --wait-timeout 180 && docker compose ps'
```

## 18_http_regresion

Duración 2.394 s; código de salida 0.

```bash
docker exec fase2-replica-dind-v110 bash -lc 'cd /tmp/proyecto && set -a && source .env && set +a && TEST_ENV=ubuntu_limpio .venv/bin/python scripts/smoke.py && TEST_ENV=ubuntu_limpio .venv/bin/python scripts/regression_http.py && docker compose exec -T web python -c "from frontend.client import call; print(call('"'"'/v1/model'"'"')['"'"'sha256'"'"'])"'
```

## copiar_regresion_ubuntu_limpio.json

Duración 0.035 s; código de salida 0.

```bash
docker cp fase2-replica-dind-v110:/tmp/proyecto/evidencias/regresion_ubuntu_limpio.json work/fase2/v110/repo/evidencias/regresion_ubuntu_limpio.json
```

## copiar_smoke_ubuntu_limpio.json

Duración 0.019 s; código de salida 0.

```bash
docker cp fase2-replica-dind-v110:/tmp/proyecto/evidencias/smoke_ubuntu_limpio.json work/fase2/v110/repo/evidencias/smoke_ubuntu_limpio.json
```

## 19_detener_dind

Duración 2.336 s; código de salida 0.

```bash
docker stop fase2-replica-dind-v110
```
