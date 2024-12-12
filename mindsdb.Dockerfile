# Stage to gather dependencies (requirements.txt files and installation files)
FROM python:3.10 as deps
WORKDIR /mindsdb
ARG EXTRAS

# Copy only necessary files for dependencies, preventing unnecessary cache invalidation
COPY setup.py default_handlers.txt README.md ./
COPY mindsdb/__about__.py mindsdb/

# Copy all required requirements files (keeping structure intact)
COPY . .

# Delete non-requirements files and empty directories to clean up the context
RUN find ./ -type f -not -name "requirements*.txt" -print | xargs rm -f \
    && find ./ -type d -empty -delete

# Build stage for installing dependencies and creating the virtual environment
FROM python:3.10 as build
WORKDIR /mindsdb
ARG EXTRAS

# Configure apt to retain downloaded packages for caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install system dependencies (with caching for faster builds)
RUN --mount=target=/var/lib/apt,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt update -qy && apt-get upgrade -qy && apt-get install -qy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    freetds-dev  # Required to build pymssql on arm64 for mssql_handler

# Copy a specific version of the uv tool to avoid changes
COPY --from=ghcr.io/astral-sh/uv:0.4.23 /uv /usr/local/bin/uv

# Copy the dependencies gathered in the previous stage
COPY --from=deps /mindsdb .

# Environment variables for uv setup
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.10 \
    UV_PROJECT_ENVIRONMENT=/mindsdb \
    VIRTUAL_ENV=/venv \
    PATH=/venv/bin:$PATH

# Install main requirements and prepare the virtual environment
RUN --mount=type=cache,target=/root/.cache \
    uv venv /venv && uv pip install pip "."  # Install mindsdb core requirements

# Install extras if specified
RUN --mount=type=cache,target=/root/.cache \
    if [ -n "$EXTRAS" ]; then uv pip install $EXTRAS; fi

# Copy all code and install the mindsdb package
COPY . .
RUN --mount=type=cache,target=/root/.cache uv pip install --no-deps "."

# Development image that includes dev dependencies
FROM build as dev
WORKDIR /mindsdb

# Install system dependencies for development
RUN --mount=target=/var/lib/apt,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt update -qy && apt-get upgrade -qy && apt-get install -qy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    libpq5 freetds-bin curl

# Install dev dependencies and mindsdb in editable mode
RUN --mount=type=cache,target=/root/.cache uv pip install -r requirements/requirements-dev.txt \
    && uv pip install --no-deps -e "."

# Copy configuration for the development environment
COPY docker/mindsdb_config.release.json /root/mindsdb_config.json

# Set environment variables for development
ENV PYTHONUNBUFFERED=1 \
    MINDSDB_DOCKER_ENV=1 \
    VIRTUAL_ENV=/venv \
    PATH=/venv/bin:$PATH

# Expose necessary ports for dev
EXPOSE 47334/tcp
EXPOSE 47335/tcp
EXPOSE 47336/tcp

ENTRYPOINT [ "bash", "-c", "python -Im mindsdb --config=/root/mindsdb_config.json --api=http,mysql,mongodb" ]

# Final production-ready image
FROM python:3.10-slim
WORKDIR /mindsdb

# Retain apt cache for faster subsequent builds
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install system dependencies for the production environment
RUN --mount=target=/var/lib/apt,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt update -qy && apt-get upgrade -qy && apt-get install -qy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    libpq5 freetds-bin curl

# Copy the virtual environment and mindsdb code from the build stage
COPY --link --from=build /venv /venv
COPY --link --from=build /mindsdb /mindsdb
COPY docker/mindsdb_config.release.json /root/mindsdb_config.json

# Set environment variables for the production environment
ENV PYTHONUNBUFFERED=1 \
    MINDSDB_DOCKER_ENV=1 \
    VIRTUAL_ENV=/venv \
    PATH=/venv/bin:$PATH

# Expose production ports
EXPOSE 47334/tcp
EXPOSE 47335/tcp
EXPOSE 47336/tcp

ENTRYPOINT [ "bash", "-c", "python -Im mindsdb --config=/root/mindsdb_config.json --api=http" ]
