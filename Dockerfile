FROM docker.io/fnndsc/mni-conda-base:civet2.1.1-python3.11.0

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
