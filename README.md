<!--
Copyright 2024 SECO Mind Srl

SPDX-License-Identifier: Apache-2.0
-->

# Astarte device SDKs documentation

This repository contains documentation regarding the architecture and supported features for each
of the Astarte device libraries (from now on called SDK).

The documentation is built from a set of markdown files contained in the `sources` folder using
[`Sphinx`](https://www.sphinx-doc.org/en/master/).

## Prerequisites

Some configuration might be required before building the documentation.

### Setup a Python virtual environment

Running the following steps into a python virtual environment is recommended.

```shell
python3 -m venv ./.venv
source ./.venv/bin/activate
```

### Install Python dependencies

Python dependencies should be installed with the following command:

```shell
pip install -r requirements.txt
```

### Create empty directories

Some empty directories required by `Sphinx` are not versioned by git.
Those are not strictly required as their absence will only generate some warning during the
building process.
To avoid such warnings run the following shell commands.

```shell
mkdir ./source/_templates
```

### Build documentation

On systems with `make` support build the documentation using the following command.

```shell
make html
```
