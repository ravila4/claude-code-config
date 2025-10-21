---
name: docker-optimization
description: Optimize Docker images and containers for size, build speed, security, and runtime performance with multi-stage builds, framework-specific patterns, and security hardening
---

# Docker Optimization

## Overview

Optimize Docker images and containers for production using multi-stage builds, minimal base images, security hardening, and framework-specific best practices.

**Core Principle:** Minimal size + Maximum security + Fast builds = Production-ready containers

## When to Use

Apply Docker optimization when:
- Building production Docker images
- Image sizes are too large (>500MB for most apps)
- Build times are slow (>5 minutes)
- Security vulnerabilities need fixing
- Migrating to containers
- Implementing CI/CD for containers

## Optimization Workflow

### 1. Analysis Phase

Analyze the existing Dockerfile:
- Identify current base image and size
- Find optimization opportunities
- Detect security issues
- Measure current build performance

### 2. Detection Phase

Determine application type:
- Analyze project structure
- Detect dependencies (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`)
- Identify workload type (web app, microservice, data processing)

### 3. Optimization Phase

Apply appropriate optimizations:
- Select optimal base image
- Design multi-stage build
- Implement security hardening
- Optimize layer caching
- Configure runtime settings

### 4. Validation Phase

Ensure optimizations work:
- Build and test optimized image
- Compare sizes (before/after)
- Run security scans (Trivy, Hadolint)
- Verify functionality with health checks

## Base Image Selection

Choose optimal base images based on requirements:

**Alpine** (5-10MB)
- Best for: Size-critical applications
- Tradeoff: Some compatibility issues with compiled binaries

**Slim** (50-100MB)
- Best for: Good balance of size and compatibility
- Tradeoff: Larger than Alpine

**Distroless** (20-40MB)
- Best for: Maximum security, minimal attack surface
- Tradeoff: No shell or package manager

**Scratch** (0MB base)
- Best for: Static binaries only (Go, Rust)
- Tradeoff: No OS utilities at all

## Multi-Stage Build Pattern

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=nodejs:nodejs /app/dist ./dist
USER nodejs
EXPOSE 3000
HEALTHCHECK CMD node healthcheck.js
CMD ["node", "dist/index.js"]
```

## Framework-Specific Optimizations

### Node.js / Express / Next.js

**Modern approach with Bun:**
- 5x faster dependency installation
- 4x faster runtime
- 90% smaller images

**Optimizations:**
- Use distroless for production
- Implement health checks
- Optimize for startup time
- Use dumb-init for signal handling

```dockerfile
FROM oven/bun:1-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun build ./src/index.ts --outdir ./dist

FROM gcr.io/distroless/base-debian12
COPY --from=build /app/dist /app
CMD ["/app/index.js"]
```

### Python / FastAPI / Django

**Modern approach with UV package manager:**
- 10-100x faster than pip
- Better dependency resolution

**Optimizations:**
- Multi-stage with virtual environments
- Distroless python3 for production
- Set `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`
- Use Gunicorn with Uvicorn workers

```dockerfile
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

FROM base AS builder
RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

FROM base
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app
WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
```

### Go / Gin

**Ultimate minimal approach:**
- Static binary compilation
- Scratch or distroless base
- Final image: 5-20MB

**Optimizations:**
- `CGO_ENABLED=0` for static linking
- Use UPX compression (optional)
- Leverage BuildKit cache mounts

```dockerfile
FROM golang:1.21-alpine AS build
WORKDIR /app
COPY go.* ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o server

FROM scratch
COPY --from=build /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

### Rust / Actix

**Performance-focused approach:**
- Static musl compilation
- Minimal scratch image
- Sub-10MB final images

**Optimizations:**
- Cross-compilation for musl
- Cargo dependency caching
- Strip binaries for size

```dockerfile
FROM rust:1.75-alpine AS build
WORKDIR /app
RUN apk add --no-cache musl-dev
COPY Cargo.* ./
RUN cargo fetch
COPY . .
RUN cargo build --release --target x86_64-unknown-linux-musl && \
    strip target/x86_64-unknown-linux-musl/release/app

FROM scratch
COPY --from=build /app/target/x86_64-unknown-linux-musl/release/app /app
ENTRYPOINT ["/app"]
```

### Java / Spring Boot

**GraalVM Native Image approach:**
- Sub-second startup time
- 90% size reduction (20-50MB vs 200-300MB)
- Better resource efficiency

**Optimizations:**
- Compile to native binary
- Use distroless Java base
- Configure JVM memory for containers

```dockerfile
FROM ghcr.io/graalvm/native-image:22 AS build
WORKDIR /app
COPY pom.xml ./
COPY src ./src
RUN native-image --no-fallback -jar target/app.jar app

FROM gcr.io/distroless/base
COPY --from=build /app/app /app
ENTRYPOINT ["/app"]
```

## Layer Optimization

**Best practices:**

1. **Order commands from least to most frequently changing:**
   ```dockerfile
   # Good - dependencies change less often than source code
   COPY package.json package-lock.json ./
   RUN npm ci
   COPY . .

   # Bad - source changes invalidate dependency cache
   COPY . .
   RUN npm install
   ```

2. **Combine related RUN commands:**
   ```dockerfile
   # Good - single layer
   RUN apt-get update && \
       apt-get install -y curl && \
       rm -rf /var/lib/apt/lists/*

   # Bad - multiple layers
   RUN apt-get update
   RUN apt-get install -y curl
   RUN rm -rf /var/lib/apt/lists/*
   ```

3. **Use .dockerignore:**
   ```
   node_modules
   .git
   .env
   *.md
   tests
   ```

## Security Hardening

### 1. Run as Non-Root User

```dockerfile
# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Switch to non-root
USER appuser
```

### 2. Use Specific Version Tags

```dockerfile
# Good
FROM node:20.10.0-alpine

# Bad
FROM node:latest
```

### 3. Scan for Vulnerabilities

```bash
# Trivy scan
trivy image myapp:latest

# Hadolint linting
hadolint Dockerfile
```

### 4. Drop Unnecessary Capabilities

```dockerfile
# In docker-compose or K8s manifests
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
```

### 5. Use Read-Only Root Filesystem

```dockerfile
# In docker-compose
read_only: true
tmpfs:
  - /tmp
```

## Build Performance Optimization

### Use BuildKit Cache Mounts

```dockerfile
# Syntax directive for BuildKit
# syntax=docker/dockerfile:1

# Cache package manager downloads
RUN --mount=type=cache,target=/root/.npm \
    npm install

# Cache Go modules
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
```

### Enable BuildKit

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1
docker build .

# Or use buildx
docker buildx build .
```

## Health Checks

Add health checks for container orchestration:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

## Common Pitfalls to Avoid

### Don't Use ADD (Use COPY)

```dockerfile
# Good
COPY package.json .

# Bad - ADD has implicit tar extraction
ADD package.json .
```

### Don't Store Secrets in Images

```dockerfile
# Bad - secret in image history
RUN echo "API_KEY=secret123" > /app/.env

# Good - use runtime secrets
docker run -e API_KEY=secret123 myapp
```

### Don't Install Unnecessary Packages

```dockerfile
# Good
RUN apt-get install --no-install-recommends -y curl

# Bad - installs recommended packages too
RUN apt-get install -y curl
```

## Tools Reference

**Build Tools:**
- BuildKit - Modern Docker build engine
- Docker Buildx - Multi-platform builds
- Dive - Image layer analysis

**Security Tools:**
- Trivy - Vulnerability scanning
- Hadolint - Dockerfile linting
- Docker Bench - Security audit

**Modern Package Managers:**
- Bun (Node.js) - 5x faster than npm
- UV (Python) - 10-100x faster than pip
- Cargo with sccache (Rust)

## Optimization Checklist

Before deploying:
- [ ] Multi-stage build implemented
- [ ] Minimal base image (alpine, slim, or distroless)
- [ ] Specific version tags (not :latest)
- [ ] Running as non-root user
- [ ] .dockerignore configured
- [ ] Layer order optimized (least to most frequently changing)
- [ ] Package caches cleaned in same RUN layer
- [ ] Health check implemented
- [ ] Vulnerability scan passed (Trivy)
- [ ] Dockerfile lint passed (Hadolint)
- [ ] Image size < 200MB for most apps
- [ ] Build time < 5 minutes with cache

## Example Results

**Node.js Application:**
- Before: 800MB (ubuntu:latest)
- After: 50MB (node:20-alpine multi-stage)
- Improvement: 94% size reduction

**Python FastAPI:**
- Before: 1.2GB (python:3.11)
- After: 150MB (python:3.11-slim with UV)
- Improvement: 87% size reduction, 10x faster builds

**Go Microservice:**
- Before: 500MB (golang:1.21)
- After: 8MB (scratch with static binary)
- Improvement: 98% size reduction

## Integration with Other Workflows

**Works with:**
- CI/CD pipelines (automated optimization)
- Security scanning workflows
- Container orchestration (K8s, Docker Swarm)

**Complements:**
- test-driven-development (test in containers)
- git-worktrees (test different optimization strategies)
