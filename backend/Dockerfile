FROM python:3.12-slim

RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh
RUN chown -R appuser:appuser /app
RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; resp = urllib.request.urlopen('http://localhost:8000/api/health'); assert resp.status == 200"

ENTRYPOINT ["./entrypoint.sh"]
