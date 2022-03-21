import logging
from pathlib import Path
from typing import List, Dict, NewType, Union

import yaml

from utils.file import BadSuffixError, BadFormatError
from utils.log import LogInit, log
from utils.singleton import Singleton

YamlNestedDataType = NewType("YamlNestedDataType", Union[Dict[str, str | List[str]], dict[str, list | str]])
YamlDataType = NewType("YamlDataType", Union[YamlNestedDataType, Dict[str, YamlNestedDataType], List[YamlNestedDataType]])


class YamlLoader(metaclass=Singleton):
    @LogInit()
    def __init__(self) -> None:
        pass

    @log(successLevel=logging.INFO)
    def load_all(self, yaml_file_path: Path) -> List[YamlDataType]:
        """
        Load YAML-documents from a given path
        :param yaml_file_path: Filename of YAML file
        :return: Generator for yaml documents (dicts)
        """
        if yaml_file_path.is_file():
            if yaml_file_path.suffix == ".yaml":
                with open(yaml_file_path.resolve(), "r") as yaml_file:
                    yaml_documents = [x for x in yaml.safe_load_all(yaml_file)]
            else:
                raise BadSuffixError(
                    f"File has the wrong format. Only yaml files are supported.", {"filename": yaml_file_path})
        else:
            raise FileNotFoundError(f"File does not exist.", {"filename": yaml_file_path})

        if not yaml_documents:
            raise BadFormatError(f"Could not find documents in yaml file.", {"filename": yaml_file_path})
        return yaml_documents

    @log(successLevel=logging.INFO)
    def load(self, yaml_file_path: Path) -> YamlDataType:
        """
        Load YAML-documents from a given path
        :param yaml_file_path: Filename of YAML file
        :return: Generator for yaml documents (dicts)
        """
        if yaml_file_path.is_file():
            if yaml_file_path.suffix == ".yaml":
                with open(yaml_file_path.resolve(), "r") as yaml_file:
                    yaml_documents = yaml.safe_load(yaml_file)
            else:
                raise BadSuffixError(
                    f"File has the wrong format. Only yaml files are supported.", {"filename": yaml_file_path})
        else:
            raise FileNotFoundError(f"File does not exist.", {"filename": yaml_file_path})

        if not yaml_documents:
            raise BadFormatError(f"Could not find documents in yaml file.", {"filename": yaml_file_path})
        return yaml_documents



