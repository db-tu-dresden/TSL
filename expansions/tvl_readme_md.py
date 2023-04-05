from pathlib import Path
from typing import List, Dict, Set

from core.tvl_config import config
from utils.yaml_utils import yaml_load_with_anchor_information


def create_toc_list(required_fields: List[str], optional_fields: List[str]):
    if len(required_fields) < len(optional_fields):
        required_fields.extend([""]*(len(optional_fields)-len(required_fields)))
    elif len(required_fields) > len(optional_fields):
        optional_fields.extend([""]*(len(required_fields)-len(optional_fields)))
    return [(required_fields[idx], optional_fields[idx]) for idx in range(len(required_fields))]

def create_readme():

    def get_anchor_names(yaml_dict, exclude_keys: List[str] = [], entry_name: str = "", result: Set[str] = None):
        if result is None:
            result: Set[str] = set()
        if yaml_dict.yaml_anchor() is not None:
            if yaml_dict.yaml_anchor().value not in result:
                result.add(yaml_dict.yaml_anchor().value)
        for key, value in yaml_dict.items():
            if key not in exclude_keys:
                if isinstance(value, dict):
                    get_anchor_names(value, exclude_keys, key, result)
        return result
    # def find_anchor(yaml_dict, entry_name: str ="", result: Dict[str, Dict[str, bool]]=None):
        # if result is None:
        #     result: Dict[str, Dict[str, bool]] = dict()
        # if yaml_dict.yaml_anchor() is not None:
        #     if yaml_dict.yaml_anchor().value not in result:
        #         result[yaml_dict.yaml_anchor().value] = {"key_name": entry_name, "already_processed": False}
        # for key, value in yaml_dict.items():
        #     if isinstance(value, dict):
        #         find_anchor(value, key, result)
        # return result

    def find_anchor_by_name(yaml_dict, anchor_name: str):
        if yaml_dict.yaml_anchor() is not None:
            if anchor_name == yaml_dict.yaml_anchor().value:
                return yaml_dict
        for key, value in yaml_dict.items():
            if isinstance(value, dict):
                result = find_anchor_by_name(value, anchor_name)
                if result:
                    return result
        return None

    def is_complex_field(yaml_dict):
        if not isinstance(yaml_dict, dict):
            return False
        if "required" in yaml_dict or "optional" in yaml_dict:
            return True
        return False

    def iterate_complex_field(yaml_dict, field_type):
        if field_type in yaml_dict:
            fields: dict = yaml_dict[field_type]
            for field_name in sorted([k for k in fields.keys()]):
                yield (field_name, fields[field_name])


    def find_dict(key_name: str, data_dict: dict, already_seen_entries: dict):
        '''
        already_seen_entries: {key_name: data_dict}
        '''
        for k,v in already_seen_entries.items():
            if data_dict == v:
                print("It seems that")
                print(f"{key_name} -> {data_dict}")
                print("equals")
                print(f"{k} -> {v}")
                return key_name
        already_seen_entries[key_name] = data_dict
        return None

    # def traverse_depth_first(key_name: str, data_dict: dict, already_seen_entries: dict):
    #     if is_complex_field(data_dict):
    #         result = []
    #         for k,v in iterate_complex_field(data_dict, "required"):
    #             if (link_name := find_dict(k, v, already_seen_entries)) is not None:
    #                 result.append({"field_name": k, "links_to": link_name, "presence_string" : "required"})
    #             else:
    #                 result.append({"field_name": k, "presence_string" : "required", "data": traverse_depth_first(k, v, already_seen_entries)})
    #         for k, v in iterate_complex_field(data_dict, "optional"):
    #             if (link_name := find_dict(k, v, already_seen_entries)) is not None:
    #                 result.append({"field_name": k, "links_to": link_name, "presence_string": "optional"})
    #             else:
    #                 result.append({"field_name": k, "presence_string": "optional",
    #                                "data": traverse_depth_first(k, v, already_seen_entries)})
    #         return result
    #     elif isinstance(data_dict, dict):
    #         result = [{k : traverse_depth_first(k, v, already_seen_entries)} for k, v in data_dict.items()]
    #         return result
    #     else:
    #         return data_dict


    def transform_dict_remove_levels(data_dict: dict):
        if is_complex_field(data_dict):
            result = {(k, "required"): transform_dict_remove_levels(v) for k, v in
                      iterate_complex_field(data_dict, "required")}
            result.update({(k, "optional"): transform_dict_remove_levels(v) for k, v in
                      iterate_complex_field(data_dict, "optional")})
            return result
        elif isinstance(data_dict, dict):
            return {k: transform_dict_remove_levels(v) for k,v in data_dict.items()}
        else:
            return data_dict

    def transform_dict_links_and_anchors(data_dict: dict, already_seen_entries: dict):
        if not isinstance(data_dict, dict):
            return data_dict
        result = {}
        for k,v in data_dict.items():
            if isinstance(v, dict):
                if (link := find_dict(k, v, already_seen_entries)) is not None:
                    result[k] = {'links_to': link}
                else:
                    result[k] = transform_dict_links_and_anchors(v, already_seen_entries)
            else:
                if isinstance(v, str) and len(v) == 0:
                    result[k] = '""'
                else:
                    result[k] = v
        return result





    schema_file = Path(config.configuration_files_dict["schema_file"]).resolve()
    from ruamel.yaml import CommentedMap
    schema_data:CommentedMap = yaml_load_with_anchor_information(schema_file)



    extension_links_names = get_anchor_names(schema_data["extension"])
    primitive_links_names = get_anchor_names(schema_data["primitive"])
    links_names_referenced_by_ext_and_prim = sorted(list(extension_links_names.intersection(primitive_links_names)))
    top_level_links_names = get_anchor_names(schema_data, exclude_keys = ["extension", "primitive"])
    extension_links_names = extension_links_names.difference(links_names_referenced_by_ext_and_prim)
    primitive_links_names = primitive_links_names.difference(links_names_referenced_by_ext_and_prim)


    global_fields = [{ link_name : find_anchor_by_name(schema_data, link_name)} for link_name in links_names_referenced_by_ext_and_prim]
    # for field in global_fields:
    #     print(field)

    links = {}
    # x = traverse_depth_first("extension", schema_data["extension"], links)
    # y = traverse_depth_first("primitive", schema_data["primitive"], links)

    x = transform_dict_remove_levels(schema_data["primitive"])
    # y = x
    y = transform_dict_links_and_anchors(x, {})
    for k,v in y.items():
        print(f"{k} -> {v}")
    z = config.get_template("readme_md_primitive_data_files")
    print(z.render({"data": y}))


    # x = breadth_first_traverse({"field_name": "primitive", "data": schema_data["primitive"]})
    # print("============================")
    # for y in x:
    #     print(y)
    # def create_value_dict(data_dict, key_name, known_anchors):
    #     result = {k:v for k,v in data_dict[key_name].items()}
    #
    #     if key_name in known_anchors:
    #         result["links_to"] =
    # schema = schema_data["primitive"]
    # required = []
    #
    # x = schema["required"]
    # required_fields = [(required_key, {k:v for k,v in schema["required"][required_key].items()}) for required_key in schema["required"]]
    # required_fields.sort(key=lambda x: x[0])
    # optional_fields = [(optional_key, {k:v for k,v in schema["optional"][optional_key].items()}) for optional_key in schema["optional"]]
    # optional_fields.sort(key=lambda x: x[0])
    # for entry in optional_fields:
    #     print(entry[0])
    #     for k,v in entry[1].items():
    #         print(f"\t{k} -> {v}")



