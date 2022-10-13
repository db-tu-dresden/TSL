from __future__ import annotations

import copy
import logging
from copy import deepcopy
from pathlib import Path
from typing import Set, List, Generator, Dict, Tuple

from core.tvl_config import config
from utils.log_utils import LogInit
from utils.requirement import requirement
from utils.yaml_utils import YamlDataType


class TVLPrimitive:
    class Declaration:
        @LogInit()
        def __init__(self, data_dict: dict):
            self.__data_dict = data_dict
            self.log(logging.INFO, f"Created Primitive Declaration {self.__data_dict['primitive_name']}")

        @property
        def data(self) -> YamlDataType:
            return self.__data_dict

        @property
        def name(self) -> str:
            return self.__data_dict["primitive_name"]

        def __deepcopy__(self, memodict={}):
            cls = self.__class__
            result = cls.__new__(cls)
            memodict[id(self)] = result
            for k, v in self.__dict__.items():
                setattr(result, k, deepcopy(v, memodict))
            return result

    class Definition:
        @LogInit()
        def __init__(self, data_dict: dict):
            self.__data_dict = data_dict
            self.log(logging.INFO,
                     f"Created Primitive Definition for {self.__data_dict['target_extension']} using {self.__data_dict['ctype']}")

        def __str__(self) -> str:
            return f"<{self.target_extension} -> {self.ctypes}>"

        @staticmethod
        def schema_identifier() -> str:
            return "definitions"

        @property
        def data(self) -> YamlDataType:
            return self.__data_dict

        @property
        def target_extension(self) -> str:
            return self.__data_dict["target_extension"]

        @property
        def architecture_flags(self) -> Generator[str, None, None]:
            yield from self.__data_dict["lscpu_flags"]

        @property
        def is_native(self) -> bool:
            return self.__data_dict["is_native"]

        @property
        def ctype(self) -> str | List[str]:
            return self.__data_dict["ctype"]

        @property
        def ctypes(self) -> List[str]:
            if isinstance(self.ctype, str):
                if len(self.ctype)==0:
                    return []
                return [self.ctype]
            return self.ctype

        @property
        def additional_simd_template_base_type(self) -> List[str]:
            if isinstance(self.__data_dict["additional_simd_template_base_type"], str):
                if len(self.__data_dict["additional_simd_template_base_type"] > 0):
                    return [self.__data_dict["additional_simd_template_base_type"]]
                else:
                    return []
            return self.__data_dict["additional_simd_template_base_type"]

        @property
        def types(self) -> Generator[Tuple[str, str], None, None]:
            ctypes_list = self.ctypes
            return_vector_basetypes_list = self.additional_simd_template_base_type
            if (len(ctypes_list) > 1) and (len(return_vector_basetypes_list) > 1):
                if len(ctypes_list) != len(return_vector_basetypes_list):
                    self.log(logging.CRITICAL, f"{self.human_readable}: {ctypes_list} -- {return_vector_basetypes_list}")
                    raise ValueError("Multiple ctypes and additional_simd_template_base_type must have the same length (1:1 mapping).")
                for idx in range(len(ctypes_list)):
                    yield [ctypes_list[idx], return_vector_basetypes_list[idx]]
            elif len(return_vector_basetypes_list) > 1:
                for rvb in return_vector_basetypes_list:
                    yield [ctypes_list[0], rvb]
            else:
                rvb = ""
                if len(return_vector_basetypes_list) == 1:
                    rvb = return_vector_basetypes_list[0]
                for t in ctypes_list:
                    yield [t, rvb]

        def __deepcopy__(self, memodict={}):
            cls = self.__class__
            result = cls.__new__(cls)
            memodict[id(self)] = result
            for k, v in self.__dict__.items():
                setattr(result, k, deepcopy(v, memodict))
            return result

        def is_similar(self, other_definition: TVLPrimitive.Definition) -> bool:
            if other_definition.target_extension != self.target_extension:
                return False
            selfset = set([f"{x},{y}" for x,y in self.types])
            otherset = set([f"{x},{y}" for x,y in other_definition.types])
            return len(selfset & otherset) > 0

        def greater_than(self, other_definition:TVLPrimitive.Definition, relevant_architecture_flags: Set[str]) -> bool:
            if not self.is_native and other_definition.is_native:
                return False
            if self.is_native and not other_definition.is_native:
                return True
            self_flags: Set[str] = set([flag for flag in self.architecture_flags])
            other_flags: Set[str] = set([flag for flag in other_definition.architecture_flags])
            return len(self_flags & relevant_architecture_flags) > len(other_flags & relevant_architecture_flags)

        def remove_ctypes(self, ctypes: List[str]) -> None:
            if isinstance(self.ctype, str):
                if self.ctype in ctypes:
                    self.__data_dict["ctype"] = ""
            else:
                if (len(self.additional_simd_template_base_type)) > 1:
                    tmp_return_types = [self.additional_simd_template_base_type[idx] for idx in range(self.ctypes) if self.ctypes[idx] not in ctypes]
                    self.__data_dict["additional_simd_template_base_type"] = tmp_return_types
                tmptypes: List[str] = [type for type in self.ctype if type not in ctypes]
                self.__data_dict["ctype"] = tmptypes

    def __str__(self) -> str:
        return f"{self.declaration.name}"

    @staticmethod
    def human_readable(name: str, ctype: str, target_extension: str) -> str:
        return f"{name}<{ctype},{target_extension}>"

    @LogInit()
    def __init__(self, declaration: TVLPrimitive.Declaration, definitions: List[TVLPrimitive.Definition]) -> None:
        self.__declaration: TVLPrimitive.Declaration = declaration
        self.__definitions: List[TVLPrimitive.Definition] = definitions

    @property
    def declaration(self) -> TVLPrimitive.Declaration:
        return self.__declaration

    @property
    def definitions(self) -> Generator[TVLPrimitive.Definition, None, None]:
        for definition in self.__definitions:
            yield definition


    def has_test(self) -> bool:
        if "testing" in self.declaration.data:
            if len(self.declaration.data["testing"]) > 0:
                return True
        return False

    @property
    def tests(self) -> Generator[YamlDataType, None, None]:
        if self.has_test():
            for test in self.declaration.data["testing"]:
                yield copy.deepcopy(test)

    @staticmethod
    @requirement(data_dict="NotNone;dict")
    def create_from_dict(data_dict: dict) -> TVLPrimitive:
        definitions_dict_list = []
        if TVLPrimitive.Definition.schema_identifier() in data_dict:
            definitions_dict_list = data_dict.pop(TVLPrimitive.Definition.schema_identifier())
        declaration: TVLPrimitive.Declaration = TVLPrimitive.Declaration(data_dict)
        # print("=========================================================")
        # print(declaration.name)
        definitions: List[TVLPrimitive.Definition] = [TVLPrimitive.Definition(definition_dict) for definition_dict in
                                                      definitions_dict_list]
        # print("\n".join([f"{d.data}" for d in definitions]))
        # print("=========================================================")

        return TVLPrimitive(declaration, definitions)

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    def specialization_dict(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = dict()
        for definition in self.definitions:
            if definition.target_extension not in result:
                result[definition.target_extension] = []
            result[definition.target_extension].extend(definition.ctypes)
        return result

class TVLPrimitiveClass:
    @LogInit()
    def __init__(self, path: Path, data_dict: YamlDataType) -> None:
        self.__primitives: List[TVLPrimitive] = list()
        self.__file_path = path
        self.__data_dict = data_dict

    @property
    def name(self) -> str:
        return self.__data_dict["name"]

    @property
    def file_name(self) -> Path:
        return self.__file_path

    @property
    def data(self) -> YamlDataType:
        return self.__data_dict

    def is_empty(self) -> bool:
        return len(self.__primitives)==0

    @requirement(other="NotNone")
    def __eq__(self, other):
        if isinstance(other, TVLPrimitiveClass):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    @requirement(other="NotNone")
    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    @requirement(path="NotNone", data_dict="NotNone")
    def create_from_dict(path: Path, data_dict: YamlDataType) -> TVLPrimitiveClass:
        primitive_data_path = config.get_primitive_files_path("primitives_path")
        primitive_class_file_relative_to_primitive_data_path = path.relative_to(primitive_data_path)
        primitive_file_path = primitive_class_file_relative_to_primitive_data_path.parent
        return TVLPrimitiveClass(primitive_file_path, data_dict)

    @requirement(primitive="NotNone")
    def add_primitive(self, primitive: TVLPrimitive, logLevel=logging.INFO) -> None:
        if primitive in self.__primitives:
            self.log(logLevel, f"Overwriting old data for primitive {primitive.declaration.name}")
            self.__primitives.remove(primitive)
        else:
            self.log(logLevel, f"Adding primitive {self.name}::{primitive.declaration.name}")
        self.__primitives.append(primitive)

    @requirement(data_dict="NotNone")
    def add_primitive_from_dict(self, data_dict: YamlDataType) -> None:
        primitive = TVLPrimitive.create_from_dict(data_dict)
        self.__primitives.append(primitive)

    def __iter__(self):
        for primitive in self.__primitives:
            yield primitive


class TVLPrimitiveClassSet:
    @LogInit()
    def __init__(self):
        self.__primitive_classes: Set[TVLPrimitiveClass] = set()

    @property
    def known_ctypes(self) -> List[str]:
        known_ctypes_set = set(config.default_types)
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                for definition in primitive.definitions:
                    for ctype in definition.ctypes:
                        known_ctypes_set.add(ctype)
        return sorted(list(known_ctypes_set))

    @requirement(primitive_class="NotNone")
    def add_primitive_class(self, primitive_class: TVLPrimitiveClass):
        if primitive_class in self.__primitive_classes:
            self.log(logging.INFO, f"Overwriting old data for extension {primitive_class.name}")
            self.__primitive_classes.discard(primitive_class)
        else:
            self.log(logging.INFO, f"Adding primitive class {primitive_class.name}")
        self.__primitive_classes.add(primitive_class)

    def __iter__(self):
        for primitive_class in self.__primitive_classes:
            yield primitive_class

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memodict))
        return result

    def definitions(self) -> Generator[TVLPrimitive.Definition, None, None]:
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                yield from primitive.definitions

    def definitions_names(self) -> Generator[str, None, None]:
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                name = primitive.declaration.name
                for definition in primitive.definitions:
                    for ctype in definition.ctypes:
                        yield TVLPrimitive.human_readable(name, ctype, definition.target_extension)

    def get_declaration_dict(self) -> Dict[Dict[str, TVLPrimitive.Declaration]]:
        result: Dict[Dict[str, TVLPrimitive.Declaration]] = dict()
        for primitive_class in self.__primitive_classes:
            result[primitive_class.name] = {primitive.declaration.name: primitive.declaration for primitive in
                                            primitive_class}
        return result
