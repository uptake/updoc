FROM continuumio/miniconda3

RUN apt-get update -y
RUN apt-get -y install redis-server
RUN mkdir -p "/opt/docs/src/contrib/"

COPY . /opt/updoc/

WORKDIR /opt/updoc

RUN python setup.py install

RUN cd docs && \
    python -msphinx -M html . _build/ && \
    mv /opt/updoc/docs/_build/html /opt/updoc/docs/_build/readme && \
    mv /opt/updoc/docs/_build/readme /opt/updoc/docserver/static

EXPOSE 8000

CMD redis-server & gunicorn --preload -w 4 -b "0.0.0.0:80" --timeout 1800 docserver.server:app
