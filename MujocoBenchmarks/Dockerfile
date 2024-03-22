FROM python:3.11-slim as build

# Set environment variables
ENV LANG=C.UTF-8 \
    PATH="/root/.local/bin:$PATH" \
    POETRY_VIRTUALENVS_PATH=/opt/virtualenvs \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    MUJOCO_PY_MUJOCO_PATH=/opt/mujoco210 \
    PYENV_ROOT="/opt/.pyenv" \
    LD_LIBRARY_PATH=/opt/mujoco210/bin:/bin/usr/local/nvidia/lib64:/usr/lib/nvidia:$LD_LIBRARY_PATH \
    LIBSVMDATA_HOME=/tmp
ENV PATH $POETRY_HOME/bin:$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Install necessary programs
ARG BUILD_DEPENDENCIES="git curl g++ build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl swig \
    libglew-dev patchelf python3-dev"
ARG RUNTIME_DEPENDENCIES="libglfw3 gcc libosmesa6-dev libgl1-mesa-glx"
WORKDIR /opt

COPY . /opt

# Install software, configure Mujoco, Pyenv and Poetry
RUN apt-get update -y && apt-get install -y $BUILD_DEPENDENCIES $RUNTIME_DEPENDENCIES && \
    curl -LO https://github.com/google-deepmind/mujoco/releases/download/2.1.0/mujoco210-linux-x86_64.tar.gz && \
    tar -xf mujoco210-linux-x86_64.tar.gz && \
    rm mujoco210-linux-x86_64.tar.gz && \
    rm -rf /tmp/mujocopy-buildlock && \
    curl -sSL https://install.python-poetry.org | python3.11 - && \
    git clone --depth=1 https://github.com/pyenv/pyenv.git /opt/.pyenv
# Cachebust
ARG CACHEBUST=1

RUN if [ -f ".python-version" ]; then \
        pyenv install $(cat .python-version) || echo "pyenv already installed version $(cat .python-version)" && \
        PATH="$PYENV_ROOT/shims:$PATH" poetry env use $(cat .python-version); \
    fi; \
    poetry install -v && \
    if [ -f ".python-version" ]; then \
        poetry env use system; \
    fi; \
    apt-get remove -y $BUILD_DEPENDENCIES && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /root/.cache/pypoetry/* && \
    chmod +x /opt/entrypoint.sh

# Clone bencher repository and install benchmarks, clean up, and make entrypoint script executable
#RUN --mount=type=cache,target=/root/.cache/pip \
#    --mount=type=cache,target=/root/.cache/pypoetry \
#    git clone --depth 1 https://LeoIV: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@github.com/LeoIV/bencher.git && \
#    for dir in /opt/bencher/*; do \
#        if [ -d "$dir" ]; then \
#            if [ -f "$dir/.python-version" ]; then \
#                cd $dir && \
#                pyenv install $(cat .python-version) || echo "pyenv already installed version $(cat .python-version)" && \
#                PATH="$PYENV_ROOT/shims:$PATH" poetry env use $(cat .python-version); \
#            fi; \
#            cd $dir && \
#            poetry install -v && \
#            if [ -f "$dir/.python-version" ]; then \
#                poetry env use system; \
#            fi; \
#        fi; \
#    done && \
#    apt-get remove -y $BUILD_DEPENDENCIES && \
#    apt-get autoremove -y && \
#    rm -rf /var/lib/apt/lists/* && \
#    rm -rf /root/.cache/pip/* && \
#    rm -rf /root/.cache/pypoetry/* && \
#    chmod +x /entrypoint.py

# Set the entrypoint
ENTRYPOINT /opt/entrypoint.sh

EXPOSE 50057

