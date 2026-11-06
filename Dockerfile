# Multi-stage lightweight container
FROM python:3.12-alpine

# Install nginx, bash and runit/supervisor
RUN apk add --no-cache nginx bash curl procps

WORKDIR /app

# Copy application directories
COPY conf/nginx-container.conf /etc/nginx/nginx.conf
COPY backend/ /app/backend/
COPY static/ /app/static/
COPY plugins/ /app/plugins/
COPY reports/ /app/reports/
COPY data/ /app/data/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh /app/backend/server.py && \
    mkdir -p /app/logs /var/log/nginx /run/nginx

EXPOSE 8088

# Volumes for host source browsing and persistent data
VOLUME ["/sources/src", "/sources/ecosystem", "/app/data", "/app/reports", "/app/plugins"]

ENTRYPOINT ["/app/entrypoint.sh"]
