from pathlib import Path
from typing import List, Generator, Dict, Tuple

from core.model.tvl_file import TVLSourceFile, TVLHeaderFile


class TVLTranslationUnit:
    def __init__(self, target_name: str) -> None:
        self.__target_name: str = target_name
        self.__source_files: List[TVLSourceFile] = []
        self.__header_files: List[TVLHeaderFile] = []

    def add_source(self, source: TVLSourceFile) -> None:
        self.__source_files.append(source)

    def add_header(self, header: TVLHeaderFile) -> None:
        self.__header_files.append(header)

    @property
    def header_files(self) -> Generator[TVLHeaderFile, None, None]:
        for h in self.__header_files:
            yield h

    @property
    def source_files(self) -> Generator[TVLSourceFile, None, None]:
        for s in self.__source_files:
            yield s

    @property
    def target_name(self) -> str:
        return self.__target_name


class TVLTranslationUnitContainer:
    def __init__(self):
        self.__tu_dict: Dict[Path, List[TVLTranslationUnit]] = dict()

    def add_tu(self, path: Path, tu: TVLTranslationUnit) -> None:
        if path not in self.__tu_dict:
            self.__tu_dict[path] = []
        self.__tu_dict[path].append(tu)

    @property
    def translation_units(self) -> Generator[Tuple[Path, List[TVLTranslationUnit]], None, None]:
        for k in self.__tu_dict:
            yield k, self.__tu_dict[k]