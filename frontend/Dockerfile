# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Enable Corepack for Yarn 4
RUN corepack enable

# Copy all frontend files first
COPY . .

# Install dependencies
RUN yarn install --frozen-lockfile

# Build the application with environment variables
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
