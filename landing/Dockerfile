FROM fholzer/nginx-brotli:latest

# Install wget and brotli CLI for build-time compression
RUN apk add --no-cache wget brotli

# Remove default config
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy nginx config first (better layer caching)
COPY nginx.conf /etc/nginx/conf.d/

# Copy application files
COPY . /usr/share/nginx/html/

# Pre-compress ALL compressible files with Brotli at maximum quality
# This happens at build time, so runtime compression is instant
RUN find /usr/share/nginx/html -type f \( \
        -name "*.js" -o \
        -name "*.css" -o \
        -name "*.svg" -o \
        -name "*.json" -o \
        -name "*.wasm" -o \
        -name "*.xml" -o \
        -name "*.html" \
    \) -exec sh -c 'echo "Compressing: $1" && brotli -q 11 -f -k "$1"' _ {} \; && \
    echo "✅ Brotli pre-compression complete" && \
    echo "📊 Checking compression results:" && \
    find /usr/share/nginx/html/web -name "*.js" -exec sh -c 'echo "Original: $(stat -c%s "$1") bytes | Compressed: $(stat -c%s "$1.br" 2>/dev/null || echo "N/A") bytes - $1"' _ {} \; | head -5

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 9070

# Enable healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget -q --spider http://localhost:9070/health || exit 1

# CMD ["nginx", "-g", "daemon off;"]