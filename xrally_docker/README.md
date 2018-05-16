# The code base of xRally plugins for Docker platform

## Project structure

The root module of __xrally_docker__ project should not be overloaded, so let's 
keep it as simple as possible.
 
* __env__ module  
  a location of plugins for Environment xRally component 
  (ex Deployment component)
 
* __task__ module  
  a location of plugins for Task xRally component (i.e scenario, context, sla, 
  etc, plugins)
 
* __verify__ module  
  a location of plugins for Verification xRally component

* __service__ module  
  a python module with a helper class which simplify usage of docker client
