import json


class V2ResultEntity(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if not self._handle_special(k, v):
                setattr(self, k, v)

    def _handle_special(self, k, v):
        return False

    def __str__(self):
        return self.to_s(self.__dict__)

    def to_s(self, d):
        return json.dumps(d, indent=2, separators=(',', ': '))


class Container(V2ResultEntity):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)


class User(V2ResultEntity):
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def _handle_special(self, k, v):
        if k == 'container':
            setattr(self, k, Container(**v))
            return True
        return False

    def __str__(self):
        d = self.__dict__
        d['container'] = self.__dict__['container'].__dict__
        return self.to_s(d)
