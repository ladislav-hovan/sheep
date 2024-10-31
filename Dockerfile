ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering
ENV PYTHONUNBUFFERED=1

# Keeps Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Create a non-privileged user that the app will run under
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "${UID}" \
    --shell "/bin/bash" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds
# Leverage a bind mount to requirements.txt to avoid having to copy them into this layer
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container
COPY . /sheep_src

# Install the application
RUN python -m pip install -e /sheep_src

# Test the application
WORKDIR /sheep_src
RUN python -m pip install pytest
RUN pytest

# Clean up some space
RUN python -m pip uninstall -y pytest
RUN rm -rf /root/.cache/pip

# Create the working directory
WORKDIR /app
RUN chown appuser /app

# Switch to the non-privileged user to run the application
USER appuser

# Run the bash shell
CMD ["bash"]