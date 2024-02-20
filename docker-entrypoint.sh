#!/bin/bash

echo "Container was started"

export POETRY_VIRTUALENVS_PATH=/opt/virtualenvs
export POETRY_HOME=/opt/poetry
export PATH="/opt/poetry/bin:$PATH"
export POETRY_VIRTUALENVS_IN_PROJECT=true

# loop over all dirs in /opt/bencher and execute poetry run start-benchmark-service for each
# this also starts the coordinating server
for dir in /opt/bencher/*; do
  echo "Checking $dir"
  if [ -d "$dir" ]; then
      echo "Starting benchmark service for $dir"
      (
      cd "$dir" || exit
      bash -c "PATH='/opt/poetry/bin:$PATH' poetry run start-benchmark-service & >> /opt/bencher/bencher.log 2>&1"
      )
  fi
done

# Keep container running
tail -f /opt/bencher/bencher.log
