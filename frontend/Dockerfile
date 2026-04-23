FROM node:20-alpine as build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'sed -i "s|ws://localhost:8000/ws|${WS_URL:-ws://backend:8000/ws}|g" /usr/share/nginx/html/index.html' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]