import inspect
import os
from glob import glob
from jinja2 import Environment, FileSystemLoader


class TemplateEnv:
    template_base: str = ""
    template_paths: list = []
    templates: list = []

    def __init__(self, template_paths: list = None):
        self.template_base = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'default')
        self.template_paths.append(os.path.abspath(self.template_base))
        if template_paths is not None:
            for path in template_paths:
                path = os.path.abspath(path)
                if os.path.isdir(path):
                    self.template_paths.append(path)
                if os.path.isfile(path):
                    self.templates.append(path)
        self._index_templates()

    def _index_templates(self):
        for path in self.template_paths:
            files = glob(os.path.join(path, '**'), recursive=True)
            for file in files:
                file = os.path.abspath(file)
                if os.path.isfile(file):
                    self.templates.append(os.path.abspath(file))

    def find_template(self, template: str):
        template = os.path.normpath(template)

        search = []

        # Search if template shows up
        for path in self.templates:
            if template in path:
                search.append(path)

        # If there are multiple, look at the basename first.
        if len(search) > 1:
            for path in search.copy():
                if template not in os.path.basename(path):
                    search.remove(path)

        # If there are multiple, only show ones outside the module path
        if len(search) > 1:
            for path in search.copy():
                if self.template_base in path:
                    search.remove(path)

        # If there are multiple, only show ones in the CWD
        if len(search) > 1:
            for path in search.copy():
                if os.path.abspath(os.getcwd()) not in path:
                    search.remove(path)

        # If there are multiple, get the one in the shallowest path
        if len(search) > 1:
            cur_path = []
            cur_count = 0
            for path in search.copy():
                test_path = path.replace(os.path.abspath(os.getcwd()), '').replace('\\', '/')
                count = len([x for x in test_path.split('/') if len(x) > 0])
                if count < cur_count or cur_count == 0:
                    cur_count = count
                    cur_path = [path]
                elif count == cur_count and cur_count > 0:
                    cur_path.append(path)
            search = cur_path

        # If there are still multiple, the shortest name will come first
        search.sort()
        return search[0] if len(search) > 0 else None

    def render_template(self, template: str, abs_path: bool = False, **kwargs):
        if not abs_path:
            template = self.find_template(template)
        is_file = os.path.isfile(template) if template is not None else False
        if not is_file:
            return LookupError(f"Template not found.")

        template_name = os.path.basename(template)
        template_dir = os.path.dirname(template)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        return template.render(**kwargs)
