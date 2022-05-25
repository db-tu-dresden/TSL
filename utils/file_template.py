from pathlib import Path


def load_template_from_file(file: Path) -> str:
    """
    Loads a string from a given file to be further processed as a Jinja2 template.
    :param file: Path to file which contains the template.
    :return: string
    """
    rfile = file.resolve()
    error_msg = f"An error occurred while creating Template from {rfile}"
    if rfile.is_file():
        if rfile.suffix == ".template":
            return rfile.read_text()
        else:
            print(f"{error_msg}. Wrong file suffix (should be: .template).")
            raise ValueError
    else:
        print(f"{error_msg}. File does not exist.")
        raise FileExistsError


