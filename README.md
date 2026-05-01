# Test Project for Developing an AIIDA Plugin for Octopus


## Developing in Docker 

The main [dockerfile](Dockerfile) uses AIIDA's docker image as the base layer:

```shell
docker pull aiidateam/aiida-core-with-services:latest
```

which automatically sets up the postgres database. One can check the docker logs or run `verdi status` to get the 
status of the services. AIIDA has some documentation on developing in docker [here](https://aiida.readthedocs.io/projects/aiida-core/en/latest/intro/run_docker.html.

A docker image is built with:

```shell
#DOCKER_BUILDKIT=1 docker compose build
# my outdated installation
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose-v1 build
```

and interactively run with:

```shell
# docker compose run --rm app
# my outdated installation
docker-compose-v1 run --rm app
```

## Installing the oct_plugin Project and Running the Plugin

Developing a basic plugin is documented [here](https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/plugin_codes.html)
After initialising the container:

```shell
# Install postopus
cd /workspace/postopus
pip install -e .
```

```shell
# Install the octopus AiiDA plugin. 
cd /workspace/aiida-plugin
pip install -e .
```

To run from the plugin root (`/workspace/aiida-plugin`):

```shell
# Run the job
cd job
verdi run launch.py
```

For more examples, see the [AIIDA plugin repository](https://github.com/PSDI-Biomolecular-team/aiida-gromacs/tree/master/aiida_gromacs, and various plugins - for example 
[GROMACS](https://github.com/PSDI-Biomolecular-team/aiida-gromacs/tree/master/aiida_gromacs).


## (Attempting) to Building a Dockerfile from Scratch

Rather than use `aiidateam/aiida-core-with-services` base image, one can attempt to build their
own dockefile. This is described below

Configuring with Pycharm:
 * Port 5432:5432
 * Host mapping /Users/alexanderbuccheri/Codes/oct_plugin/pg_data:/var/lib/postgresql/data

This should all go into the dockerfile:

**locale-gen**

```dockerfile
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_MESSAGES=POSIX
```

**Setting up the Database**

```shell
# Need to ensure the service starts.
service postgresql start
# Switch to `postgres` superuser
su -l postgres
# Create user, then database
psql -c "CREATE USER aiida WITH PASSWORD 'null';"
# Can't get the LC to be picked up, so I've dropped it when creating the database
# # CREATE DATABASE aiidadb OWNER aiida ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
 psql -c "CREATE DATABASE aiidadb OWNER aiida ENCODING 'UTF8' TEMPLATE=template0;"
 psql -c "GRANT ALL PRIVILEGES ON DATABASE aiidadb to aiida;"
# Test the database having exited `postgres` superuser: 
psql -h localhost -d aiidadb -U aiida -W
```

Some additional commands worth noting:

```shell
# Delete Database
 psql -c "DROP DATABASE aiidadb;"
# Delete user
 psql -c "DROP USER aiida;"
```

**Activate venv**

Get the dockerfile to switch to a venv:

```shell
source /.virtualenvs/aiida/bin/activate
```

**Set up Verdi**

```shell
verdi quicksetup
```

Configuration details:
* Profile name: Alex-debug
* E-mail: alexander.buccheri@mpsd.mpg.de
* Alex Buccheri MPSD

