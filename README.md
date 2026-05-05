# AiiDA Plugin for Octopus

This repository contains an AiiDA plugin for running Octopus calculations and parsing the retrieved results back into 
AiiDA data nodes.

## Development 

The [dockerfile](Dockerfile) uses AiiDA's docker image as the base layer:

```shell
docker pull aiidateam/aiida-core-with-services:latest
```

which automatically sets up the postgres database. One can check the docker logs or run `verdi status` to get the 
status of the services. AiiDA has some documentation on developing in docker [here](https://aiida.readthedocs.io/projects/aiida-core/en/latest/intro/run_docker.html.
The development environment containing AiiDA, octopus, Postopus and this plugin can be built with `docker compose`:

```shell
docker compose build
# Or for the older version of compose
docker-compose-v1 build
```

and interactively run with:

```shell
docker compose run --rm app
# Or for the older version of compose
docker-compose-v1 run --rm app
```

After initialising the container:

```shell
# Install postopus from the mounted directory
pip install -e /workspace/postopus/.
```

```shell
# Install the octopus AiiDA plugin. 
pip install -e .
pip install -e .[tests]
```

and run the tests in the container (from `/workspace/aiida-plugin`) with:

```shell
pytest
```

If a test is not written with `pytest`, then it should be run through `verdi`:

```shell  
verdi run path/to/launch.py  
```
