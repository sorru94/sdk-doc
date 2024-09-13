# (C) Copyright 2024, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

"""link_api_docs.py

Can be used to generate the links to the API documentation.

Checked using pylint with the following command (pip install pylint):
python -m pylint --rcfile=./.pylintrc ./*.py
Formatted using black with the following command (pip install black):
python -m black --line-length 100 ./*.py
Import sorted using isort with the following command (pip install isort):
isort .
"""

# pylint: disable=duplicate-code

import argparse
import os
import sys
import tempfile
from pathlib import Path
from string import Template

from git import Repo


def get_api_docs_urls():
    """Get the SDKs APIs documentation URLs.

    Returns:
      touple: The first element is the base path for the SDKs API documentation repository. While
              the second is a dictionary containing the subdirectories present in the base path.
    """
    with tempfile.TemporaryDirectory(prefix="sdk_doc_") as temp_dir:
        docs_dir = Path(temp_dir).joinpath("docs")
        Repo.clone_from("https://github.com/astarte-platform/docs.git", docs_dir)
        api_docs = {}
        for api_docs_dir in docs_dir.joinpath("device-sdks").iterdir():
            if api_docs_dir.is_dir() and api_docs_dir.name != "common":
                for release_dir in api_docs_dir.iterdir():
                    if release_dir.name not in ["latest", "snapshot"]:
                        api_docs.setdefault(api_docs_dir.name, []).append(release_dir.name)
                api_docs[api_docs_dir.name].sort()

    return ("https://docs.astarte-platform.org/device-sdks", api_docs)


def generate_exernal_top_toctree_entry(base_url: str, platform: str, release: str):
    """Generate a toctree entry for the top file api_docs.md

    Args:
      base_url (str): Base URL for the API docs.
      platform (str): Platform for the entry.
      release (str): Release version for the entry.

    Returns:
      str: The toctree entry.
    """
    return f"{platform.capitalize()} APIs <{base_url}/{platform}/{release}/api>\n"


def generate_exernal_sub_toctree_entry(base_url: str, platform: str, release: str):
    """Generate a toctree entry for the sub markdown files

    Args:
      base_url (str): Base URL for the API docs.
      platform (str): Platform for the entry.
      release (str): Release version for the entry.

    Returns:
      str: The toctree entry.
    """
    return f"{platform.capitalize()} v{release} APIs <{base_url}/{platform}/{release}/api>\n"


platform_md_template = Template(
    r"""# ${platform_cap} APIs documentation

Find the ${platform_cap} documentation at the following links:
```{toctree}
:maxdepth: 1
${toctree_content}
```
"""
)


def generate_toctree_and_markdown_from_api_docs_urls(urls):
    """Generate the toctree entries to add in the api_docs.md file and the markdown files
    for each platform with multiple versions.

    Args:
      urls (touple): Object returned by get_api_docs_urls.

    Returns:
      touple: The first element is the toctree for the api_docs.md file, the second is a list
              of additional markdown files.
    """
    top_toctree = []
    additional_md = {}
    base_url, platforms = urls
    for platform, versions in platforms.items():
        if len(versions) == 1:
            top_toctree.append(generate_exernal_top_toctree_entry(base_url, platform, versions[0]))
        else:
            top_toctree_entry = f"{platform.capitalize()} APIs <api_docs/{platform}.md>\n"
            if top_toctree_entry not in top_toctree:
                top_toctree.append(top_toctree_entry)
            sub_toctree = []
            for version in versions:
                sub_toctree.append(generate_exernal_sub_toctree_entry(base_url, platform, version))
            additional_md[f"{platform}.md"] = platform_md_template.substitute(
                platform_cap=platform.capitalize(), toctree_content="".join(reversed(sub_toctree))
            )

    return (top_toctree, additional_md)


def store_toctree_and_markdown(top_toctree, additional_md):
    """Store the generated toctree entries and markdown files in their location.

    Args:
      top_toctree (list): Toctree entries for the file api_docs.md.
      additional_md (dict): Additional markdown generated for different releases.
    """

    # Store the additional files in the correct directory
    output_dir = Path(os.getcwd()).joinpath("source").joinpath("api_docs")
    output_dir.mkdir(exist_ok=True)
    for filename, content in additional_md.items():
        file_path = output_dir / filename
        file_path.write_text(content)

    # Update the toctree of api_docs.md
    api_docs_file = Path(os.getcwd()).joinpath("source").joinpath("api_docs.md")
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

        toctree_content = top_toctree + file_lines[start_line:end_line]
        toctree_content = [
            x for i, x in enumerate(toctree_content) if i == toctree_content.index(x)
        ]

        file_lines = file_lines[:start_line] + toctree_content + file_lines[end_line:]
        file.seek(0, 0)
        file.writelines(file_lines)


def check_toctree_and_markdown(top_toctree, additional_md):
    """Check if the generated toctree entries and markdown files match the ones stored on disk.

    Args:
      top_toctree (list): Toctree entries for the file api_docs.md.
      additional_md (dict): Additional markdown generated for different releases.

    Returns:
      int: -1 if they do not match, 0 otherwise.
    """

    # Check if the generate files exist and match the wanted ones
    api_docs_dir = Path(os.getcwd()).joinpath("source").joinpath("api_docs")
    if not api_docs_dir.exists():
        return -1 if additional_md else 0

    for filename, new_content in additional_md.items():
        filepath = api_docs_dir / filename
        if not filepath.exists():
            return -1
        with open(filepath, "r", encoding="utf-8") as file:
            old_content = file.read()
        if new_content != old_content:
            return -1

    # Check if the update of the toctree would be fine
    api_docs_file = Path(os.getcwd()).joinpath("source").joinpath("api_docs.md")
    with open(api_docs_file, "r+", encoding="utf-8") as file:
        old_file_lines = file.readlines()
        start_line = None
        end_line = None
        for idx, line in enumerate(old_file_lines):
            if line.startswith(r":maxdepth: 1"):
                start_line = idx + 1
            elif start_line and line.startswith(r"```"):
                end_line = idx
                break

        toctree_content = top_toctree + old_file_lines[start_line:end_line]
        toctree_content = [
            x for i, x in enumerate(toctree_content) if i == toctree_content.index(x)
        ]

        new_file_lines = old_file_lines[:start_line] + toctree_content + old_file_lines[end_line:]
        if new_file_lines != old_file_lines:
            return 1

    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script to generate the links to the APIs documentation files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not change any file, return 1 when the operation would have changed some file.",
    )
    args = parser.parse_args()

    api_docs_urls = get_api_docs_urls()

    toctree, markdowns = generate_toctree_and_markdown_from_api_docs_urls(api_docs_urls)

    if args.dry_run:
        sys.exit(abs(check_toctree_and_markdown(toctree, markdowns)))
    else:
        store_toctree_and_markdown(toctree, markdowns)
