# Updoc

- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)

A self hosted readthedocs.io-like documentation repository and hosting service.  The problem that this attempts to 
solve is that there aren't many easy to use solutions to store and host simple static html.  There are numerous 
tools out there like Sphinx (for Python and many other languages), pkgdown and pkgnet (for R), and SchemaSpy (for 
databases) that generate beautiful html documentation.  This allows users to host that documentation in a central 
location and easily categorize and share it.

## Quick Start

1. Build the docker image

```
git clone https://github.com/uptake/updoc
cd updoc
docker build -t updoc .
```

2. Run the docker image

```
docker run --name doc --rm -d -p 8080:80 updoc
```

3: Visit in your browser

```
# On Mac
open http://localhost:8080
```

You're all set!

## Features

- **Ready**: Supports AWS S3 and file system storage out of the box.
- **Extensible**: We made it really easy to support other storage backends.
- **Web UI**: Allows you to easily search through and view hosted static html.

## Usage

### Posting documentation tarballs to **docserver**

The way in which a folder is tar'd for distribution on docserver is **important**.  In order for the application to
correctly understand which category your documentation belongs to and the name of your documentation, the naming
of your tarball must follow the following format: ``<CATEGORY>_<DOCNAME>.tar.gz``.  When extracted, the tarball must
expand into a single folder named ``<DOCNAME>``, containing at minimum a ``<DOCNAME>/index.html``.

You can host static html with ``docserver`` using a POST request:

```
# bash
tarball=<PATH-TO-TARBALL>
curl -X POST -F file=@$tarball http://localhost:8080
```

If all goes well, you should receive the this message:

```
Document: <DOCNAME> was correctly uploaded, stored, and extracted.
```

## Configuration

Documentation storage: By default, ``docserver`` uses file system storage, but in a production environment in most
cases S3 or another object store is desirable. ``docserver`` supports AWS S3 out of the box. The recommended way to
set configuration options is using a ``.env`` file:

```
# .env
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID_HERE>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY_HERE>
AWS_DEFAULT_REGION=<YOUR_PREFERED_REGION_HERE>
AWS_DEFAULT_BUCKET=<YOUR_PREFERRED_DEFAULT_BUCKET_HERE>
AWS_BUCKET_FOLDER_PATH=<YOUR_PATH_TO_S3_FOLDER_IN_BUCKET>
```

The environment file can then be sourced when running from docker:

```
docker run --name doc --rm -d -p 8080:80 --env-file=.env updoc
```
