from __future__ import annotations

import copy
import datetime
import os.path
from pathlib import Path

from jinja2 import Template

from core.tvl_config import config
from utils.log_utils import LogInit
from utils.requirement import requirement
from utils.yaml_utils import YamlDataType


class TVLHeaderFile:
    """
    Helper class for the generator used to populate the header_file template.
    """
    @LogInit()
    def __init__(self, filename: Path, data_dict: YamlDataType) -> None:
        self.__filename = filename
        self.__data_dict = copy.deepcopy(data_dict)

    @property
    def data(self) -> YamlDataType:
        return self.__data_dict

    @property
    def file_name(self) -> Path:
        return self.__filename

    def __eq__(self, other):
        if isinstance(other, TVLHeaderFile):
            # if the include_guard is the same, the header file must be the same
            return self.__data_dict["tvl_include_guard"] == other.data["tvl_include_guard"]
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__data_dict["tvl_include_guard"])

    def add_file_include(self, header_file: TVLHeaderFile) -> None:
        if header_file not in self.__data_dict["tvl_file_includes"]:
            self.__data_dict["tvl_file_includes"].append(header_file)

    def add_include(self, include: str) -> None:
        if include not in self.__data_dict["includes"]:
            self.__data_dict["includes"].append(include)

    def import_includes(self, data_dict: YamlDataType) -> None:
        if "includes" in data_dict:
            for include_str in data_dict["includes"]:
                self.add_include(include_str)

    def add_code(self, code: str) -> None:
        self.__data_dict["codes"].append(code)

    def add_code_to_be_rendered(self, code: str) -> None:
        self.__data_dict["codes"].append(Template(code).render(self.__data_dict))

    def get_relative_file_name(self) -> Path:
        return self.__filename

    def render(self) -> str:
        # includes = copy.deepcopy(self.__data_dict["includes"])
        current_path: Path = self.file_name.parent
        tvl_file_includes = [f"\"{Path(os.path.relpath(Path(included_file.file_name), current_path))}\"" for included_file in self.__data_dict["tvl_file_includes"]]
        self.__data_dict["includes"].extend([tvl_include for tvl_include in tvl_file_includes if tvl_include not in self.__data_dict["includes"]])
        return config.get_template("core::header_file").render(self.__data_dict)

    def render_to_file(self) -> None:
        self.__filename.write_text(self.render())

    @staticmethod
    def create_include_guard(filename: Path) -> str:
        subst_filename: str = config.include_guard_regex.sub("_", str(filename).upper())
        return f"TUD_D2RG_TVL{subst_filename}"

    @staticmethod
    @requirement(filename="NotNone", data_dict="NotNone")
    def create_from_dict(filename: Path, data_dict: YamlDataType) -> TVLHeaderFile:
        new_data_dict: YamlDataType = {
            # "file_name": filename,
            "year": datetime.date.today().year,
            "date": datetime.date.today(),
            "file_description": data_dict["description"] if "description" in data_dict else "",
            "git_information": config.git_config_as_list,
            "file_name": filename,


            "git_version_str" : config.get_version_str,
            "tvl_include_guard": TVLHeaderFile.create_include_guard(filename),
            "tvl_namespace": config.get_config_entry("namespace"),
            "tvl_file_includes": [],
            "includes": [],
            "codes": []
        }
        return TVLHeaderFile(filename, {**new_data_dict, **data_dict})


class TVLSourceFile:
    @LogInit()
    def __init__(self, filename: Path, data_dict: YamlDataType) -> None:
        self.__filename = filename
        self.__data_dict = copy.deepcopy(data_dict)

    @property
    def data(self) -> YamlDataType:
        return self.__data_dict

    @property
    def file_name(self) -> Path:
        return self.__filename

    def __eq__(self, other):
        if isinstance(other, TVLSourceFile):
            # if the include_guard is the same, the header file must be the same
            return self.file_name == other.file_name
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(str(self.__filename))

    def add_include(self, include: str) -> None:
        if include not in self.__data_dict["includes"]:
            self.__data_dict["includes"].append(include)

    def add_file_include(self, header_file: TVLHeaderFile) -> None:
        if header_file not in self.__data_dict["tvl_file_includes"]:
            self.__data_dict["tvl_file_includes"].append(header_file)

    def import_includes(self, data_dict: YamlDataType) -> None:
        if "includes" in data_dict:
            for include_str in data_dict["includes"]:
                self.add_include(include_str)

    def add_code(self, code: str) -> None:
        self.__data_dict["codes"].append(code)

    def get_relative_file_name(self) -> Path:
        return self.__filename

    def render(self) -> str:
        current_path: Path = self.file_name.parent
        tvl_file_includes = [f"\"{Path(os.path.relpath(Path(included_file.file_name), current_path))}\"" for
                             included_file in self.__data_dict["tvl_file_includes"]]
        self.__data_dict["includes"].extend(
            [tvl_include for tvl_include in tvl_file_includes if tvl_include not in self.__data_dict["includes"]])
        return config.get_template("core::source_file").render(self.__data_dict)

    def render_to_file(self) -> None:
        self.__filename.write_text(self.render())

    @staticmethod
    @requirement(filename="NotNone", data_dict="NotNone")
    def create_from_dict(filename: Path, data_dict: YamlDataType) -> TVLSourceFile:
        new_data_dict: YamlDataType = {
            "file_name": filename,
            "tvl_license": config.get_template("license").render({"year": datetime.date.today().year}),
            "tvl_file_doxygen": config.get_template("core::doxygen_file").render(
                {
                    "file_name": filename,
                    "date": datetime.date.today(),
                    "file_description": data_dict["description"] if "description" in data_dict else ""
                }
            ),
            "tvl_namespace": config.get_config_entry("namespace"),
            "tvl_file_includes": [],
            "includes": [],
            "codes": []
        }
        return TVLSourceFile(filename, {**new_data_dict, **data_dict})
