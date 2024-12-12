"""Settings for the python package setup."""

from typing import Self

import git
from setuptools import find_packages, setup


class RepoDetails:
    """Retrieve all the repo details."""

    def __init__(self: Self) -> None:
        """Retrieves basic details."""
        self.author = "1st Sedgley Scouts"
        self.email = "github@1stsedgleyscouts.org.uk"
        self.repo = git.Repo(search_parent_directories=True)
        self.tag = self.get_latest_tag()
        self.name = self.get_repo_name()
        self.url = f"https://github.com/1st-Sedgley-Scout-Group/{self.name}"

    def get_latest_tag(self: Self) -> str:
        """Extracts the most recent tag published to GitHub releases in this repo.

        Raises:
            RuntimeError: If there is an issue retrieving the latest tag.

        Returns:
            str: The latest tag.
        """
        try:
            repo = git.Repo(search_parent_directories=True)
            tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
            if tags:
                return tags[-1].name
            else:
                return ""
        except (git.exc.GitError, IndexError) as e:
            raise RuntimeError("Failed to get latest tag: " + str(e))

    def get_repo_name(self: Self) -> str:
        """Retrieves the name of the current Git repository.

        Returns:
            str: The name of the current Git repository.
        """
        tree = self.repo.working_tree_dir
        return tree.split("/")[-1]

    def get_file_content(self: Self, filename: str) -> str:
        """Retrieves the content of a file within the current Git repository root.

        Args:
            filename (str): The name of the file to retrieve content from.

        Returns:
            str: The content of the file as a string.

        Raises:
            NameError: If the specified file is not found in the root directory of the Git repository.
        """
        try:
            tree = self.repo.tree()
            return tree[filename].data_stream.read().decode("utf-8")
        except KeyError:
            raise KeyError(f"File named {filename}, not found in root of {self.name}")


# Run Class
repo_details = RepoDetails()

setup(
    name=repo_details.name,
    version=repo_details.tag,
    description=repo_details.get_file_content("README.md"),
    author=repo_details.author,
    author_email=repo_details.email,
    url=repo_details.url,
    packages=find_packages(),
    install_requires=repo_details.get_file_content("requirements.txt"),
)
