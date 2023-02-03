from core.tvl_config import config
from flask import Flask
from pathlib import Path

from editor.template_generator.template_generator import generate_primitive_flask_template
from utils.yaml_utils import yaml_load


app = Flask(__name__, static_url_path="/editor/static", template_folder="/editor/templates")
config.setup(yaml_load(Path("config/default_conf.yaml")))

@app.route('/')
def hello_world():  # put application's code here
    return generate_primitive_flask_template()
    # return f"{config.get_schema('primitive')}"


if __name__ == '__main__':

    app.run(debug=True, use_reloader=False)
