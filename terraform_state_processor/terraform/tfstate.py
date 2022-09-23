import importlib
import importlib.util
import inspect
import glob
import os.path
import pathlib
import pkgutil
import json


class TerraformState:
    _package_base = None
    _custom_base = None
    _raw_state = dict()
    _resource_processors = dict()

    format_version = None
    terraform_version = None

    entries = []
    resources = []

    def __init__(self, jsondata: str, custom_base: str = None, resource_base: str = 'resource_types'):
        self._raw_state = json.loads(jsondata)
        self._package_base = self.__module__.rsplit('.', 1)[0]
        self._custom_base = custom_base

        self._resource_processors = self._load_resource_processors(resource_base)
        self._resource_processors.update(self._load_external_resource_processors(self._custom_base))

        self._process_statedata()

    @staticmethod
    def _inherits_from(child, parent, match: bool = False):
        if inspect.isclass(child):
            if parent in [c.__name__ for c in inspect.getmro(child)[1:]]:
                return True
            if parent == child.__name__ and match:
                return True
        return False

    def _load_resource_processors(self, package_base: str):
        _processors = {}

        processors_path = f"{self._package_base}.{package_base}"
        processors_fpath = importlib.util.find_spec(processors_path).submodule_search_locations

        base_spec = importlib.util.find_spec(processors_path)
        base_module = importlib.util.module_from_spec(base_spec)
        base_spec.loader.exec_module(base_module)

        base = [getattr(base_module, x) for x in base_module.__dir__()]
        base = [x for x in base if hasattr(x, '__datatype__')][0]
        _processors.update({base.__datatype__: base})

        for importer, modname, ispkg in pkgutil.walk_packages(path=processors_fpath):
            module_path = f"{processors_path}.{modname}"
            spec = importlib.util.find_spec(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            classes = [getattr(module, x) for x in module.__dir__()]
            for _class in [x for x in classes if hasattr(x, '__datatype__')]:
                if self._inherits_from(_class, base.__name__, match=True):
                    if _class not in _processors.values():
                        _processors.update({_class.__datatype__: _class})
        return _processors

    def _load_external_resource_processors(self, package_dir: str):
        if not package_dir:
            return {}

        package_dir = os.path.abspath(package_dir)
        if not os.path.isdir(package_dir):
            return {}

        _processors = {}
        base_processor = self._resource_processors.get(None)

        paths = glob.glob(os.path.normpath(os.path.join(package_dir, '*.py')))
        for path in paths:
            module_name = pathlib.Path(path).stem
            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            classes = [getattr(module, x) for x in module.__dir__()]
            for _class in [x for x in classes if hasattr(x, '__datatype__')]:
                if self._inherits_from(_class, base_processor.__name__):
                    _processors.update({_class.__datatype__: _class})
        return _processors

    def _process_statedata(self):
        self.format_version = self._raw_state.get('format_version')
        self.terraform_version = self._raw_state.get('terraform_version')

        values = self._raw_state.get('values')
        root = values.get('root_module', {}).values()
        modules = []
        for value in root:
            if isinstance(value, list):
                modules.extend(value)
        modules = [x for x in modules if isinstance(x, dict)]
        modules = [x for x in modules if 'resources' in x.keys()]
        for module in modules:
            address = module.get('address')
            address = address.split('.')
            address = address[1:]
            address = '.'.join(address)

            resources = module.get('resources')
            for item in resources:
                _type = item.get('type')
                _type = _type if _type in self._resource_processors.keys() else None
                processor = self._resource_processors.get(_type)
                if processor is not None:
                    self.resources.append(processor(item, module=address))

    def __str__(self):
        header = f"<Terraform State Processor[Format {self.format_version}, Terraform {self.terraform_version}]"
        stats = f"{len(self.resources)} Resource Objects Loaded.>"
        return f"{header}: {stats}"

    def __repr__(self):
        return self.__str__()
