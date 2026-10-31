ARG BASE_IMAGE=vertice-fase2:1.0.0
FROM ${BASE_IMAGE}
COPY --chown=app:app deploy/cloudrun_web.py deploy/cloudrun_web.py
CMD ["python", "deploy/cloudrun_web.py"]
