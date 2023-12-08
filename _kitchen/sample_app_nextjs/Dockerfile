FROM node:20

WORKDIR /app

# Install and cache app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm ci

# Copy the rest of the application code
COPY . .

EXPOSE 3087
CMD ["npm", "run", "dev"]