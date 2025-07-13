FROM python:3.11-slim
WORKDIR /app

RUN printf 'Acquire::Retries "10";\nAcquire::http::Timeout "10";\nAcquire::ForceIPv4 "true";\n' \
    > /etc/apt/apt.conf.d/80-net \

RUN sed -i 's|deb.debian.org|ftp.de.debian.org|g' $(grep -Rl deb.debian.org /etc/apt) || true

RUN apt-get update --allow-insecure-repositories
RUN apt-get install -y --no-install-recommends git-lfs ffmpeg libopenblas-dev --allow-unauthenticated
RUN rm -rf /var/lib/apt/lists/*
RUN git lfs install

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ /app/app
COPY models/ /app/models
EXPOSE 7860
CMD ["python", "-m", "app.main"]
