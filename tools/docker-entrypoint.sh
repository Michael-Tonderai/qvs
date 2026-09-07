#!/bin/sh
# tools/docker-entrypoint.sh
#
# Container start-up. Runs the two steps that must happen before the server can
# usefully accept a request, then hands the process to whatever CMD the image carries.
#
# Why a script rather than `command:` in docker-compose.yml: this logic needs to
# explain itself, and YAML has nowhere to put the reason. CLAUDE.md Section 5 asks for
# the why in the file, and the report's DevOps workflow section is assembled from
# exactly these comments.
#
# Note on the interpreter: CLAUDE.md Section 3 requires every Python invocation on the
# development machine to go through .\.venv\Scripts\python.exe. That rule exists
# because Windows has several interpreters and a Store alias stub that can be reached
# by accident. Inside this image there is exactly one interpreter, installed at
# /usr/local/bin/python by the base image, so the bare name is unambiguous here. The
# rule is not being broken; the condition it guards against does not exist.
#
# Why `set -e`: a failed migration must stop the container. Without it gunicorn would
# start against a half-built schema and serve database errors that look like
# application bugs, which is a far more expensive thing to diagnose than a container
# that refused to start and said why.

set -e

echo "[entrypoint] applying migrations"
python manage.py migrate --noinput

# Collected on every start rather than baked into the image at build time. It costs
# about a second, and it means the static files always match the code that is running
# - a stale build-time collection is a class of bug this removes rather than manages.
echo "[entrypoint] collecting static files"
python manage.py collectstatic --noinput

# exec replaces this shell with gunicorn, so gunicorn becomes PID 1 and receives
# SIGTERM from `docker compose down` directly. Without exec the shell holds PID 1,
# does not forward the signal, and every shutdown waits out the ten-second timeout
# before the container is killed.
echo "[entrypoint] starting: $*"
exec "$@"
