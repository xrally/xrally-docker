# xrally-docker

xRally plugins for [Docker engine](https://www.docker.com).

## What is it?!

Originally, it was created as a quick proof-of-concept to show ability of
[Rally](https://github.com/openstack/rally) to test platforms other than
[OpenStack](https://www.openstack.org/). After the first preview,
it became obvious that it should be developed as a complete package.

__xrally_docker__ is a pack of xRally plugins for execution different workloads
at the top of Docker Engine. Such workloads can be used as like for testing
environments with Docker or testing behaviour of specified docker image.

## How to use?!

### Install package

__xrally_docker__ package is configured to be auto-discovered by Rally. Since
rally package is a dependency of __xrally_docker__ , so to start using
__xrally_docker__ you need to install just one package:

```commandline

pip install xrally_docker

```

### Specify entry-point of docker engine to use

The next step is to specify entry-point to docker, i.e. create rally 
environment. There are 2 way to do it:

1. Specify environment specification manually. For a simple case (no cert, 
   tls, etc), it looks like ``{"docker@existing": {}}``.
2. Create environment specification from system environment variables 
   (supported by Rally >= 0.11.2) using 
   ``rally env create --name example --from-sysenv`` command. An expected 
   system variables are the same as native docker client supports.

### Check that Rally can access the docker

First of all try to execute ``rally env check`` command. It checks all 
platforms of the environment to be available. If it does not show any errors 
for communicating with docker, go and execute any task against docker. 
If is fails, try to execute the command again with ``--detailed`` flag.

Also, you can use ``rally env info`` command for the same purpose. Unlike 
``rally env check`` it will not only check the platforms, but print some 
information about them. In case of docker platform, it will print the similar 
to ``docker --version`` data.

### Execute a workload against docker

Here is a simple workload:

```yaml

---
  version: 2
  title: Simple task with only one workload
  subtasks:
    -
      title: a subtask with one workload
      description: This workload should run a container from "ubuntu" 
                   image and execute simple command.
      scenario:
        Docker.run_container:
          image_name: "ubuntu"
          command: "echo 'Hello world!'"
      runner:
        constant:
          times: 10
          concurrency: 2
      sla:
        failure_rate:
          max: 0
```

This task will download _ubuntu_ image first, if it does not present in the 
system. Then, it will run 10 containers from the image with 2 concurrency and 
execute a  simple command. The output of the command will be saved as 
TextArea and will be available via json and html reports.

See plugin references for the full list of available plugins for docker 
platform to combine workloads. 

## Known issues

This package works fine, but you need to install the proper version of Docker
client which suits your Docker API version.
