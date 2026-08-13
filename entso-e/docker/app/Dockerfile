FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SERVICE_LOG_DIR=/logs/
RUN apt-get update \
  && apt-get install --yes --no-install-recommends \
#    build-essential \
#    cmake \
#    curl \
    git \
    postgresql-client \
  && apt-get autoremove \
  && rm -rf /var/lib/apt/lists/*
# RUN apt-get update; apt-get install -y gcc libc-dev git
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY /requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN git clone --filter=blob:none --quiet  --depth=1 --branch docker-build  https://github.com/BlueBird-project/UBFlex.git /ubflex

##############################################################
##############################################################
##############################################################
##############################################################
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SERVICE_LOG_DIR=/var/log/

RUN apt-get update \
  && apt-get install --yes --no-install-recommends

COPY --from=builder /opt/venv /opt/venv

RUN mkdir app
RUN mkdir app/resources

COPY --from=builder /ubflex/ontology/imported /app/resources/ontologies
COPY --from=builder /ubflex/ontology/bluebirdontology/bluebird.ttl /app/resources/ontologies/bluebird.ttl

RUN mkdir config
RUN mkdir logs
RUN mkdir env
COPY /resources/deployment /app/resources/deployment
COPY /docker/app/config.yaml /config/config.yaml

COPY --from=builder /ubflex/ke.graph-patterns /app/resources/graph-patterns


########################################

RUN mkdir app/tm_entso_e
WORKDIR /app

#RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY /tm_entso_e /app/tm_entso_e
COPY /manage.py /app/manage.py
#COPY /resources/deployment /app/resources/deployment
#COPY --from=ontologies_dir . /app/resources/ontologies
#COPY /docker/app/config.yaml /config/config.yaml

#ENV KE_KI_CONFIG_PATH="/app/resources/deployment/ke_config.yaml"
ENV DB_INIT_SCRIPT_LOCATION="/app/resources/deployment/db/pg_init.sql"
ENV APP_LOGGING_CONF_PATH="/app/resources/deployment/logging.ini"
#ENV APP_USE_SCHEDULER=True
#ENV APP_USE_REST_API=True
#ENV APP_USE_KE_API=True
EXPOSE 8080
CMD ["/opt/venv/bin/python", "manage.py","-c" ,"/config/config.yaml"  ]