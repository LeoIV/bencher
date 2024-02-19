FROM python:3.11-slim as build

# Set environment variables
ENV LANG=C.UTF-8 \
    PATH="/root/.local/bin:$PATH" \
    POETRY_VIRTUALENVS_PATH=/opt/virtualenvs \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    MUJOCO_PY_MUJOCO_PATH=/opt/mujoco210 \
    PYENV_ROOT="/opt/.pyenv" \
    LD_LIBRARY_PATH=/opt/mujoco210/bin:/bin/usr/local/nvidia/lib64:/usr/lib/nvidia:$LD_LIBRARY_PATH
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV PATH $POETRY_HOME/bin:$PATH
ARG GITHUB_SHA
ENV GITHUB_SHA ${GITHUB_SHA}

# Install necessary programs
ARG BUILD_DEPENDENCIES="git curl g++ build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget \
    curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl swig \
    libglew-dev patchelf wget python3-dev"
ARG RUNTIME_DEPENDENCIES="libglfw3 gcc libosmesa6-dev libgl1-mesa-glx"
RUN apt-get update -y && apt-get install -y $BUILD_DEPENDENCIES $RUNTIME_DEPENDENCIES

# Configure Mujoco
WORKDIR /opt
RUN wget https://github.com/google-deepmind/mujoco/releases/download/2.1.0/mujoco210-linux-x86_64.tar.gz && \
    tar -xf mujoco210-linux-x86_64.tar.gz && \
    rm mujoco210-linux-x86_64.tar.gz && \
    rm -rf /tmp/mujocopy-buildlock

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.11 -
# Install Pyenv
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git /opt/.pyenv
# Clone bencher repository
ADD $GITHUB_SHA skipcache
RUN git clone --depth 1 https://LeoIV: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@github.com/LeoIV/bencher.git

# Install benchmarks
RUN --mount =type=cache,target=/root/.cache/pip \
    --mount =type=cache,target=/root/.cache/pypoetry \
    for dir in /opt/bencher/*; do \
        if [ -d "$dir" ]; then \
            if [ -f "$dir/.python-version" ]; then \
                cd $dir && \
                pyenv install $(cat .python-version) || echo "pyenv already installed version $(cat .python-version)" && \
                PATH="$PYENV_ROOT/shims:$PATH" poetry env use $(cat .python-version); \
            fi; \
            cd $dir && \
            poetry install -v && \
            if [ -f "$dir/.python-version" ]; then \
                poetry env use system; \
            fi; \
        fi; \
    done

# Clean up
RUN apt-get remove -y $BUILD_DEPENDENCIES && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /root/.cache/pypoetry/*

# Set the working directory to /opt/bencherclient
WORKDIR /opt/bencherclient

# Copy the entrypoint script into the Docker image
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Make the script executable
RUN chmod +x /docker-entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 50051

