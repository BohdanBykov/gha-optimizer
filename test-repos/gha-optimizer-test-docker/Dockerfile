FROM node:18-alpine

# ❌ Inefficient layer structure (could be optimized)
COPY . /app
WORKDIR /app
RUN npm ci
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]