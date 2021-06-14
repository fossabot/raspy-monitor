FROM docker.io/library/node:14-alpine
LABEL org.opencontainers.image.source https://github.com/lemniskett/raspy-
ENV NODE_ENV production
WORKDIR /usr/src/app
COPY . .
RUN set -ex; \
    adduser -S -s /bin/false -h /usr/src/app -u 999 raspy_monitor; \
    mkdir -p /config; \
    chown -R raspy_monitor /usr/src/app /config; \
    npm install; \
    npm run build; \
    npm prune --production; \
    rm -rf .git
USER raspy_monitor
EXPOSE 3000
CMD node build/index.js