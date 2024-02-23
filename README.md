[![Docker Build](https://github.com/LeoIV/bencher/actions/workflows/docker_build.yml/badge.svg)](https://github.com/LeoIV/bencher/actions/workflows/docker_build.yml)

# Docker Container

The Docker container can be pulled from the [Docker Hub](https://hub.docker.com/r/gaunab/bencher) or built locally.
It contains all benchmarks and dependencies and exposes the benchmark server via port 50051.

We give an exemplary usage of the Docker container in the [bencherclient](https://github.com/LeoIV/bencherclient)
repository.

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

### Starting the instance

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

### Evaluating a benchmark

We show how to run all benchmarks in the [`bencherclient`](https://github.com/LeoIV/bencherclient) repository.
You don't need to use this repository, it is mainly used to test the benchmarks.
The general setup to evaluate a benchmark is as follows.
First, install the [`bencherscaffold`](https://github.com/LeoIV/BencherScaffold) package:

```shell
pip install git+https://github.com/LeoIV/BencherScaffold
```

Then, you can use the following code to evaluate a benchmark:

```python
import grpc

from bencherscaffold.bencher_pb2 import BenchmarkRequest
from bencherscaffold.bencher_pb2_grpc import BencherStub

benchmarkname = "your-benchmark-name"
dimensions = 10  # number of dimensions of the benchmark

# this assumes that you have a running instance of the bencher server on localhost:50051
stub = BencherStub(
    grpc.insecure_channel(f"localhost:{50051}")
)

result = stub.evaluate_point(
    BenchmarkRequest(
        benchmark=benchmarkname,
        point={'values': [1] * dimensions}
    )
)

print(result)
```

### Available Benchmarks

The following benchmarks are available:

| Benchmark Name     | # Dimensions | Source(s) |
|--------------------|--------------|-----------|
| lasso-dna          | 180          | [^1],[^5] |
| lasso-simple       | 60           | [^1]      |
| lasso-medium       | 100          | [^1]      |
| lasso-high         | 300          | [^1],[^5] |
| lasso-hard         | 1000         | [^1],[^5] |
| lasso-leukemia     | 7129         | [^1]      |
| lasso-rcv1         | 47236        | [^1],[^2] |
| lasso-diabetes     | 8            | [^1]      |
| lasso-breastcancer | 10           | [^1]      |
| mopta08            | 124          | [^4],[^5] |
| maxsat60           | 60           | [^6],[^7] |
| maxsat125          | 125          | [^7]      |
| robotpushing       | 14           | [^3]      |
| rover              | 60           | [^3]      |
| mujoco-ant         | 888          | [^5]      |
| mujoco-hopper      | 33           | [^5]      |
| mujoco-walker      | 102          | [^5]      |
| mujoco-halfcheetah | 102          | [^5]      |
| mujoco-swimmer     | 16           | [^5]      |
| mujoco-humanoid    | 6392         | [^5]      |
| svm                | 388          | [^4],[^5] |

[^1]: [LassoBench](https://github.com/ksehic/LassoBench) (`
Šehić Kenan, Gramfort Alexandre, Salmon Joseph and Nardi Luigi, "LassoBench: A High-Dimensional Hyperparameter Optimization Benchmark Suite for Lasso", AutoML conference, 2022.`)
[^2]: The LassoBench paper states 19,959 features, but the number of features in the RCV1 dataset is 47,236.
[^3]: [TurBO](https://github.com/uber-research/TuRBO) (`David Eriksson, Michael Pearce, Jacob Gardner, Ryan D Turner and Matthias Poloczek "Scalable Global Optimization via Local Bayesian Optimization." NeurIPS 2019`)
[^4]: `High-dimensional Bayesian optimization with sparse axisaligned subspaces`
[^5]: `BAxUS`
[^6]: `BODi`
[^7]: `Bounce`