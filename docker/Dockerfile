# Example: Apache Superset with the superset-i18n-bcms translations added.
#
# Build context: a directory that contains superset/translations/<lang>/LC_MESSAGES/
# (an unpacked release zip, or dist/<version>/ from tools/build.py), e.g.
#   docker build -f docker/Dockerfile -t superset-bcms:6.1.0 dist/6.1.0
# See docker/README.md.

ARG SUPERSET_VERSION=6.1.0
FROM apache/superset:${SUPERSET_VERSION}

# Superset 6.1.0 cannot load the sr_Latn frontend pack (its bootstrap passes only the
# base language "sr", and /superset/language_pack/ rejects "sr_Latn"; fixed in 7.0).
# SERBIAN_SCRIPT=latin installs the sr_Latn files under the sr code instead, so the
# whole UI is Latin script when "sr" is selected. Default: Cyrillic under sr.
ARG SERBIAN_SCRIPT=cyrillic

USER root
COPY superset/translations/ /tmp/i18n-bcms/
RUN set -eu; \
    dest="$(python -c 'import importlib.util, os; print(os.path.join(os.path.dirname(importlib.util.find_spec("superset").origin), "translations"))')"; \
    echo "Superset translations directory: $dest"; \
    find /tmp/i18n-bcms -type d -exec chmod 755 {} +; \
    find /tmp/i18n-bcms -type f -exec chmod 644 {} +; \
    cp -r /tmp/i18n-bcms/. "$dest/"; \
    if [ "$SERBIAN_SCRIPT" = "latin" ]; then \
      test -d /tmp/i18n-bcms/sr_Latn || { echo "SERBIAN_SCRIPT=latin needs sr_Latn in the build context" >&2; exit 1; }; \
      mkdir -p "$dest/sr/LC_MESSAGES"; \
      cp /tmp/i18n-bcms/sr_Latn/LC_MESSAGES/messages.mo /tmp/i18n-bcms/sr_Latn/LC_MESSAGES/messages.json "$dest/sr/LC_MESSAGES/"; \
    fi; \
    rm -rf /tmp/i18n-bcms; \
    for f in "$dest"/*/LC_MESSAGES/messages.mo; do d="$(dirname "$f")"; test -f "$d/messages.json" && echo "installed: ${d#$dest/}"; done
USER superset
