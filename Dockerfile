# Pull base image
FROM python:3.11-slim@sha256:8eb5fc663972b871c528fef04be4eaa9ab8ab4539a5316c4b8c133771214a617

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
