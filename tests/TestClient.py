#!/usr/bin/env python

from sys import argv, exit
from digicert.api.commands import OrderCertificateCommand
from digicert.api.queries import OrderDetailsQuery, RetrieveCertificateQuery

customer_name='070457'
customer_api_key='3v8pl7rb3hhvwtndhx0zrzlp1srqzmp4'

def usage():
    print 'TestClient.py order <path_to_cert_file>|details <order_id>|retrieve <order_id>'
    exit(1)


def order_certificate():
    cmd = OrderCertificateCommand(
        customer_name=customer_name,
        customer_api_key=customer_api_key,
        certificate_type=OrderCertificateCommand.CertificateType.SSLPLUS,
        validity=OrderCertificateCommand.Validity.ONE_YEAR,
        common_name='fake.com',
        org_name='Fake Co.',
        org_addr1='123 Nowhere Lane',
        org_city='Nowhere',
        org_state='UT',
        org_zip='12345',
        org_country='US',
        org_contact_firstname='Bill',
        org_contact_lastname='Billson',
        org_contact_email='bbillson@fakeco.biz',
        org_contact_telephone='2345556789',
        csr='MIICmTCCAYECAQAwVDELMAkGA1UEBhMCVVMxDTALBgNVBAgTBFV0YWgxEDAOBgNV' +
            'BAcTB05vd2hlcmUxETAPBgNVBAoTCEZha2UgQ28uMREwDwYDVQQDEwhmYWtlLmNv' +
            'bTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAM4Vg7KLqsFcKmmOCh1B' +
            'HaKaDAkB0uy2fejSm9jRVeHVtycx2/Lb7qKVor4S82ZSNi0/LPrOVeTTf7KqajWE' +
            '4PYZ5JeXpA/DRbyHN+oteiYGq+0X5hdo7rEikvgCttlC7qK5s2WyE0OetuBlHwi2' +
            'U0GguA4Gp8Vdm4GbB4s5zFW88F0QeGHjabpeYZXlcPO90fzvSfhZvfkg4agFpS7A' +
            'T0M3TNR99u16Duub6jMDTIBqA7DMbIQu3H8davCYT33n82qrq3aakMKgKSIbKsrz' +
            'lB9biIaNSYkQ6piJyoTVnjpVX3s9SdQUZl5ytPffaUlDestP6j2DaEXuQfG9yW76' +
            'eQUCAwEAAaAAMA0GCSqGSIb3DQEBBQUAA4IBAQAcvcL9BSkUuXu9wmeinKZ5qkid' +
            'XfRciQ/rukZTEJGeDbzXea3XUD+3QKm4Mny4eZ3DlB4DuqQoxvFi00YRqId2AWNF' +
            'Wutg0abyzKy1y9h7MdNtTPfXFUV8kkDcebCvJfqoxneYRjDSx+ozk9ON/B9aCwT7' +
            'IDckFyKSId8cK79uNsnUvAvrgunSVadu+W3lO50ZmG7ldUAB4BN2LrrkCZLqgQwB' +
            '9BxYzVCOWU70I9NhZLrT10gHWKOXAW3zH0zWnQwxnlfpjTsm585f4i7IXfQZC7Wo' +
            'O7vhtZdOoiM+mqbNsdjZnTi7yk+9Rf934JdQmfe0wyT3KF5cz5vS/O9KyaAu')
    response = cmd.send()
    print response

def order_details(order_id):
    req = OrderDetailsQuery(customer_name=customer_name,
                            customer_api_key=customer_api_key,
                            order_id=order_id)
    response = req.send()
    print response



def retrieve_certificate(order_id):
    req = RetrieveCertificateQuery(customer_name=customer_name,
                                   customer_api_key=customer_api_key,
                                   order_id=order_id)
    response = req.send()
    print response


if __name__ == '__main__':
    if len(argv) < 2:
        usage()
    if argv[1] == 'order':
        order_certificate()
    elif argv[1] == 'details':
        if len(argv) < 3:
            usage()
        order_details(argv[2])
    elif argv[1] == 'retrieve':
        if len(argv) < 3:
            usage()
        retrieve_certificate(argv[2])
    else:
        usage()