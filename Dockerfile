FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.4.2
ENV PATH="/opt/poetry/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}

# Set working directory
WORKDIR /app

# Copy only dependency files first
COPY pyproject.toml poetry.lock ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root \
    && pip install 'open-autonomy[all]' \
    && pip install open-aea-ledger-ethereum

# Copy the rest of the application
COPY . .

# Generate Ethereum key and set up certificates at build time
RUN cd whale_watcher && \
    rm -f ethereum_private_key.txt && \
    yes | aea -s remove-key ethereum || true && \
    yes | aea -s generate-key ethereum && \
    yes | aea -s add-key ethereum && \
    yes | aea -s install && \
    yes | aea -s issue-certificates

# Command to run the agent
CMD ["sh", "-c", "cd whale_watcher && aea -s run"]