FROM node:18-alpine

# ❌ Inefficient layer structure - copies everything first
COPY . /app
WORKDIR /app

# ❌ npm ci runs after copying all files (invalidates cache frequently)
RUN npm ci

# ❌ Build runs every time instead of being cached
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]