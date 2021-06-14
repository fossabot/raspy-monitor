FROM docker.io/library/node:14-alpine
LABEL org.opencontainers.image.source https://github.com/lemniskett/raspy-monitor
WORKDIR /usr/src/app
RUN set -ex; \
    adduser -S -s /bin/false -h /usr/src/app -u 999 raspy_monitor; \
    mkdir -p /config; \
    chown -R raspy_monitor /usr/src/app /config;
USER raspy_monitor
COPY --chown=raspy_monitor:root . .
RUN set -ex; \
    npm install; \
    npm run build; \
    npm prune --production; \
    rm -rf .git
ENV NODE_ENV production
EXPOSE 3000
CMD node build/index.js