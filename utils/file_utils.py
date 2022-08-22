from pathlib import Path
from typing import Dict, Generator, Tuple


class StaticFileTree:
    def __init__(self, path: Path, pattern: str = ""):
        self.__files: Dict[Path, int] = dict()
        self.__path = path
        self.__pattern = pattern

    def get_recently_updated_files(self) -> Generator[Path, None, None]:
        for file in self.__path.rglob(self.__pattern):
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
        for file in self.__path.rglob(self.__pattern):
            if file.is_file():
                last_accessed_time = file.stat().st_mtime_ns
                self.__files[file] = last_accessed_time
                yield file

    def build(self) -> None:
        for file in self.__path.rglob(self.__pattern):
            if file.is_file():
                last_accessed_time = file.stat().st_mtime_ns
                self.__files[file] = last_accessed_time

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
