Rally Deployments
=================

Rally needs to be configured to use a Docker deployment to be able to
benchmark it.

To configure Rally to use a Docker deployment, you need create a
deployment configuration by supplying the endpoint and credentials, as follows:

  .. code-block::

    rally deployment create --file <one_of_files_from_this_dir> --name my_cloud

existing-default.json
---------------------

In case of using just regular local deployment of Docker, you may do not need
to configure any credentials. This is an example of such case.

existing-custom.json
--------------------

Register existing Docker deployment by specifying host, certs.
