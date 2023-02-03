import os
from pathlib import Path

from core.tvl_config import config
from utils.file_template import load_template_from_file
from utils.yaml_schema import Schema

# style="border:1px solid black;"
# <div class="row">
#    <div class="col-md-12">
def build_template(node: Schema.SchemaNode, form_template, level = 0):
    if not node.is_complex:
        if node.entry_type is None:
            return form_template.render({
                    "level": level,
                    "identifier": node.identifier,
                    "type": node.type,
                    "inner": ""
                })
        else:
            return form_template.render({
                "level": level,
                "identifier": node.identifier,
                "type": node.type,
                "inner": build_template(node.entry_type, form_template, level+1)
            })
    else:
        inner = ""
        for required in node.required_fields():
            inner += build_template(required, form_template, level+1)
        for optional in node.optional_fields():
            inner += build_template(optional, form_template, level+1)
        return form_template.render({
            "level": level,
            "identifier": node.identifier,
            "type": node.type,
            "inner": inner
        })

def generate_primitive_flask_template():
    form_template = config.create_template(load_template_from_file(Path("./editor/template_generator/templates/form.template")))
    # result = ""
    # indent = 0
    extension_schema = config.get_schema("primitive")
    return build_template(extension_schema.root, form_template)
    # for node in extension_schema.depth_first_iter():
    #     if node is None:
    #         indent = indent - 2
    #         form_template.render()
    #         current = ""
    #     else:
    #         if node.is_complex:
    #
    #         result += f"{'&nbsp' * indent}{node.type} - {node.identifier}<br/>"
    #         indent = indent + 2
    # return result