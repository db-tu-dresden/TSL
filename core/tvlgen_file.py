import logging
import re
from pathlib import Path
from typing import Dict, Generator
from datetime import date

from core.tvl_config import TVLGeneratorConfig
from utils.cpp_utils import IncludeContainer
from utils.file import RequiredFileNotFoundError
from utils.log import LogInit, log
from utils.singleton import Singleton
from utils.yaml import YamlDataType


class TVLFile:

    @LogInit()
    def __init__(self, relative_file_path: Path, filename: Path, file_documentation_data: YamlDataType) -> None:
        if relative_file_path.is_absolute():
            raise Exception(f"Provided path should be relative but is absolut. ({relative_file_path}).")
        self.__includes: IncludeContainer = IncludeContainer()
        self.__file_path = TVLGeneratorConfig().generation_out_base_path.joinpath(relative_file_path)
        self.__file_path.mkdir(parents=True, exist_ok=True)

        self.__file_name = self.__file_path.joinpath(filename.with_suffix(".hpp"))

        include_guard_filename = re.sub(r"[/\.\\]", "_", str(self.__file_name)).upper()

        file_documentation_data["file_name"] = self.__file_name
        file_documentation_data["date"] = date.today().strftime("%d.%m.%Y")
        self.__data_dict: YamlDataType = {
            "tvl_license": TVLGeneratorConfig().license_template.render(),
            "tvl_file_doxygen":
                TVLGeneratorConfig().documentation_template.render_file_documentation(file_documentation_data),
            "tvl_include_guard": f"TUD_D2RG_TVL_{include_guard_filename}",
            "tvl_namespace": TVLGeneratorConfig().tvl_namespace,
            "codes": []
        }

    @property
    def file(self) -> Path:
        return self.__file_name

    @log
    def add_includes(self, includes: Generator[str, None, None]) -> None:
        self.__includes.add_includes(includes)

    @log
    def add_include(self, include: str) -> None:
        self.__includes.add_include(include)

    @log
    def add_code(self, code: str) -> None:
        self.__data_dict["codes"].append(code)

    @log
    def generate(self) -> None:
        self.__data_dict["includes"] = self.__includes.includes
        self.__file_name.resolve().write_text(TVLGeneratorConfig().header_file_template.render(self.__data_dict))

class FileDictHelper(metaclass=Singleton):
    @LogInit()
    def __init__(self):
        pass

    @log
    def create_file_dict(self, base_path: Path) -> Dict[Path, int]:
        return {file: file.stat().st_mtime_ns for file in base_path.rglob("*.yaml")}

class TVLYamlFileTree:
    @LogInit()
    def __init__(self, base_path: Path):
        self.__extensions_path: Path = base_path.joinpath("extensions")
        self.__extensions: Dict[Path, int] = dict()
        self.__primitives_path: Path = base_path.joinpath("primitives")
        self.__primitives: Dict[Path, int] = dict()

        self.__primitive_classes_file: Path = base_path.joinpath("primitive_classes.yaml").resolve()
        if not self.__primitive_classes_file.is_file():
            raise RequiredFileNotFoundError(f"{str(self.__primitive_classes_file)} not found")



    @log
    def __relevant_files(self, base_path: Path, file_dict: Dict[Path, int]) -> Generator[Path, None, None]:
        tmp_dict: Dict[Path, int] = FileDictHelper().create_file_dict(base_path)
        for file in tmp_dict:
            if file not in file_dict:
                file_dict[file] = tmp_dict[file]
                yield file
            else:
                if tmp_dict[file] > file_dict[file]:
                    file_dict[file] = tmp_dict[file]
                    yield file

    @log
    def relevant_extension_files(self) -> Generator[Path, None, None]:
        yield from self.__relevant_files(self.__extensions_path, self.__extensions)

    @log
    def get_extension_rel_path(self, extension_file: Path) -> Path:
        return extension_file.parent.relative_to(self.__extensions_path)

    @log
    def relevant_primitive_files(self) -> Generator[Path, None, None]:
        yield from self.__relevant_files(self.__primitives_path, self.__primitives)

    @property
    @log
    def primitive_classes_file(self) -> Path:
        return self.__primitive_classes_file
