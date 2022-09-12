import importlib
import importlib.util
import inspect
import pkgutil
import json


class TerraformState:
    _package_base = None
    _raw_state = dict
    _resource_processors = {}
    _data_processors = {}

    data = []
    resources = []

    def __init__(self, jsondata: str, package_base: str = None, resource_base: str = 'resource_types',
                 data_base: str = 'data_types'):
        self._raw_state = json.loads(jsondata)

        self._package_base = package_base if package_base is not None else self.__module__.rsplit('.', 1)[0]
        self._data_processors = self._load_resource_processors(data_base)
        self._resource_processors = self._load_resource_processors(resource_base)

        self._process_statedata()

    @staticmethod
    def _inherits_from(child, parent):
        if inspect.isclass(child):
            if parent in [c.__name__ for c in inspect.getmro(child)[1:]]:
                return True
            if parent == child.__name__:
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
                if self._inherits_from(_class, base.__name__):
                    if _class not in _processors.values():
                        _processors.update({_class.__datatype__: _class})
        return _processors

    def _process_statedata(self):
        values = self._raw_state.get('values')
        root = values.get('root_module', {}).values()
        modules = []
        for value in root:
            if isinstance(value, list):
                modules.extend(value)
        modules = [x for x in modules if isinstance(x, dict)]
        modules = [x for x in modules if 'resources' in x.keys()]
        modules = [item for resources in modules for item in resources.get('resources')]

        for item in modules:
            mode = item.get('mode')
            _type = item.get('type')
            if mode == 'data':
                _datatype = _type if _type in self._data_processors.keys() else None
                processor = self._data_processors.get(_datatype)
                if processor is not None:
                    self.data.append(processor(item))
            if mode == 'managed':
                _managedtype = _type if _type in self._resource_processors.keys() else None
                processor = self._resource_processors.get(_managedtype)
                if processor is not None:
                    self.resources.append(processor(item))
