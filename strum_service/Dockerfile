FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build once (runs tsoa + tsc as defined in package.json)
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
