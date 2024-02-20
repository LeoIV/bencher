[![Docker Build](https://github.com/LeoIV/bencher/actions/workflows/docker_build.yml/badge.svg)](https://github.com/LeoIV/bencher/actions/workflows/docker_build.yml)

# Docker Container

The Docker container can be pulled from the [Docker Hub](https://hub.docker.com/r/gaunab/bencher) or built locally.
It contains all benchmarks and dependencies and exposes the benchmark server via port 50051.

We give an exemplary usage of the Docker container in the [bencherclient](https://github.com/LeoIV/bencherclient) repository.


```shell
pwd # /path/to/bencher
docker build -t bencher .
docker run -p 50051:50051 --name bencher-container bencher
```

**or**

```shell
docker pull gaunab/bencher:latest
docker run -p 50051:50051 --name bencher-container gaunab/bencher:latest
```

# Apptainer / Singularity Container

You can build an Apptainer container from the Docker image:

```shell
Bootstrap: docker
From: gaunab/bencher:latest
Namespace:
Stage: build

%environment
    export LANG=C.UTF-8
    export PATH="/root/.local/bin:$PATH"

%post
    cd /opt
    git clone your-repo
    cd your-repo && install your-dependencies

%startscript
    bash -c "/docker-entrypoint.sh"

%runscript
    bash -c "your-command-to-run-your-app"
```
This will create an Apptainer container with the Docker image `gaunab/bencher:latest` and the repository `your-repo`
with the dependencies `your-dependencies` installed.

## Usage

```shell
apptainer build container.sif your-apptainer-file
```

### Start the Apptainer instance

This starts all the benchmarks in the container (as defined in the `startscript` of the Apptainer file).

```shell
apptainer instance start container.sif your-instance-name
```

### Run your command that depends on the benchmarks

This runs your command in the instance `your-instance-name` as defined in the `runscript` of the Apptainer file.

```shell
apptainer run instance://your-instance-name
```