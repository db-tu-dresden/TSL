from core.tvl_config import config


def create_readme():
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
                return key_name
        already_seen_entries[key_name] = data_dict
        return None

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


    schema_dict = config.schema_dict

    known_links = {}
    extension_dict = transform_dict_links_and_anchors(transform_dict_remove_levels(schema_dict["extension"]), known_links)
    primitive_dict = transform_dict_links_and_anchors(transform_dict_remove_levels(schema_dict["primitive"]), known_links)

    jinja_template = config.get_template("readme_md_primitive_data_files")
    print(jinja_template.render({"extension": extension_dict, "primitive": primitive_dict}))

