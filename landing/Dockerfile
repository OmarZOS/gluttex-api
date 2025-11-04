# Use nginx with Brotli support
FROM fholzer/nginx-brotli:latest

# Install wget for healthcheck
RUN apk add --no-cache wget

# Remove default nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/

# Copy all content
COPY . /usr/share/nginx/html/

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 9070

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget -q --spider http://localhost:9070/ || exit 1

CMD ["nginx", "-g", "daemon off;"]