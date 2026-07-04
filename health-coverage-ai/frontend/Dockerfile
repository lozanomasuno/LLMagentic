# ── Development stage ─────────────────────────────────────────────
FROM node:22-alpine3.22 AS development

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 4200
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200", "--disable-host-check"]

# ── Build stage ───────────────────────────────────────────────────
FROM node:22-alpine3.22 AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx ng build --configuration=production

# ── Production stage (nginx) ──────────────────────────────────────
FROM nginx:alpine AS production

COPY --from=build /app/dist/health-coverage-ai/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q -O /dev/null http://localhost:80 || exit 1
CMD ["nginx", "-g", "daemon off;"]
