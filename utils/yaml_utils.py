from __future__ import with_statement

import copy
from pathlib import Path
from typing import Dict, NewType, Union, TypeVar, Generator

import yaml

YamlKeyType = TypeVar('YamlKeyType', bound=str)
YamlValueType = TypeVar('YamlValueType', str, list, dict)
YamlDataType = NewType('YamlDataType', Union[str, Dict[YamlKeyType, YamlValueType]])

def yaml_load_all(file: Path) -> Generator[YamlDataType, None, None]:
    """
    Load YAML-documents from a given path
    :param yaml_file_path: Filename of YAML file
    :return: Generator for yaml documents (dicts)
    """
    rfile = file.resolve()
    error_msg = f"An error occurred while reading yaml data from {rfile}"
    if rfile.is_file():
        if rfile.suffix == ".yaml":
            try:
                with open(rfile.resolve(), "r") as yaml_file:
                    num = 0
                    for x in yaml.safe_load_all(yaml_file):
                        yield copy.deepcopy(x)
                        num += 1
                    if num == 0:
                        print(f"{error_msg}. No yaml documents found.")
                        raise ValueError
            except EnvironmentError as e:
                print(f"{error_msg}.")
        else:
            print(f"{error_msg}. Wrong file suffix (should be: .yaml).")
            raise ValueError
    else:
        print(f"{error_msg}. File does not exist.")

def yaml_load(file: Path) -> YamlDataType:
    """
    Load YAML-documents from a given path
    :param yaml_file_path: Filename of YAML file
    :return: Generator for yaml documents (dicts)
    """
    rfile = file.resolve()
    error_msg = f"An error occurred while reading yaml data from {rfile}"
    if rfile.is_file():
        if rfile.suffix == ".yaml":
            try:
                with open(rfile.resolve(), "r") as yaml_file:
                    return copy.deepcopy(yaml.safe_load(yaml_file))
            except EnvironmentError as e:
                print(f"{error_msg}.")
        else:
            print(f"{error_msg}. Wrong file suffix (should be: .yaml).")
            raise ValueError
    else:
        print(f"{error_msg}. File does not exist.")

def yaml_store(file: Path, data: dict) -> None:
    rfile = file.resolve()
    if not file.parent.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
    if rfile.suffix != ".yaml":
        rfile.with_suffix(".yaml")
    with open(rfile, 'w') as file:
        yaml.dump(data, file)
