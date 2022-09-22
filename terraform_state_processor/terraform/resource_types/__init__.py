class StateField(object):
    _path: str = None
    _processor: callable = None

    def __init__(self, path: str, processor: callable = None):
        self._path = path
        self._processor = processor

    @property
    def path(self):
        return self._path

    @property
    def processor(self):
        return self._processor

    def render(self, data):
        if self.processor is not None:
            return self.processor(data)
        return data

    def value(self, data):
        path = self.path.replace('..', '|||')
        for sub in path.split('.'):
            data = data.get(sub.replace('|||', '.')) if data is not None else data
        if data is not None:
            data = self.render(data)
        return data

    def __str__(self):
        return f"Field"

    def __repr__(self):
        return self.__str__()


class BaseResource(object):
    __datatype__ = None
    __rawdata__ = None

    module = StateField('__kwarg__')
    name = StateField('name')
    type = StateField('type')
    index = StateField('index')
    change_version = StateField('values.change_version')

    def __init__(self, data: dict, **kwargs):
        self.__kwargs__ = kwargs
        self.__rawdata__ = data

    def __getattribute__(self, item):
        item_name = item
        item = object.__getattribute__(self, item)
        if not isinstance(item, StateField):
            return item

        data = object.__getattribute__(self, '__rawdata__').copy()
        kwargs = object.__getattribute__(self, '__kwargs__')

        if item.path == '__kwarg__':
            return item.render(kwargs.get(item_name))

        return item.value(data)

    def __str__(self):
        classtype = str(type(self)).split('.')[-1][0:-2]
        fields = [x for x in self.__dir__() if isinstance(object.__getattribute__(self, x), StateField)]
        fields = [f"{x} = {getattr(self, x)}" for x in fields]
        fields = ', '.join(fields)
        name = self.name
        _type = self.type
        index = '[' + str(self.index) + ']' if self.index is not None else ''
        return f"<{classtype}> {name}{index}: {_type} ({fields})"

    def __repr__(self):
        return self.__str__()
