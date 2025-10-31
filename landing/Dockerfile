# Stage 1: Build Flutter web app (optional, if not prebuilt)
# If you already have build/web inside landing/, skip to Stage 2.

# FROM dart:stable AS build
# WORKDIR /app
# COPY . .
# RUN flutter build web --release --web-renderer canvaskit -t lib/main.dart

# Stage 2: Nginx serving Flutter web app
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy optimized nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy all app content (including Flutter web build)
COPY . /usr/share/nginx/html/

# Expose internal port
EXPOSE 80

# Health check (optional)
HEALTHCHECK CMD wget -q --spider http://localhost/ || exit 1
