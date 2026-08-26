FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY frontend/package*.json ./
RUN npm ci || npm install

COPY frontend/ .
RUN chmod -R +x node_modules/.bin && npx vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

RUN echo 'server { \
    listen 80; \
    listen [::]:80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    location / { \
        try_files $uri $uri/ /index.html; \
        add_header Cache-Control "no-cache, no-store, must-revalidate" always; \
    } \
    location /assets/ { \
        try_files $uri =404; \
        add_header Cache-Control "public, max-age=31536000, immutable" always; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["sh", "-c", "nginx -g 'daemon off;'"]
