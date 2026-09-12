# Dockerfile
#
# QVS runtime image. Single stage on python:3.12-slim.
#
# Why single stage: the dependency set is Django, gunicorn and whitenoise - all pure
# Python or shipping manylinux wheels, so nothing is compiled and there are no build
# artefacts to discard. A multi-stage build would add indirection to save nothing
# measurable, and D-008 exists to make deployment demonstrable rather than elaborate.
#
# Why 3.12-slim rather than 3.12.10-slim: D-010 pins the minor version across the
# local .venv, CI and this image so a failure reproduces identically in all three.
# The patch version floats for the same reason requirements.txt uses ranges rather
# than a lockfile (D-016) - security patches arrive without a dependency-update
# workflow this project has no time to run. The cost, that builds are not
# byte-identical across time, is the one D-016 already accepted and named.

FROM python:3.12-slim

# PYTHONDONTWRITEBYTECODE keeps .pyc files out of layers where they are never reused.
# PYTHONUNBUFFERED matters more: without it gunicorn's start-up output sits in a pipe
# buffer and `docker compose logs` shows nothing until the buffer fills, which looks
# like a hung container on camera.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies are copied and installed before the application code so that editing a
# view does not invalidate the pip layer. requirements.txt changes rarely; the code
# changes every commit. This ordering is the difference between a rebuild of seconds
# and one of minutes, which is felt most on the day the video is being recorded.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

# Why a non-root user: a compromised process running as root is root inside the
# container, and the assignment lists advanced security mechanisms among its bonus
# criteria. /data is created and owned here because the named volume mounts over it
# and takes this ownership when Docker creates it for the first time - without this,
# the volume arrives owned by root and the entrypoint's migrate cannot write the
# SQLite file.
RUN useradd --create-home --uid 10001 qvs \
 && mkdir -p /data /app/staticfiles \
 && chown -R qvs:qvs /app /data

# Executable bit set while still root. The repository is developed on Windows, which
# does not carry the bit through git, so setting it here rather than relying on the
# checkout is what makes the entrypoint runnable on Linux.
RUN chmod +x /app/tools/docker-entrypoint.sh

USER qvs

# Documentation rather than a port publication - docker-compose.yml maps this to 8020
# on the host. The managed platform ignores EXPOSE entirely and routes to whatever
# port the process actually listens on, which is why the bind below reads $PORT.
EXPOSE 8000

# The entrypoint runs migrate and collectstatic and then execs this CMD, which is what
# makes starting the system a single step with nothing to follow (REQ-N-003).
#
# WHY sh -c RATHER THAN A BARE ARGUMENT LIST. The exec form of CMD is passed straight
# to execve with no shell, so ${PORT} would reach gunicorn as six literal characters.
# The managed platform assigns a port through $PORT and routes to it; a hard-coded
# 8000 would start cleanly, listen on the wrong port, fail the platform's health check
# and never receive traffic - a silent failure that looks like a broken application.
# The inner `exec` keeps the process identity the entrypoint's own exec establishes,
# so gunicorn is still PID 1 and still receives SIGTERM directly. Default 8000 keeps
# `docker compose up` working unchanged, where nothing sets $PORT.
#
# --access-logfile - sends the request log to stdout so it appears in the platform's
# log stream and in `docker compose logs` alongside everything else, rather than into
# a file inside a container nobody will open.
#
# WEB_CONCURRENCY rather than a fixed worker count: three is right for a laptop and
# wrong for a 512 MB free instance, where three copies of Django plus collectstatic
# is how an out-of-memory kill arrives mid-demonstration. The platform sets it to 2 in
# render.yaml; local runs keep 3.
ENTRYPOINT ["/app/tools/docker-entrypoint.sh"]
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --access-logfile -"]
