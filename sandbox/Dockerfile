# Vital Source sandbox. Build from the repo root:
#   docker build -f sandbox/Dockerfile -t anarchygames/learn-linux:dev .

FROM debian:trixie-slim AS base

ENV LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

# Slim images strip man pages and docs via dpkg path excludes. Lesson 0 needs them,
# so drop the excludes and reinstall what is already there to get its pages back.
RUN rm -f /etc/dpkg/dpkg.cfg.d/docker /etc/dpkg/dpkg.cfg.d/excludes \
 && apt-get update \
 && dpkg-query -W -f='${Package}\n' | xargs apt-get install -y --reinstall --no-install-recommends \
 && apt-get install -y --no-install-recommends \
      man-db manpages less nano vim-tiny file tree curl wget ca-certificates \
      sudo python3 bash-completion procps tar gzip xz-utils bzip2 zip unzip tealdeer \
 && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash --groups sudo learner \
 && echo 'learner:learner' | chpasswd \
 && mkdir -p /var/lib/drill \
 && chown learner:learner /var/lib/drill

# tldr pages are fetched once at build time so the sandbox works offline.
USER learner
RUN tldr --update
USER root

FROM base

COPY sandbox/theme/ /etc/learn-linux/
RUN cat /etc/learn-linux/bashrc >> /home/learner/.bashrc

COPY drill/drill/ /usr/local/lib/drill/drill/
COPY drill/run.py /usr/local/lib/drill/run.py
RUN printf '#!/bin/sh\nexec python3 /usr/local/lib/drill/run.py "$@"\n' > /usr/local/bin/drill \
 && chmod 755 /usr/local/bin/drill

USER learner
WORKDIR /home/learner
CMD ["bash", "-l"]
