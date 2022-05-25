from typing import Dict

from utils.log_utils import LogInit, log
from utils.yaml_utils import YamlDataType


class Schema:
    class TypeCastError(Exception):
        def __init__(self, message, errors):
            super().__init__(message)
            self.message = message
            self.error = errors

        def add_field(self, fieldname: str, field_data: dict):
            self.error["fieldname"] = fieldname
            self.error["description"] = field_data["brief"]
            if "example" in field_data:
                self.error["example"] = field_data["example"]

        def __str__(self):
            errors = ", ".join(f"{x}: {self.error[x]}" for x in self.error)
            return f"{self.message} ({errors})"

    class RequiredFieldError(Exception):
        def __init__(self, message, errors):
            super().__init__(message)
            self.message = message
            self.error = errors

        def __str__(self):
            errors = ", ".join(f"{x}: {self.error[x]}" for x in self.error)
            return f"{self.message} ({errors})"

    class UnknownTypeError(Exception):
        def __init__(self, message, errors):
            super().__init__(message)
            self.message = message
            self.error = errors

        def __str__(self):
            errors = ", ".join(f"{x}: {self.error[x]}" for x in self.error)
            return f"{self.message} ({errors})"

    class SchemaNode:
        @LogInit()
        def __init__(self, schema_dict: YamlDataType) -> None:
            if "required" in schema_dict or "optional" in schema_dict:
                if "required" in schema_dict:
                    self.__required_fields: Dict[str, Schema.SchemaNode] = {
                        field: self.__class__(schema_dict["required"][field])
                        for
                        field in schema_dict["required"]}
                else:
                    self.__required_fields = {}
                if "optional" in schema_dict:
                    self.__optional_fields: Dict[str, Schema.SchemaNode] = {
                        field: self.__class__(schema_dict["optional"][field])
                        for
                        field in schema_dict["optional"]}
                else:
                    self.__optional_fields = {}
                self.__complex = True
            else:
                if isinstance(schema_dict, dict):
                    self.__complex = False
                    self.__type: str = schema_dict["type"]
                    self.__brief: str = schema_dict["brief"]
                    self.__example = schema_dict["example"] if "example" in schema_dict else None
                    self.__default = schema_dict["default"] if "default" in schema_dict else None
                    self.__entry_type = self.__class__(
                        schema_dict["entry_type"]) if "entry_type" in schema_dict else None
                else:
                    self.__complex = False
                    self.__type: str = schema_dict
                    self.__brief = None
                    self.__example = None
                    self.__default = None
                    self.__entry_type = None

        def __has_default_value(self) -> bool:
            return self.__default is not None

        def __get_default_value(self) -> YamlDataType:
            return self.__default

        @log
        def validate(self, data: YamlDataType) -> YamlDataType:
            if self.__complex:
                for required_field_name in self.__required_fields:
                    if required_field_name not in data:
                        raise Schema.RequiredFieldError("Required field missing",
                                                        {   "data": data,
                                                            "required_fields": str(self.__required_fields),
                                                            "fieldname": required_field_name
                                                         })
                    data[required_field_name] = self.__required_fields[required_field_name].validate(
                        data[required_field_name])
                for optional_field_name in self.__optional_fields:
                    if optional_field_name not in data:
                        if self.__optional_fields[optional_field_name].__has_default_value():
                            data[optional_field_name] = self.__optional_fields[
                                optional_field_name].__get_default_value()
                    else:
                        data[optional_field_name] = self.__optional_fields[optional_field_name].validate(
                            data[optional_field_name])
                return data
            else:
                if isinstance(data, eval(self.__type)):
                    casted_data = data
                else:
                    try:
                        if self.__entry_type is not None:
                            if "list" == self.__type:
                                casted_data = [data]
                        else:
                            casted_data = eval(self.__type)(data)
                    except:
                        raise Schema.TypeCastError("Cast was not possible.",
                                                   {"cast candidate": data, "target type": self.__type})
                if self.__entry_type is not None:
                    if "list" == self.__type:
                        return [self.__entry_type.validate(d) for d in casted_data]
                    elif "dict" == self.__type:
                        casted_data = self.__entry_type.validate(casted_data)
                    else:
                        raise Schema.UnknownTypeError("Type has to be list or dict", {"type": self.__type})

                return casted_data

    @LogInit()
    def __init__(self, schema_dict: YamlDataType) -> None:
        self._schema = Schema.SchemaNode(schema_dict)

    @log
    def validate(self, other_dict: YamlDataType) -> dict:
        return self._schema.validate(other_dict)
