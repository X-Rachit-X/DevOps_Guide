FROM node:22-slim

WORKDIR /app

RUN useradd --system --uid 1001 appuser

COPY --chown=appuser:appuser package*.json ./
RUN npm ci --omit=dev

COPY --chown=appuser:appuser dist ./dist

USER appuser

CMD ["node", "dist/index.js"]
