FROM python:3.8
MAINTAINER Lars van Rhijn

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE equestria.settings.production_docker
ENV PATH /root/.poetry/bin:${PATH}

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

WORKDIR /equestria/src
COPY resources/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY resources/uwsgi.sh /usr/local/bin/uwsgi.sh
COPY resources/background.sh /usr/local/bin/background.sh
COPY poetry.lock pyproject.toml /equestria/src/

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends postgresql-client && \
    rm --recursive --force /var/lib/apt/lists/* && \
    \
    mkdir --parents /equestria/src/ && \
    mkdir --parents /equestria/log/ && \
    mkdir --parents /equestria/static/ && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    poetry config --no-interaction --no-ansi virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-dev


COPY equestria /equestria/src/website/