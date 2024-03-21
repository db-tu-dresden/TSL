from __future__ import annotations

from pathlib import Path
import shutil
from typing import Dict, Generator, Tuple, List
import re

class StaticFileTree:

    @staticmethod
    def escape_pathstr(p: str) -> str:
        return p.replace("/", "\\/")

    @staticmethod
    def get_dirstr(p: str) -> str:
        return rf"(.*\/{StaticFileTree.escape_pathstr(p)}\/.*)"

    def __init__(self, path: Path, pattern: str = "", exclude_paths: List[str] = []):
        self.__files: Dict[Path, int] = dict()
        self.__path = path
        self.__pattern = pattern.split("|")
        self.__exclude_paths_regex_str = r"|".join([StaticFileTree.get_dirstr(e) for e in exclude_paths])
        if len(exclude_paths) == 0:
            self.__exclude_paths_regex_str = ""
        self.__exclude_paths_regex = re.compile(self.__exclude_paths_regex_str)

    def __glob(self) -> Generator[Path, None, None]:
        for p in self.__pattern:
            for f in self.__path.rglob(p):
                if len(self.__exclude_paths_regex_str) > 0:
                    if not bool(self.__exclude_paths_regex.search(f"{f}")):
                        yield f
                else:
                    yield f

                # else:
                #     print(f"Excluded {f}")
            #yield from self.__path.rglob(p)

    def get_recently_updated_files(self) -> Generator[Path, None, None]:
        for file in self.__glob():
            if file.is_file():
                last_accessed_time = file.stat().st_mtime_ns
                if file not in self.__files:
                    self.__files[file] = last_accessed_time
                    yield file
                else:
                    if last_accessed_time > self.__files[file]:
                        self.__files[file] = last_accessed_time
                        yield file

    def get_files(self) -> Generator[Path, None, None]:
        for file in self.__glob():
            if file.is_file():
                last_accessed_time = file.stat().st_mtime_ns
                self.__files[file] = last_accessed_time
                yield file

    def build(self) -> StaticFileTree:
        for file in self.__glob():
            if file.is_file():
                last_accessed_time = file.stat().st_mtime_ns
                self.__files[file] = last_accessed_time
        return self

    @property
    def items(self) -> Generator[Tuple[Path,int], None, None]:
        for k, v in self.__files.items():
            yield [k,v]

    @property
    def files(self) -> Dict[Path, int]:
        return self.__files

def strip_common_path_prefix(file: Path, prefix: Path) -> Path:
    prefix_parts = prefix.parts
    prefix_length = len(prefix_parts) - 1
    for common_prefix_pos, part in enumerate(file.parts):
        if common_prefix_pos > prefix_length:
            return Path(*file.parts[common_prefix_pos:])
        if part != prefix_parts[common_prefix_pos]:
            return Path(*file.parts[common_prefix_pos:])
    return file


def strip_path_prefix(file: Path) -> Path:
    return Path(*file.parts[-1:])

def remove_path(folder: Path) -> bool:
    if folder.exists:
        shutil.rmtree(folder)
        return True
    return False


def get_relative_path(from_path: Path, to_path: Path) -> Path:
    first_divergence = 0
    for idx in range(min(len(from_path.parts), len(to_path.parts))):
        if from_path.parts[idx] != to_path.parts[idx]:
            first_divergence = idx
            break
    from_path_parts = from_path.parts[first_divergence:]
    to_path_parts = to_path.parts[first_divergence:]
    relative_parts_to_path = ['../'] * (len(from_path_parts) - 1) + list(to_path_parts)
    result = Path(*relative_parts_to_path)
    return result
