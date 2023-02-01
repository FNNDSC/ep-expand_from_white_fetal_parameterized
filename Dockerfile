# Python version can be changed, e.g.
# FROM python:3.8
# FROM docker.io/fnndsc/conda:python3.10.2-cuda11.6.0
FROM docker.io/python:3.11.0-slim-bullseye

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="expand_from_white fetus CP experiment" \
      org.opencontainers.image.description="A ChRIS plugin wrapper for modified CIVET expand_from_white where stretch weight and laplacian weight can be scaled by parameters."

WORKDIR /usr/local/src/ep-expand_from_white_fetal_parameterized

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ARG extras_require=none
RUN pip install ".[${extras_require}]"

CMD ["expand_from_white_wrapper", "--help"]
