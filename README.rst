==================================
Docker plugins for Rally Framework
==================================


What is it?!
------------

.. warning:: It is just proof of concept

This is an example of rally plugins for Docker platform. It includes:

* all required base classes(inner rally stuff);
* the scenario ``Docker.run_container`` which launches a container and executes
  the command in it
* the simple context for polling images or discovering existing ones.

How to use?!
------------

Rally 0.10.0 supports auto-discovering plugins by entry-point. It simplifies a
lot of things. To install these plugins, you need to install that repository
just like regular python package and Rally will find it.

Know issues
-----------

This package works fine, but you need to install the proper version of Docker
client which suits your Docker API version.
