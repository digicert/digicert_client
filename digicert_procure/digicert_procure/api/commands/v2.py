class V2Command(object):
    def __init__(self, customer_api_key, **kwargs):
        self.set_header('X-DC-DEVKEY', customer_api_key)


class OrderCertificateCommand(V2Command):
    def __init__(self, customer_api_key, **kwargs):
        super(OrderCertificateCommand, self).__init__(customer_api_key=customer_api_key, **kwargs)

    def get_path(self):
        return '/services/v2/'  # plus more

if __name__ == '__main__':
    pass