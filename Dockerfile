FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PYTHONPATH=/app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 app
COPY --chown=app:app backend backend
COPY --chown=app:app frontend frontend
COPY --chown=app:app modelos modelos
COPY --chown=app:app contexto contexto
COPY --chown=app:app documentos/vertice_logo.png documentos/vertice_logo.png
COPY --chown=app:app .streamlit .streamlit
COPY --chown=app:app scripts/start.py scripts/start.py
USER app
EXPOSE 8000 8501
CMD ["python", "scripts/start.py"]
