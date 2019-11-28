#!/usr/bin/env python

from sys import argv, exit
from os import makedirs
from os.path import exists, dirname, expanduser, splitext
from http.client import HTTPSConnection

from .. import Validity, CertificateType, CertificateOrder

use_verified_http = False


def usage():
    print('TestClient.py order|details <order_id>|download <order_id>')
    exit(1)


def read_default_properties(path):
    p = {}
    if exists(path):
        with open(path) as pf:
            for line in pf.readlines():
                line = line.strip()
                if not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    p[key] = value
    return p


def validate_certificate_validity(validity, properties):
    if Validity.THREE_YEARS == validity and \
        (properties['certificate_type'] == CertificateType.EVSSL or
            properties['certificate_type'] == CertificateType.EVMULTI):
        return 'Select only 1 or 2 years for certificate type "%s"' % properties['certificate_type']
    return None


def validate_two_chars(p, properties):
    if 2 != len(p):
        return 'Input must be a two-character code'
    return None


def validate_zip(p, properties):
    if 5 != len(p) or not p.isdigit():
        return 'Zip code must be five digits'
    return None


def validate_telephone(p, properties):
    if 10 != len(p) or not p.isdigit():
        return 'Telephone must be 10 digits'
    return None


def validate_csr_path(p, properties):
    if not exists(p):
        return 'No such file "%s"' % p
    if '.csr' != splitext(p)[1]:
        return 'File "%s" does not have .csr extension' % p
    with open(p) as csr:
        lines = csr.readlines()
        if lines[0].strip() != '-----BEGIN CERTIFICATE REQUEST-----' or \
            lines[len(lines)-1].strip() != '-----END CERTIFICATE REQUEST-----':
            return 'File "%s" does not appear to be a valid CSR' % p
    return None


def get_property(properties, key, prompt, allowed_values=[], allow_empty=False, validator=None):
    default = properties.get(key, None)
    full_prompt = prompt
    if len(allowed_values):
        full_prompt = '%s (%s)' % (full_prompt, ','.join(allowed_values))
    if default:
        full_prompt = '%s [%s]' % (full_prompt, default)
    full_prompt += ': '
    p = None
    while not p:
        p = input(full_prompt)
        if default and p == '':
            p = default
        if p == '' and allow_empty:
            break
        if len(allowed_values) and not p in allowed_values:
            print('Illegal input "%s" - valid values are %s' % (p, ','.join(allowed_values)))
            p = None
        if p and validator:
            msg = validator(p, properties)
            if msg:
                print(msg)
                p = None
    return p


def save_properties(properties, path):
    dir = dirname(path)
    if not exists(dir):
        makedirs(dir)
    with open(path, 'w') as pf:
        pf.writelines(['%s:%s\n' % (k, v) for k, v in list(properties.items())])


def get_properties(cmd):
    propsfile = '%s/.digicert/.digicert_procure_testclient.properties' % expanduser('~')
    properties = read_default_properties(propsfile)

    properties['customer_account_id'] = get_property(properties, 'customer_account_id', 'Customer Account Id', allow_empty=True)
    properties['customer_api_key'] = get_property(properties, 'customer_api_key', 'Customer API Key')
    properties['host'] = get_property(properties, 'host', 'Hostname')

    if 'order' == cmd:
        properties['certificate_type'] = get_property(properties,
                                                      'certificate_type',
                                                      'Certificate Type',
                                                      [certtype for certtype in CertificateType()])
        properties['validity'] = get_property(properties,
                                              'validity',
                                              'Validity Period',
                                              ['%d' % period for period in Validity()],
                                              validate_certificate_validity)
        properties['common_name'] = get_property(properties, 'common_name', 'Common Name')
        properties['org_name'] = get_property(properties, 'org_name', 'Organization Name')
        properties['org_addr1'] = get_property(properties, 'org_addr1', 'Organization Address')
        properties['org_city'] = get_property(properties, 'org_city', 'Organization City')
        properties['org_state'] = get_property(properties, 'org_state', 'Organization State', validator=validate_two_chars)
        properties['org_zip'] = get_property(properties, 'org_zip', 'Organization Zip Code', validator=validate_zip)
        properties['org_country'] = get_property(properties, 'org_country', 'Organization Country', validator=validate_two_chars)
        properties['org_contact_firstname'] = get_property(properties,
                                                             'org_contact_firstname',
                                                             'Organization Contact First Name')
        properties['org_contact_lastname'] = get_property(properties,
                                                            'org_contact_lastname',
                                                            'Organization Contact Last Name')
        properties['org_contact_email'] = get_property(properties,
                                                         'org_contact_email',
                                                         'Organization Contact Email')
        properties['org_contact_telephone'] = get_property(properties,
                                                             'org_contact_telephone',
                                                             'Organization Contact Telephone',
                                                             validator=validate_telephone)
        properties['csr_path'] = get_property(properties, 'csr_path', 'Path to CSR file', validator=validate_csr_path)

        if properties['certificate_type'] == CertificateType.EVSSL or \
            properties['certificate_type'] == CertificateType.EVMULTI:
            properties['telephone'] = properties['org_contact_telephone']
            properties['org_contact_job_title'] = get_property(properties,
                                                               'org_contact_job_title',
                                                               'Organization Contact Job Title')

    save_properties(properties, propsfile)

    if 'customer_account_id' not in properties or 0 == len(properties['customer_account_id']):
        properties['customer_account_id'] = None

    return properties


def order_certificate(properties):
    csr = None
    with open(properties['csr_path']) as csr_file:
        csr = ''.join(csr_file.readlines()[1:-1]).strip()

    order = CertificateOrder(host=properties['host'],
                  customer_api_key=properties['customer_api_key'],
                  customer_name=properties['customer_account_id'],
                  conn=(None if use_verified_http else HTTPSConnection(properties['host'])))
    order_params = dict(list({'csr': csr}.items()) + list(properties.items()))
    del order_params['customer_account_id']
    del order_params['customer_api_key']
    response = order.place(**order_params)
    print(response)


def view_certificate(order_id, properties):
    order = CertificateOrder(host=properties['host'],
                  customer_api_key=properties['customer_api_key'],
                  customer_name=properties['customer_account_id'],
                  conn=(None if use_verified_http else HTTPSConnection(properties['host'])))
    response = order.view(order_id=order_id)
    print(response)


def download_certificate(order_id, properties):
    order = CertificateOrder(host=properties['host'],
                  customer_api_key=properties['customer_api_key'],
                  customer_name=properties['customer_account_id'],
                  conn=(None if use_verified_http else HTTPSConnection(properties['host'])))
    response = order.download(order_id=order_id)
    print(response)


if __name__ == '__main__':
    if len(argv) < 2:
        usage()

    if argv[1] == 'order':
        order_certificate(get_properties(argv[1]))
    elif argv[1] == 'view':
        if len(argv) < 3:
            usage()
        view_certificate(argv[2], get_properties(argv[1]))
    elif argv[1] == 'download':
        if len(argv) < 3:
            usage()
        download_certificate(argv[2], get_properties(argv[1]))
    else:
        usage()
