import re
from typing import Set, List, Generator

from utils.log import LogInit, log


class IncludeContainer:
    @LogInit()
    def __init__(self) -> None:
        self.__include_set: Set[str] = set()
        self.__includes: List[str] = []

    @log
    def add_include(self, include: str ) -> None:
        clear_include = re.sub(r"[\"<>]", "", include).upper()
        if clear_include not in self.__include_set:
            self.__include_set.add(clear_include)
            self.__includes.append(include)

    @log
    def add_includes(self, includes: Generator[str, None, None]) -> None:
        for include in includes:
            self.add_include(include)

    @log
    def add_list_of_includes(self, includes: Generator[List[str], None, None]) -> None:
        for includeList in includes:
            for include in includeList:
                self.add_include(include)

    @property
    def includes(self) -> List[str]:
        return self.__includes
