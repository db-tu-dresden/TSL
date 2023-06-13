import copy
import logging
from copy import deepcopy
from typing import List, Dict, Set

from generator.core.model.tsl_extension import TSLExtensionSet
from generator.core.model.tsl_primitive import TSLPrimitiveClassSet, TSLPrimitiveClass, TSLPrimitive
from generator.utils.dict_utils import intersects, deep_update_dict
from generator.utils.log_utils import LogInit, log
from generator.utils.requirement import requirement


class TSLSlicer:
    @LogInit()
    def __init__(self, relevant_hardware_flags: List[str] = None, relevant_types: List[str] = []):
        self.__relevant_hardware_flags: List[str] = relevant_hardware_flags
        self.__relevant_types: Set[str] = set(relevant_types)
        # self.__relevant_hardware_flags_set: Set[str] = set(relevant_hardware_flags)

    def update_relevant_flags(self, relevant_hardware_flags: List[str]): 
        self.__relevant_hardware_flags = relevant_hardware_flags

    @requirement(data_dict="NotNone")
    def is_extension_relevant(self, data_dict: dict) -> bool:
        """
        Checks whether a specific SIMD-Extension is relevant (/requested). If relevant_lscpu_flags is None or empty, all
        extensions are of interest and the method returns True. If the extension does not have any lscpu_flags specified
         it will also be of interest and consequently, the method returns True.
        If both lists (parameter and user-data) are not empty, the method returns True, if the lscpu-flags of the
        extension has a non-empty set-intersection with the lscpu-flags list, given as parameter.
        :param relevant_lscpu_flags:
        :return:
        """
        if (self.__relevant_hardware_flags is None) or (len(self.__relevant_hardware_flags) == 0):
            return True
        if len(data_dict["lscpu_flags"]) == 0:
            return True
        return len((set(data_dict["lscpu_flags"]) & set(self.__relevant_hardware_flags))) > 0

    @requirement(data_dict="NotNone")
    def is_primitive_relevant(self, data_dict: dict) -> bool:
        """
        Checks whether a specific SIMD-Extension is relevant (/requested). If relevant_lscpu_flags is None or empty, all
        extensions are of interest and the method returns True. If the extension does not have any lscpu_flags specified
         it will also be of interest and consequently, the method returns True.
        If both lists (parameter and user-data) are not empty, the method returns True, if the lscpu-flags of the
        extension has a non-empty set-intersection with the lscpu-flags list, given as parameter.
        :param relevant_lscpu_flags:
        :return:
        @todo: split this method into two methods (dedicated for extension and primitive). the given implementation targets only extensions!
        prim: ["sse2", "sse4.1"]
        rel_hw_f: ["sse2"]
        @todo: prim.issubset(rel_hw_f)
        """
        if (self.__relevant_hardware_flags is None) or (len(self.__relevant_hardware_flags) == 0):
            return True
        if len(data_dict["lscpu_flags"]) == 0:
            return True
        if self.has_lscpu_disjunction(data_dict):
            for group in data_dict["lscpu_flags"]:
                elements = group.strip("[").strip("]").replace("'","").replace(" ","")
                parsed_group = elements.split(",")
                if (set(parsed_group).issubset(set(self.__relevant_hardware_flags))):
                    data_dict["lscpu_flags"] = set(parsed_group)
                    return True
            return False
        else:
            return (set(data_dict["lscpu_flags"]).issubset(set(self.__relevant_hardware_flags)))

    def has_lscpu_disjunction(self, data_dict: dict) -> bool:
        if len(set(data_dict["lscpu_flags"])) <= 1:
            return False
        else:
            for flag in set(data_dict["lscpu_flags"]):
                if "[" in flag and "]" in flag:
                    return True
            return False

    @log
    def slice_extensions(self, extension_set: TSLExtensionSet) -> TSLExtensionSet:
        if self.__relevant_hardware_flags is None:
            return deepcopy(extension_set)
        self.log(logging.INFO, f"Slicing Extensions for {self.__relevant_hardware_flags}")
        result = TSLExtensionSet()
        for extension in extension_set:
            if self.is_extension_relevant(extension.data):
                self.log(logging.DEBUG, f"Found relevant extension {extension.name}.")
                result.add_extension(deepcopy(extension), logging.WARNING)
        return result

    def __is_definition_relevant(self, definition: TSLPrimitive.Definition) -> bool:
        if intersects(set(definition.ctypes), self.__relevant_types) and intersects(set(definition.additional_simd_template_base_types), self.__relevant_types):
            if len(definition.additional_simd_template_base_type_mapping_dict) != 0:
                return len(deep_update_dict(definition.additional_simd_template_base_type_mapping_dict, list(self.__relevant_types), False)) != 0
            else:
                return True
        return False

    # def __update_definition(self, definition: TSLPrimitive.Definition):
    #     definition.ctypes = list((set(definition.ctypes)).intersection(self.__relevant_types))
    @log
    def __slice_primitive(self, primitive: TSLPrimitive) -> TSLPrimitive:
        relevant_hw_flags_set: Set[str] = set(self.__relevant_hardware_flags)
        definitions: Dict[str, List[TSLPrimitive.Definition]] = dict()
        for definition in primitive.definitions:
            copied_definition: TSLPrimitive.Definition = copy.deepcopy(definition)
            if self.is_primitive_relevant(copied_definition.data) and self.__is_definition_relevant(copied_definition):
                copied_definition.update_types(list(self.__relevant_types))
                # copied_definition.ctypes = list((set(copied_definition.ctypes)).intersection(self.__relevant_types))
                # copied_definition.additional_simd_template_base_types = list((set(copied_definition.additional_simd_template_base_types)).intersection(self.__relevant_types))
                if copied_definition.target_extension not in definitions:
                    definitions[copied_definition.target_extension] = [copied_definition]
                else:
                    #Greedy search for better fitting definitions
                    for d in definitions[copied_definition.target_extension]:
                        #if the current definition is not similar (same target extension and at least one equal ctype) to the already present definition, continue
                        if not d.is_similar(copied_definition):
                            continue
                        else:
                            if d.greater_than(copied_definition, relevant_hw_flags_set):
                                #if present definition is better fitting, remove all ctypes from definition which also exist in the present definition.
                                copied_definition.remove_ctypes(d.ctypes)
                            else:
                                #if current definition is better fitting, remove all ctypes from present one which exist in the current definition
                                d.remove_ctypes(copied_definition.ctypes)
                        if len(copied_definition.ctypes) == 0:
                            #if no ctypes are relevant for the current definition we do not have to do anything and can break out
                            break
                    definitions[copied_definition.target_extension] = [d for d in definitions[copied_definition.target_extension] if len(d.ctypes)>0]
                    if len(copied_definition.ctypes) > 0:
                        definitions[copied_definition.target_extension].append(copied_definition)

                # definitions.append(deepcopy(definition))

        if len(definitions) > 0:
            defs = []
            for val in definitions.values():
                defs.extend(val)
            return TSLPrimitive(deepcopy(primitive.declaration), defs)
            # return TSLPrimitive(deepcopy(primitive.declaration),
            #                 definitions)
        else:
            return None

    @log
    def slice_primitives(self, primitive_class_set: TSLPrimitiveClassSet) -> TSLPrimitiveClassSet:
        if self.__relevant_hardware_flags is None:
            return deepcopy(primitive_class_set)
        self.log(logging.INFO, f"Slicing Primitives for {self.__relevant_hardware_flags}")
        result = TSLPrimitiveClassSet()
        for primitive_class in primitive_class_set:
            pclass = TSLPrimitiveClass(primitive_class.file_name, primitive_class.data)
            for primitive in primitive_class:
                p = self.__slice_primitive(primitive)
                if p is not None:
                    pclass.add_primitive(p)
            if not pclass.is_empty():
                result.add_primitive_class(pclass)
        return result


