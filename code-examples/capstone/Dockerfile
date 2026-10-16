# One image, two entrypoints (editorial):  node dist/api.js  |  node dist/worker.js
FROM node:22 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:22-slim AS production
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=builder /app/dist ./dist
RUN useradd --system --uid 1001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 3000
CMD ["node", "dist/api.js"]
