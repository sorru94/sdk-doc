# (C) Copyright 2024, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

"""docs.py

West extension that can be used to build doxygen documentation for this project.

Checked using pylint with the following command (pip install pylint):
python -m pylint --rcfile=./.pylintrc ./*.py
Formatted using black with the following command (pip install black):
python -m black --line-length 100 ./*.py
Import sorted using isort with the following command (pip install isort):
isort .
"""

# pylint: disable=duplicate-code

import os
import re
import shutil
import tempfile
from pathlib import Path

from git import Repo

STANDARD_VERSION_PATTERN = r"^v(\d+)\.(\d+)\.(\d+)$"


def version_is_standard_release(version: str):
    """Check if a version is a standard release. I.E. not a pre-release.

    Args:
      version (str): Version to check.

    Returns:
      bool: True if standard release, False otherwise.
    """
    return bool(re.match(STANDARD_VERSION_PATTERN, version))


sdk_repos = [
    ("csharp", "https://github.com/astarte-platform/astarte-device-sdk-csharp.git", []),
    ("python", "https://github.com/astarte-platform/astarte-device-sdk-python.git", []),
    ("elixir", "https://github.com/astarte-platform/astarte-device-sdk-elixir.git", []),
    ("esp32", "https://github.com/astarte-platform/astarte-device-sdk-esp32.git", []),
    ("java", "https://github.com/astarte-platform/astarte-device-sdk-java.git", []),
    ("qt5", "https://github.com/astarte-platform/astarte-device-sdk-qt5.git", []),
    ("go", "https://github.com/astarte-platform/astarte-device-sdk-go.git", []),
    ("rust", "https://github.com/astarte-platform/astarte-device-sdk-rust.git", []),
]


def group_get_started_files(sdks_dir: Path, get_started_dir: Path):
    """Group the get started files from the repos in sdk_repos in a single temporary directory.

    Args:
      sdks_dir (Path): The temporary directory where to place the sdks.
      get_started_dir (Path): The temporary directory where to place the get started files.
    """

    for name, git_url, get_started_files in sdk_repos:
        repo_dir = sdks_dir.joinpath(name)
        get_started_file = repo_dir.joinpath("get_started.md")

        # Clone the SDK repository
        repo = Repo.clone_from(git_url, repo_dir)

        # Get the latest tag
        tags = [tag for tag in reversed(repo.tags) if version_is_standard_release(tag.name)]
        if tags:
            # Latest tag is also the latest version
            tag = tags[0]

            # Get the latest version in the format 'vX.X' without the patch
            match = re.match(STANDARD_VERSION_PATTERN, tag.name)
            major, minor, _ = match.groups()
            version_no_patch = f"{major}.{minor}"

            # Checkout latest release
            repo.git.checkout(tag)
        else:
            version_no_patch = "latest"

        # Check if this repo contains a get_started.md file and in case copy it
        if get_started_file.exists() and get_started_file.is_file():
            print(
                f"Found get_started.md for repo {name} and tag {tag.name if tag else version_no_patch}"
            )
            destination_file = get_started_dir / f"get_started_{name}_{version_no_patch}.md"
            shutil.copy2(get_started_file, destination_file)
            get_started_files.append((version_no_patch, destination_file))


def move_get_started_files(get_started_dir: Path):
    """Move the get started files to this repo and also updated the toctree of the get_starte.md.

    Args:
      get_started_dir (Path): The temporary directory where get started files are.
    """

    # Copy all created get started pages to the main repo
    skd_docs_get_started_dir = Path(os.getcwd()).joinpath("source").joinpath("get_started")
    for get_started_file in get_started_dir.iterdir():
        shutil.copy2(get_started_file, skd_docs_get_started_dir)

    # Find the additional content for the toctree
    toctree_additional_content = []
    for name, _, get_started_files in sdk_repos:
        for version_no_patch, get_started_file in get_started_files:
            toctree_additional_content.append(
                f"Get started with {name.capitalize()} ({version_no_patch}) <get_started/{get_started_file.name}>\n"
            )

    # Update the toctree of get_started.md
    api_docs_file = Path(os.getcwd()).joinpath("source").joinpath("get_started.md")
    with open(api_docs_file, "r+", encoding="utf-8") as file:
        file_lines = file.readlines()
        start_line = None
        end_line = None
        for idx, line in enumerate(file_lines):
            if line.startswith(r":maxdepth: 1"):
                start_line = idx + 1
            elif start_line and line.startswith(r"```"):
                end_line = idx
                break

        toctree_content = toctree_additional_content + file_lines[start_line:end_line]
        toctree_content = [
            x for i, x in enumerate(toctree_content) if i == toctree_content.index(x)
        ]

        file_lines = file_lines[:start_line] + toctree_content + file_lines[end_line:]
        file.seek(0, 0)
        file.writelines(file_lines)


if __name__ == "__main__":

    with tempfile.TemporaryDirectory(prefix="sdk_doc_") as temp_dir:
        temp_get_started_dir = Path(temp_dir).joinpath("get_started")
        temp_get_started_dir.mkdir()

        group_get_started_files(Path(temp_dir), temp_get_started_dir)

        move_get_started_files(temp_get_started_dir)
