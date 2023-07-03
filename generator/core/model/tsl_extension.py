from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import Set, List

from generator.core.tsl_config import config
from generator.utils.log_utils import LogInit
from generator.utils.requirement import requirement
from generator.utils.yaml_utils import YamlDataType


class TSLExtension:
    @LogInit()
    def __init__(self, path: Path, data_dict: YamlDataType) -> None:
        self.__file_path = path
        self.__data_dict = data_dict

    @property
    def data(self) -> YamlDataType:
        return self.__data_dict

    @property
    def name(self) -> str:
        return self.__data_dict["extension_name"]

    @property
    def file_name(self) -> Path:
        return self.__file_path

    def synonym_flags(self) -> YamlDataType:
        return self.__data_dict["synonym_flags"]

    @property
    def has_synonyms(self) -> YamlDataType:
        return "synonym_flags" in self.__data_dict

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    @requirement(other="NotNone")
    def __eq__(self, other):
        if isinstance(other, TSLExtension):
            return self.name == other.name
        return False

    @requirement(other="NotNone")
    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__data_dict["extension_name"])

    def __str__(self):
        return f"{str(self.name)}: {str(self.data)}"

    def __repr__(self):
        return f"{{TSLExtension {str(self.name)}: {{{str(self.data)}}}}}"

    @staticmethod
    @requirement(path="NotNone", data_dict="NotNone")
    def create_from_dict(path: Path, data_dict: YamlDataType) -> TSLExtension:
        return TSLExtension(path, data_dict)


class TSLExtensionSet:
    @LogInit()
    def __init__(self) -> None:
        self.__extensions: Set[TSLExtension] = set()

    @property
    def known_extensions(self) -> List[str]:
        return sorted([extension.name for extension in self.__extensions])

    @requirement(extension="NotNone")
    def add_extension(self, extension: TSLExtension, logLevel=logging.INFO) -> None:
        if extension in self.__extensions:
            self.log(logLevel, f"Overwriting old data for extension {extension.name}")
            self.__extensions.discard(extension)
        else:
            self.log(logging.INFO, f"Adding extension {extension.name}")
        self.__extensions.add(extension)

    @requirement(path="NotNone", data_dict="NotNone")
    def add_extension_from_data_dict(self, path: Path, data_dict: YamlDataType) -> None:
        extension_data_path = config.get_primitive_files_path("extensions_path")
        extension_file_relative_to_extension_data_path = path.relative_to(extension_data_path)
        extension_file_path = extension_file_relative_to_extension_data_path.parent
        extension = TSLExtension.create_from_dict(extension_file_path, data_dict)
        self.add_extension(extension)

    @requirement(extension_name="NonEmptyString")
    def get_extension_by_name(self, extension_name: str) -> TSLExtension:
        for extension in self.__extensions:
            if extension.name == extension_name:
                return extension
        self.log(logging.ERROR, f"Could not find extension {extension_name}")
        raise ValueError(f"{extension_name} not found.")

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    def __iter__(self):
        for extension in self.__extensions:
            yield extension

    def __str__(self):
        return f"{str(self.__extensions)}"

    def __repr__(self):
        return f"{{TSLExtensionSet: {{{str(self.__extensions)}}}}}"
