=============
xrally_docker
=============

xRally plugins for `Docker engine <https://www.docker.com>`_.

What is it?!
------------

Originally, it was created as a quick proof-of-concept to show ability of
`Rally <https://github.com/openstack/rally>`_ to test platforms other than
`OpenStack <https://www.openstack.org/>`_. After the first preview,
it became obvious that it should be developed as a complete package.

**xrally_docker** is a pack of xRally plugins for execution different workloads
at the top of Docker Engine. Such workloads can be used as like for testing
environments with Docker or testing behaviour of specified docker image.

How to use?!
------------

**xrally_docker** package is configured to be auto-discovered by Rally. Since
rally package is a dependency of **xrally_docker** , so to start using
**xrally_docker** you need to install just one package:

  .. code-block:: console

    pip install xrally_docker


Know issues
-----------

This package works fine, but you need to install the proper version of Docker
client which suits your Docker API version.
