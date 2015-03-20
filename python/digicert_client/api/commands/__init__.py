#!/usr/bin/env python

from ...api import Action


class Command(Action):
    """Base class for CQRS-style Command objects."""

    def __init__(self, customer_api_key, customer_name=None, **kwargs):
        """
        Command constructor

        :param customer_api_key: the customer's DigiCert API key
        :param customer_name: the customer's DigiCert account number, e.g. '012345'
        :param kwargs:
        :return:
        """
        super(Command, self).__init__(customer_api_key=customer_api_key, customer_name=customer_name, **kwargs)

    def get_method(self):
        return 'POST'


if __name__ == '__main__':
    pass