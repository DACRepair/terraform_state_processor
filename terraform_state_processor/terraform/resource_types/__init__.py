class BaseResource(object):
    __datatype__ = None
    __rawdata__ = None

    module = '__kwarg__'
    name = 'name'
    type = 'type'
    index = 'index'
    change_version = 'values.change_version'

    def __init__(self, data: dict, **kwargs):
        self.__kwargs__ = kwargs
        self.__rawdata__ = data

    def __getattribute__(self, item):
        if item in super(object, self).__getattribute__('__dir__')():
            return object.__getattribute__(self, item)

        data = object.__getattribute__(self, '__rawdata__').copy()
        kwargs = object.__getattribute__(self, '__kwargs__')

        if object.__getattribute__(self, item) == '__kwarg__':
            return kwargs.get(item)

        item = kwargs.get(item, object.__getattribute__(self, item))
        if item is not None:
            item = item.replace('..', '|||')
            for sub in item.split('.'):
                data = data.get(sub.replace('|||', '.')) if data is not None else data
            return data
        return None

    def __str__(self):
        classtype = str(type(self)).split('.')[-1][0:-2]
        fields = [f"{x} = {getattr(self, x)}" for x in self.__dir__() if not x.startswith('_') and not callable(x)]
        fields = ', '.join(fields)
        name = self.name
        _type = self.type
        index = '[' + str(self.index) + ']' if self.index is not None else ''
        return f"<{classtype}> {name}{index}: {_type} ({fields})"

    def __repr__(self):
        return self.__str__()
