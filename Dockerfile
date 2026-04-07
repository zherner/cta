FROM python:3.12-slim as application

WORKDIR /app

#RUN apt-get update && apt-get install -y \
#    build-essential \
#    curl \
#    jq \
#    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

# Update lock file if pyproject.toml changed, then install
RUN (poetry lock || true) && poetry install --no-root

COPY main.py .

CMD ["python", "main.py"]
