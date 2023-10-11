from __future__ import annotations

import copy
import logging
from copy import deepcopy
from pathlib import Path
from typing import Set, List, Generator, Dict, Tuple

from generator.core.tsl_config import config
from generator.utils.dict_utils import deep_update_dict, keep_in_list
from generator.utils.log_utils import LogInit
from generator.utils.requirement import requirement
from generator.utils.yaml_utils import YamlDataType


class TSLPrimitive:
    class Declaration:
        @LogInit()
        def __init__(self, data_dict: dict):
            self.__data_dict = data_dict
            self.__data_dict["tsl_namespace"] = config.get_config_entry("namespace")
            if "tsl_implementation_namespace" not in self.__data_dict:
                self.__data_dict["tsl_implementation_namespace"] = config.implementation_namespace
            if len(data_dict["functor_name"]) == 0:
                self.__data_dict["functor_name"] = data_dict["primitive_name"]
            self.log(logging.INFO, f"Created Primitive Declaration {self.__data_dict['primitive_name']}")

        @property
        def data(self) -> YamlDataType:
            return self.__data_dict

        @property
        def name(self) -> str:
            return self.__data_dict["primitive_name"]

        @property
        def functor_name(self) -> str:
            return self.__data_dict["functor_name"]

        def __deepcopy__(self, memodict={}):
            cls = self.__class__
            result = cls.__new__(cls)
            memodict[id(self)] = result
            for k, v in self.__dict__.items():
                setattr(result, k, deepcopy(v, memodict))
            return result
        def has_additional_simd_template_parameters(self) -> bool:
           return self.__data_dict["additional_simd_template_parameter"]["name"] != ""

    class Definition:
        @classmethod
        def map_types_cartesian(cls, alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
            for a in alist:
                for b in blist:
                    yield (a,b)

        @classmethod
        def map_types_one2m(cls, alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
            if len(alist) > 1:
                raise ValueError("map_types_one2m: First parameter must have length of 1.")
            for b in blist:
                yield (alist[0], b)

        @classmethod
        def map_types_m2one(cls, alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
            if len(blist) > 1:
                raise ValueError("map_types_m2one: Second parameter must have length of 1.")
            for a in alist:
                yield (a, blist[0])

        @classmethod
        def map_types_one2one(cls, alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
            if len(alist) != len(blist):
                raise ValueError("map_types_one2one: Both parameters must have same length.")
            for i in range(len(alist)):
                yield (alist[i], blist[i])

        @classmethod
        def map_types_m2m(clscls, alist: List[str]) -> Generator[Tuple[str, str], None, None]:
            for i in alist:
                yield(i,i)


        @classmethod
        def map_types_from_dict(cls, alist: List[str], bdict: Dict[str, List[str]]) -> Generator[Tuple[str, str], None, None]:
            for i in alist:
                if i not in bdict:
                    raise ValueError("map_types_from_dict: value from left parameter not in right one.")
                for j in bdict[i]:
                    yield (i, j)

        @LogInit()
        def __init__(self, data_dict: dict):
            self.__data_dict = data_dict
            self.log(logging.INFO,
                     f"Created Primitive Definition for {self.__data_dict['target_extension']} using {self.__data_dict['ctype']}")

        @classmethod
        def construct(cls, data_dict: dict):
            if isinstance(data_dict['target_extension'], list):
                for target_extension in data_dict['target_extension']:
                    cd = copy.deepcopy(data_dict)
                    cd['target_extension'] = target_extension
                    yield TSLPrimitive.Definition(cd)
            else:
                yield TSLPrimitive.Definition(data_dict)

        def __str__(self) -> str:
            return f"<{self.target_extension} -> {self.ctypes}>"

        @staticmethod
        def schema_identifier() -> str:
            return "definitions"

        @property
        def data(self) -> YamlDataType:
            return self.__data_dict
        
        @property
        def location_of_origin_str(self) -> str:
            if "yaml_origin_file" and "yaml_origin_file" in self.__data_dict:
                return f"{self.__data_dict['yaml_origin_file']}:{self.__data_dict['yaml_origin_line']}"
            else:
                return "UNKNOWN"

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

        @ctypes.setter
        def ctypes(self, ct: List[str]):
            self.__data_dict["ctype"] = ct

        @property
        def additional_simd_template_base_types(self) -> List[str]:
            if isinstance(self.__data_dict["additional_simd_template_base_type"], str):
                if len(self.__data_dict["additional_simd_template_base_type"] > 0):
                    return [self.__data_dict["additional_simd_template_base_type"]]
                else:
                    return []
            return self.__data_dict["additional_simd_template_base_type"]

        @additional_simd_template_base_types.setter
        def additional_simd_template_base_types(self, ct: List[str]):
            self.__data_dict["additional_simd_template_base_type"] = ct

        @property
        def additional_simd_template_base_type_mapping_dict(self) -> Dict[str, List[str]]:
            return self.__data_dict["additional_simd_template_base_type_mapping_dict"]
        
        @property 
        def additional_simd_template_extension(self) -> str:
            aste = self.__data_dict['additional_simd_template_extension']
            return aste if aste else self.target_extension

        def update_types(self, ct: List[str]):
            ctypes = copy.deepcopy(self.ctypes)
            astbt = copy.deepcopy(self.additional_simd_template_base_types)
            astbtmd = copy.deepcopy(self.additional_simd_template_base_type_mapping_dict)
            keep_in_list(self.ctypes, ct)
            keep_in_list(self.additional_simd_template_base_types, ct)
            deep_update_dict(self.additional_simd_template_base_type_mapping_dict, ct, True)
            # if ctypes != self.ctypes or astbt != self.additional_simd_template_base_types or astbtmd != self.additional_simd_template_base_type_mapping_dict:
            #     print("SOMETHING CHANGED")


        @property
        def types(self) -> Generator[Tuple[str, str], None, None]:
            ctypes_list = self.ctypes
            return_vector_basetypes_list = self.additional_simd_template_base_types
            if (len(return_vector_basetypes_list) == 0) and (len(self.additional_simd_template_base_type_mapping_dict) == 0) and self.__data_dict["additional_simd_template_extension"] == "":
                for t in ctypes_list:
                    yield (t, "")
            elif (len(ctypes_list) == 1) and (len(return_vector_basetypes_list) > 1):
                yield from TSLPrimitive.Definition.map_types_one2m(ctypes_list, return_vector_basetypes_list)
            elif (len(ctypes_list) > 1) and (len(return_vector_basetypes_list) == 1):
                yield from TSLPrimitive.Definition.map_types_m2one(ctypes_list, return_vector_basetypes_list)
            elif len(ctypes_list) == (len(return_vector_basetypes_list)):
                yield from TSLPrimitive.Definition.map_types_one2one(ctypes_list, return_vector_basetypes_list)
            elif len(self.additional_simd_template_base_type_mapping_dict) > 0:
                yield from TSLPrimitive.Definition.map_types_from_dict(ctypes_list, self.additional_simd_template_base_type_mapping_dict)
            elif len(ctypes_list) > 0 and len(return_vector_basetypes_list) == 0:
                yield from TSLPrimitive.Definition.map_types_m2m(ctypes_list)
            else:
                yield from TSLPrimitive.Definition.map_types_cartesian(ctypes_list, return_vector_basetypes_list)

        @property
        def types_dict(self) -> Dict[str, List[str]]:
            result: Dict[str, List[str]] = {}
            for t in self.types:
                if t[0] in result:
                    result[t[0]].append(t[1])
                else:
                    result[t[0]] = [t[1]]
            return result

        def __deepcopy__(self, memodict={}):
            cls = self.__class__
            result = cls.__new__(cls)
            memodict[id(self)] = result
            for k, v in self.__dict__.items():
                setattr(result, k, deepcopy(v, memodict))
            return result

        def is_similar(self, other_definition: TSLPrimitive.Definition) -> bool:
            if other_definition.target_extension != self.target_extension:
                return False
            selfset = set([f"{x},{y}" for x,y in self.types])
            otherset = set([f"{x},{y}" for x,y in other_definition.types])
            return len(selfset & otherset) > 0

        def greater_than(self, other_definition:TSLPrimitive.Definition, relevant_architecture_flags: Set[str]) -> bool:
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
                if (len(self.additional_simd_template_base_types) == 0) and (len(self.additional_simd_template_base_type_mapping_dict) == 0):
                    tmptypes: List[str] = [type for type in self.ctype if type not in ctypes]
                    self.__data_dict["ctype"] = tmptypes
                elif (len(self.ctypes) == 1) and (len(self.additional_simd_template_base_types) > 1):
                    if self.ctypes[0] in ctypes:
                        self.__data_dict["ctype"] = []
                        self.__data_dict["additional_simd_template_base_type"] = []
                elif (len(self.ctypes) > 1) and (len(self.additional_simd_template_base_types) == 1):
                    tmptypes: List[str] = [type for type in self.ctype if type not in ctypes]
                    self.__data_dict["ctype"] = tmptypes
                elif len(self.ctypes) == len(self.additional_simd_template_base_types):
                    idx_to_keep = [idx for idx in range(len(self.ctypes)) if self.ctypes[idx] not in ctypes]
                    tmp_return_types = [self.additional_simd_template_base_types[idx] for idx in idx_to_keep]
                    tmp_types = [self.ctypes[idx] for idx in idx_to_keep]
                    self.__data_dict["additional_simd_template_base_type"] = tmp_return_types
                    self.__data_dict["ctype"] = tmp_types
                    self.__data_dict["additional_simd_template_base_type"] = tmp_return_types
                elif len(self.additional_simd_template_base_type_mapping_dict) > 0:
                    tmp_types: List[str] = [type for type in self.ctype if type not in ctypes]
                    tmp_dict: Dict[str, List[str]] = {t: self.additional_simd_template_base_type_mapping_dict[t] for t in tmp_types}
                    self.__data_dict["ctype"] = tmp_types
                    self.__data_dict["additional_simd_template_base_type_mapping_dict"] = tmp_dict
                else:
                    tmptypes: List[str] = [type for type in self.ctype if type not in ctypes]
                    self.__data_dict["ctype"] = tmptypes

    def __str__(self) -> str:
        return f"{self.declaration.name}"

    def __eq__(self, other):
        if isinstance(other, TSLPrimitive):
            if other.declaration.name == self.declaration.name:
                return other.declaration.functor_name == self.declaration.functor_name
        else:
            return False


    @staticmethod
    def human_readable(name: str, ctype: str, target_extension: str) -> str:
        return f"{name}<{ctype},{target_extension}>"

    @LogInit()
    def __init__(self, declaration: TSLPrimitive.Declaration, definitions: List[TSLPrimitive.Definition]) -> None:
        self.__declaration: TSLPrimitive.Declaration = declaration
        self.__definitions: List[TSLPrimitive.Definition] = definitions

    @property
    def declaration(self) -> TSLPrimitive.Declaration:
        return self.__declaration

    @property
    def definitions(self) -> Generator[TSLPrimitive.Definition, None, None]:
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
                if "implementation" in test:
                  yield copy.deepcopy(test)
            
    def get_tests(self, copy: bool = True) -> Generator[Tuple[str, str, bool, str], None, None]:
        if self.has_test():
            test_names_dict: Dict[str, int] = {}
            for test in self.declaration.data["testing"]:
                if "yaml_origin_file" and "yaml_origin_file" in self.__data_dict:
                    location_or_origin_str = f"{test['yaml_origin_file']}:{test['yaml_origin_line']}"
                else:
                    location_or_origin_str = "UNKNOWN"
                if "implementation" in test:
                    test_name = test["test_name"]
                    if test_name in test_names_dict:
                        test["test_name"] = f"{test_name}_{test_names_dict[test_name]}"
                        test_names_dict[test_name] += 1
                    else:
                        test_names_dict[test_name] = 0
                    if copy:
                        yield test["test_name"], copy.deepcopy(test["implementation"]), test["implicitly_reliable"], location_or_origin_str
                    else:
                        yield test["test_name"], test["implementation"], test["implicitly_reliable"], location_or_origin_str
    
    def get_implementations(self, copy: bool = True) -> Generator[str, None, None]:
      if copy:
        for definition in self.definitions:
            yield copy.deepcopy(definition.data["implementation"])
      else:
        for definition in self.definitions:
            yield definition.data["implementation"]

    @staticmethod
    @requirement(data_dict="NotNone;dict")
    def create_from_dict(data_dict: dict) -> TSLPrimitive:
        definitions_dict_list = []
        if TSLPrimitive.Definition.schema_identifier() in data_dict:
            definitions_dict_list = data_dict.pop(TSLPrimitive.Definition.schema_identifier())
        declaration: TSLPrimitive.Declaration = TSLPrimitive.Declaration(data_dict)
        definitions: List[TSLPrimitive.Definition] = [
            definition for definition_dict in definitions_dict_list 
            for definition in TSLPrimitive.Definition.construct(definition_dict)
        ]
        return TSLPrimitive(declaration, definitions)

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
            for ctype in definition.ctypes:
                if ctype not in result[definition.target_extension]:
                    result[definition.target_extension].append(ctype)
        return result

    # resulting dict: (extension, additional_simd_template_extension, ctype) -> list of additional_simd_template_base_type
    def conversion_types(self, specializations: Dict[str, List[str]]) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        if not self.declaration.has_additional_simd_template_parameters():
            return None
        result: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for definition in self.definitions:
            te = definition.target_extension
            if te not in result:
                result[te] = {}
            result_te = result[te]
            aste = definition.additional_simd_template_extension
            if aste not in result_te:
                result_te[aste] = {}
            known_conversions = result_te[aste]
            tsdict: Dict[str, List[str]] = definition.types_dict
            for tstype in tsdict:
                if tstype in specializations[te]:
                    if tstype not in known_conversions:
                        known_conversions[tstype] = []
                    known_conversions[tstype].extend(tsdict[tstype])
        return result

class TSLPrimitiveClass:
    @LogInit()
    def __init__(self, path: Path, data_dict: YamlDataType) -> None:
        self.__primitives: List[TSLPrimitive] = list()
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
        if isinstance(other, TSLPrimitiveClass):
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
    def create_from_dict(path: Path, data_dict: YamlDataType) -> TSLPrimitiveClass:
        primitive_data_path = config.get_primitive_files_path("primitives_path")
        primitive_class_file_relative_to_primitive_data_path = path.relative_to(primitive_data_path)
        primitive_file_path = primitive_class_file_relative_to_primitive_data_path.parent
        return TSLPrimitiveClass(primitive_file_path, data_dict)

    @requirement(primitive="NotNone")
    def add_primitive(self, primitive: TSLPrimitive, logLevel=logging.INFO) -> None:
        if primitive in self.__primitives:
            self.log(logLevel, f"Overwriting old data for primitive {primitive.declaration.name}")
            self.__primitives.remove(primitive)
        else:
            self.log(logLevel, f"Adding primitive {self.name}::{primitive.declaration.name}")
        self.__primitives.append(primitive)

    @requirement(data_dict="NotNone")
    def add_primitive_from_dict(self, data_dict: YamlDataType) -> None:
        primitive = TSLPrimitive.create_from_dict(data_dict)
        self.__primitives.append(primitive)

    def __iter__(self):
        for primitive in self.__primitives:
            yield primitive


class TSLPrimitiveClassSet:
    @LogInit()
    def __init__(self):
        self.__primitive_classes: Set[TSLPrimitiveClass] = set()

    @property
    def known_ctypes(self) -> List[str]:
        known_ctypes_set = set(config.relevant_types)
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                for definition in primitive.definitions:
                    for ctype in definition.ctypes:
                        known_ctypes_set.add(ctype)
        return sorted(list(known_ctypes_set))

    @requirement(primitive_class="NotNone")
    def add_primitive_class(self, primitive_class: TSLPrimitiveClass):
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

    def definitions(self) -> Generator[TSLPrimitive.Definition, None, None]:
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                yield from primitive.definitions

    def primitives(self) -> Generator[TSLPrimitive, None, None]:
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                yield primitive

    def definitions_names(self) -> Generator[str, None, None]:
        for primitive_class in self.__primitive_classes:
            for primitive in primitive_class:
                name = primitive.declaration.functor_name
                for definition in primitive.definitions:
                    for ctype in definition.ctypes:
                        yield TSLPrimitive.human_readable(name, ctype, definition.target_extension)

    def get_declaration_dict(self) -> Dict[Dict[str, TSLPrimitive.Declaration]]:
        result: Dict[Dict[str, TSLPrimitive.Declaration]] = dict()
        for primitive_class in self.__primitive_classes:
            result[primitive_class.name] = {primitive.declaration.functor_name: primitive.declaration for primitive in
                                            primitive_class}
        return result
