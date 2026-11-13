FROM spark:4.1.3-scala2.13-java17-python3-ubuntu

USER root

# rsync: Spark worker syncs jars from master; gosu: drop privileges after volume init
RUN apt-get update && \
    apt-get install -y --no-install-recommends rsync gosu && \
    rm -rf /var/lib/apt/lists/*

ARG ICEBERG_VERSION=1.12.0
ARG ICEBERG_JAR=iceberg-spark-runtime-4.1_2.13-${ICEBERG_VERSION}.jar

# Download Iceberg runtime JAR
RUN curl -fL -o /opt/spark/jars/${ICEBERG_JAR} \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.1_2.13/${ICEBERG_VERSION}/${ICEBERG_JAR}"

# Python deps for Jupyter / PySpark in the cluster (see requirements/README.md)
COPY requirements/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Spark configuration
COPY docker/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

# Entrypoint scripts
COPY docker/entrypoint-init.sh /opt/spark/workshop/entrypoint-init.sh
COPY docker/entrypoint-master.sh /opt/spark/workshop/entrypoint-master.sh
COPY docker/entrypoint-worker.sh /opt/spark/workshop/entrypoint-worker.sh
COPY docker/entrypoint-jupyter.sh /opt/spark/workshop/entrypoint-jupyter.sh
RUN chmod +x /opt/spark/workshop/*.sh

# Workshop code (shared utilities, notebooks)
WORKDIR /workspace
COPY shared/ /workspace/shared/
COPY requirements/ /workspace/requirements/

ENV PYTHONPATH=/workspace
ENV SPARK_MASTER=spark://spark-master:7077
ENV SPARK_DRIVER_HOST=jupyter-lab
ENV SPARK_DRIVER_BIND_ADDRESS=0.0.0.0

# Spark user in the official image has HOME=/nonexistent; give it a real home dir
RUN mkdir -p /home/spark && chown 185:185 /home/spark

# Stay as root; entrypoint-init.sh drops to SPARK_UID after fixing volume permissions
ENV SPARK_UID=185
ENV SPARK_GID=185
ENV HOME=/home/spark
