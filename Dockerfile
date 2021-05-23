FROM docker.io/library/python:3.9-slim
WORKDIR /usr/src/app
COPY . .
RUN set -ex; \
    useradd \
        --system \
        --shell /bin/false \
        --home-dir /usr/src/app \
        --no-user-group \
        --uid 999 \
        raspy_monitor; \
    mkdir -p /config; \
    chown -R raspy_monitor /usr/src/app /config; \
    apt update; apt install -y gcc g++; \
    pip install -r requirements.txt; \
    apt purge --autoremove -y gcc g++;
STOPSIGNAL SIGINT
ENV DB_PATH "/config/raspy_monitor.db"
USER raspy_monitor
CMD python3 app.py
