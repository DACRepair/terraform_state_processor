import os
from jinja2 import Environment, FileSystemLoader


class TemplateEnv:
    template_path = ""

    def __init__(self, template_path: str = None):
        if template_path is None:
            template_path = f"./{self.__module__.rsplit('.', 1)[0].replace('.', '/')}/default"
        self.template_path = os.path.normpath(os.path.abspath(template_path))
        print(self.template_path)

    def find_template(self, template: str):
        test_path = os.path.normpath(os.path.abspath(f"{self.template_path}/{template}.j2"))
        if os.path.isfile(test_path):
            return os.path.realpath(os.path.dirname(test_path)), os.path.basename(test_path)

        test_path = os.path.normpath(os.path.abspath(template))
        if os.path.isfile(test_path):
            return os.path.realpath(os.path.dirname(test_path)), os.path.basename(test_path)

        return None

    def render_template(self, template_path: str, template_name: str, **kwargs):
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template(template_name)
        return template.render(**kwargs)
