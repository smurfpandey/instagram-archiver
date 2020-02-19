FROM python:3.6-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV WORKDIR /app/

WORKDIR ${WORKDIR}

COPY Pipfile Pipfile.lock ${WORKDIR}

RUN pip install pipenv --no-cache-dir && \
    pipenv install --deploy --ignore-pipfile

COPY . $WORKDIR

CMD ["pipenv", "run", "python", "main.py"]