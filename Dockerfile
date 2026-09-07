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
# on the host.
EXPOSE 8000

# The entrypoint runs migrate and collectstatic and then execs this CMD, which is what
# makes `docker compose up` a single command with nothing to follow (REQ-N-003).
#
# --access-logfile - sends the request log to stdout so it appears in
# `docker compose logs` alongside everything else, rather than into a file inside a
# container nobody will open. Three workers is arbitrary but not thoughtless: enough
# that a slow request does not block the demonstration, few enough to be honest about
# a system backed by SQLite.
ENTRYPOINT ["/app/tools/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
