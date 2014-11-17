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


class V2ContainerizedResultEntity(V2ResultEntity):
    def __init__(self, **kwargs):
        super(V2ContainerizedResultEntity, self).__init__(**kwargs)

    def _handle_special(self, k, v):
        if k == 'container':
            setattr(self, k, Container(**v))
            return True
        return False

    def __str__(self):
        d = dict(self.__dict__)
        d['container'] = self.__dict__['container'].__dict__
        return self.to_s(d)


class User(V2ContainerizedResultEntity):
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


class Organization(V2ContainerizedResultEntity):
    def __init__(self, **kwargs):
        super(Organization, self).__init__(**kwargs)

    def matches(self, org_dict):
        match_dict = dict(self.__dict__)
        del match_dict['status']
        del match_dict['container']
        del match_dict['type']
        del match_dict['id']
        if 'address' in match_dict:
            match_dict['addr1'] = match_dict['address']
            del match_dict['address']
        if 'address2' in match_dict:
            match_dict['addr2'] = match_dict['address2']
            del match_dict['address2']

        for k, v in match_dict.items():
            if not k in org_dict:
                return False
            elif org_dict[k].lower() != v.lower():
                return False
        return True


class V2ResultEntityCollection(object):
    def __init__(self, list_of_collectibles):
        self.collectibles = list_of_collectibles

    def __str__(self):
        return '[%s]' % ', '.join([c.__str__() for c in self.collectibles])

    def __iter__(self):
        for c in self.collectibles:
            yield c


class Organizations(V2ResultEntityCollection):
    def __init__(self, list_of_organizations):
        super(Organizations, self).__init__(list_of_organizations)


class Domain(V2ContainerizedResultEntity):
    def __init__(self, **kwargs):
        super(Domain, self).__init__(**kwargs)

    def matches(self, domain):
        return 'name' in self.__dict__ and domain.lower() == self.name.lower()


class Domains(V2ResultEntityCollection):
    def __init__(self, list_of_domains):
        super(Domains, self).__init__(list_of_domains)


class CertificateOrderResult(V2ResultEntity):
    def __init__(self, **kwargs):
        super(CertificateOrderResult, self).__init__(**kwargs)


class CertificateDetailsResult(V2ResultEntity):
    def __init__(self, **kwargs):
        super(CertificateDetailsResult, self).__init__(**kwargs)


class RetrieveCertificateResult(V2ResultEntity):
    def __init__(self, **kwargs):
        super(RetrieveCertificateResult, self).__init__(**kwargs)
