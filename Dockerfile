# TODO(andreykurilin): port to xrally/xrally as soon as proper image will appear
FROM xrally/xrally-openstack:0.11.1

USER root
COPY . /home/rally/xrally_docker
WORKDIR /home/rally/xrally_docker
RUN pip install .
USER rally
