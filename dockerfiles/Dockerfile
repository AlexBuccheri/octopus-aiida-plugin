# Commands
# ---------------------------
# docker build -t aiida_base .
#
FROM ubuntu:lunar

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y  \
    curl \
    git  \
    python3-dev  \
    python3-pip  \
    virtualenv

RUN apt-get update && apt-get install -y  \
    postgresql  \
    postgresql-server-dev-all  \
    postgresql-client  \
    rabbitmq-server

# Locales for database
RUN apt-get update && apt-get install -y locales language-pack-en

# TODO(Alex) Check this works
#RUN /bin/bash -c 'echo "eval \"$(_VERDI_COMPLETE=source verdi)\"" >> /root/.bashrc'

# TODO(Alex) Get venv to persist, and be the login shell
# PEP 668 adopted in this version of Ubuntu, so use a venv for all further installations
RUN virtualenv /.virtualenvs/aiida

RUN . /.virtualenvs/aiida/bin/activate && pip install aiida-core

# TODO(Alex) Get service to start upon starting the container
# Start PostgreSQL service
#CMD ["service", "postgresql", "start"]
