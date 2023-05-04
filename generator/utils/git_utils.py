from __future__ import annotations
from dataclasses import dataclass
from typing import List
import re
from pathlib import Path
import subprocess
import os

from generator.utils.file_utils import strip_common_path_prefix


@dataclass
class GitUtils:
    local_path: Path
    remote_url: str
    branch: str
    abbrev_hash: str
    hash: str
    submodules: List[GitUtils]
    submodule_regex_pattern = re.compile(r"(\S+)\s+(\S+)\s+(\S+)")

    def __create_list(self, indentation: int) -> List[str]:
        result: List[str] = []
        result.append(f"{' ' * indentation}Git-Local Url : {self.local_path}")
        result.append(f"{' ' * indentation}Git-Remote Url: {self.remote_url}")
        result.append(f"{' ' * indentation}Git-Branch    : {self.branch}")
        result.append(f"{' ' * indentation}Git-Commit    : {self.abbrev_hash} ({self.hash})")
        return result

    def __strip_submodule_path_prefix(self, prefix: Path) -> None:
        self.local_path = strip_common_path_prefix(self.local_path, prefix)
        for submodule in self.submodules:
            submodule.__strip_submodule_path_prefix(prefix)

    def create_indented_list(self, indentation: int = 0) -> List[str]:
        if indentation == 0:
            #strip the common path prefix
            for submodule in self.submodules:
                submodule.__strip_submodule_path_prefix(self.local_path)
        result: List[str] = self.__create_list(indentation)
        for submodule in self.submodules:
            result.append(f"{' ' * indentation}Submodule(s):")
            result.extend(submodule.create_indented_list(indentation+2))
        return result

    def create_version_str(self) -> str:
        result: str = str(self)
        for submodule in self.submodules:
            result += f", {submodule.create_version_str()}"
        return result

    def __str__(self):
        return f"{self.remote_url}:/{self.branch}@{self.abbrev_hash}"

    @staticmethod
    def get_git_data() -> GitUtils:
        local_path: Path = Path().resolve()
        try:
            remote_url: str = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).strip().decode(
                "utf-8")
            branch: str = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode("utf-8")
            abbrev_hash: str = subprocess.check_output(["git", "describe", "--always"]).strip().decode("utf-8")
            hash: str = subprocess.check_output(["git", "rev-parse", abbrev_hash]).strip().decode("utf-8")
            submodules_status: List[str] = subprocess.check_output(["git", "submodule", "status"]).strip().decode(
                "utf-8").split("\n")
            submodules: List[GitUtils] = []
            for submodule_str in submodules_status:
                if len(submodule_str) == 0:
                    continue
                submodule_path: str = GitUtils.submodule_regex_pattern.search(submodule_str).group(2)
                os.chdir(local_path.joinpath(submodule_path))
                submodules.append(GitUtils.get_git_data())
                os.chdir(local_path)
            return GitUtils(local_path, remote_url, branch, abbrev_hash, hash, submodules)
        except:
            return GitUtils(local_path, "unknown url", "unknown branch", "unknown commit", "unknown commit", [])
