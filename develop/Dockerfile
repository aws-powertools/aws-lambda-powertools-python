# v9.1.18
FROM squidfunk/mkdocs-material@sha256:d063d8460d449d5094da4b58c6e9b2aa8da869bb3a113a21401e0fe00bb8a628
# pip-compile --generate-hashes --output-file=requirements.txt requirements.in
COPY requirements.txt /tmp/
RUN pip install --require-hashes -r /tmp/requirements.txt
