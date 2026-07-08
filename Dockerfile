# Pull base image
FROM python:3.12-slim@sha256:86d3e4424d5e963e60594a3a6b4d597cc4d41f5152fe67a97a40dca9ea092475

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y unzip wget

RUN pip install --no-cache-dir -U pip==23.2.1

# NOTE: the Gateway assumes that the python3 binary is available at /usr/local/bin/python3
# If you are using a different python3 binary, please create a symlink to it.
# For example, if your python3 binary is located at /path/to/python3, you can uncomment
# the following line:
# RUN ln -s <path>/to/python3 /usr/local/bin/python3

RUN mkdir -p /workspace
RUN mkdir -p /apheris/src

WORKDIR /workspace/

COPY requirements*.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH="/apheris/src/:/workspace:/workspace/custom"

COPY --chmod=755 src/logistic_regression_quickstart/secure_runtime/ /usr/secure_runtime/src/

COPY src/ /apheris/src/

RUN addgroup nvflare-run \
    --gid 3333 &&\
    useradd nvflare-run \
    --gid 3333 \
    --uid 3333 \
    --no-create-home && \
    chown -R nvflare-run:nvflare-run /workspace

RUN chmod -R 777 /workspace
USER nvflare-run
