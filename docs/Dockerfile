# v9.1.18
FROM squidfunk/mkdocs-material@sha256:3f571e7f83702812ab63e73c912dfea762abecd12b3d9bae678211bb625ba9ad
# pip-compile --generate-hashes --output-file=requirements.txt requirements.in
COPY requirements.txt /tmp/
RUN pip install --require-hashes -r /tmp/requirements.txt
