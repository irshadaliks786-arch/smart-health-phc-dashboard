# --- build stage ---
FROM node:20-slim AS build
WORKDIR /app

# API base URL baked in at build time (Vite env vars are compile-time).
ARG VITE_API_BASE_URL=http://localhost:8080
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

# --- serve stage ---
FROM nginx:1.27-alpine
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

ENV PORT=8080
EXPOSE 8080

# nginx's built-in entrypoint runs envsubst on /etc/nginx/templates/*.template
# into /etc/nginx/conf.d/, which is exactly what Cloud Run's dynamic $PORT needs.
CMD ["nginx", "-g", "daemon off;"]
