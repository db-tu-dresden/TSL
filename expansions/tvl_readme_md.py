from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Tuple, Generator, Dict, Any

from core.tvl_config import config


def create_primitive_data_readme(readme_md_root_path: Path):
    def is_complex_field(yaml_dict):
        if not isinstance(yaml_dict, dict):
            return False
        if "required" in yaml_dict or "optional" in yaml_dict:
            return True
        return False

    def update_name(name: str, predecessor: str = ""):
        new_name = re.sub(r'\W+', '-', name)
        new_predecessor = re.sub(r'\W+', '-', predecessor)
        if len(predecessor) == 0:
            return new_name
        return f"{new_predecessor}--{new_name}"

    def iterate_complex_field(yaml_dict, field_type, predecessor_name: str = ""):
        if field_type in yaml_dict:
            fields: dict = yaml_dict[field_type]
            for field_name in sorted([k for k in fields.keys()]):
                yield field_name, update_name(field_name, predecessor_name), fields[field_name]

    def find_dict(key_name: tuple, data_dict: dict, already_seen_entries: Dict[Tuple, Dict[str, Any | None]]):
        if not isinstance(key_name, tuple):
            raise ValueError(f"{key_name} must be tuple")
        if isinstance(data_dict, str):
            raise ValueError(f"{key_name}: {data_dict} must be dict not str")
        """
        already_seen_entries: {key_name: data_dict}
        """
        for k, v in already_seen_entries.items():
            if data_dict == v:
                return k
        already_seen_entries[key_name] = data_dict
        return None

    def transform_dict_remove_levels(data_dict: dict, parent_name: str = ""):
        if is_complex_field(data_dict):
            result = {(field_name, field_id, "required"): transform_dict_remove_levels(value, field_id) for
                      field_name, field_id, value in
                      iterate_complex_field(data_dict, "required", parent_name)}
            result.update({(field_name, field_id, "optional"): transform_dict_remove_levels(value, field_id) for
                           field_name, field_id, value in
                           iterate_complex_field(data_dict, "optional", parent_name)})
            return result
        elif isinstance(data_dict, dict):
            return {update_name(k, ""): transform_dict_remove_levels(v, update_name(k, parent_name)) for k, v in
                    data_dict.items()}
        else:
            return data_dict

    def transform_dict_links_and_anchors(data_dict: dict, already_seen_entries: dict):
        if not isinstance(data_dict, dict):
            return data_dict
        result = {}
        for k, v in data_dict.items():
            if isinstance(v, dict):
                link = None
                if isinstance(k, tuple):
                    link = find_dict(k, v, already_seen_entries)
                if link is not None:
                    result[k] = {'links_to': link}
                else:
                    result[k] = transform_dict_links_and_anchors(v, already_seen_entries)
            else:
                if isinstance(v, str) and len(v) == 0:
                    result[k] = '""'
                else:
                    result[k] = v
        return result

    def get_field_names(field_dict: dict, presence_spec: str) -> Generator[Tuple[str, str], None, None]:
        if isinstance(field_dict, dict):
            for k, v in field_dict.items():
                if isinstance(k, tuple):
                    if k[1].count('--') == 1:
                        if presence_spec == k[2]:
                            yield (k[0], k[1])
                    yield from get_field_names(v, presence_spec)
                elif isinstance(v, dict):
                    yield from get_field_names(v, presence_spec)

    schema_dict = config.schema_dict

    known_links = {}
    extension_dict = transform_dict_links_and_anchors(
        transform_dict_remove_levels(schema_dict["extension"], "extension"), known_links)
    extension_required_fields_list = [x for x in get_field_names(extension_dict, "required")]
    extension_optional_fields_list = [x for x in get_field_names(extension_dict, "optional")]
    extension_fields_list = list(itertools.zip_longest(extension_required_fields_list, extension_optional_fields_list))
    primitive_dict = transform_dict_links_and_anchors(
        transform_dict_remove_levels(schema_dict["primitive"], "primitive"), known_links)
    primitive_required_fields_list = [x for x in get_field_names(primitive_dict, "required")]
    primitive_optional_fields_list = [x for x in get_field_names(primitive_dict, "optional")]
    primitive_fields_list = list(itertools.zip_longest(primitive_required_fields_list, primitive_optional_fields_list))
    readme_md_root_path.joinpath("primitive_data/README.md").write_text(
        config.get_template("readme_md_primitive_data_files").render(
            {
                "extension": extension_dict,
                "extension_fields_list": extension_fields_list,
                "primitive": primitive_dict,
                "primitive_fields_list": primitive_fields_list
            }
        )
    )


def create_readme():
    if not config.expansion_enabled("readme_md"):
        return
    readme_config_dict: dict = config.get_expansion_config("readme_md")

    create_primitive_data_readme(Path(readme_config_dict["root_path"]))
