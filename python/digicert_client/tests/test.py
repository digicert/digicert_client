__author__ = 'jfischer'

from digicert_client import CertificateOrder


def list_duplicates(order_id):
    order = CertificateOrder(host='localhost.digicert.com',
                  customer_api_key='CJYBV43GXF4JEXNCWKIDQ4H62DDOZJEU3IP4S44D6EZIL64R3E65YZHQX5BH6T62BIB25FXVGWR3ND4S6',
                  customer_name='')
    return order.list_duplicates(digicert_order_id=order_id)


def view_duplicate(order_id, sub_id):
    order = CertificateOrder(host='localhost.digicert.com',
                  customer_api_key='CJYBV43GXF4JEXNCWKIDQ4H62DDOZJEU3IP4S44D6EZIL64R3E65YZHQX5BH6T62BIB25FXVGWR3ND4S6')
    return order.download_duplicate(digicert_order_id=order_id, sub_id=sub_id)


def create_duplicate(order_id, properties):
    order = CertificateOrder(host='localhost.digicert.com',
                  customer_api_key='CJYBV43GXF4JEXNCWKIDQ4H62DDOZJEU3IP4S44D6EZIL64R3E65YZHQX5BH6T62BIB25FXVGWR3ND4S6')
    return order.create_duplicate(digicert_order_id=order_id, **properties)


if __name__ == '__main__':
    # print list_duplicates('00687308')

    # print view_duplicate('00687308', '001')

    properties = {"certificate":{"common_name":"test2.nocsr.com", "csr":"-----BEGIN CERTIFICATE REQUEST-----MIICnjCCAYYCAQAwWTELMAkGA1UEBhMCVVMxDTALBgNVBAgMBFV0YWgxDjAMBgNVBAcMBXByb3ZvMRUwEwYDVQQKDAxkaWdpY2VydCBpbmMxFDASBgNVBAMMC3lvdS5tYXguY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Y+FJGm4VrgVc1JUbVWiooM20TrqS+dmkabh80BPWFEfXUHbXeLAjXOgLworMnEFSLJiCSuZQndleHCUHW/3+hyDsSwhEmpdjUXHEqVhVEmSBLc478PMKGQNi2snpf3VSBdpNbnrADsZOfQxbkPnh7yy5yQYiLGv4ibFPT3rVKd2XzbHwz49mhAT8yF261/Kge7ES/N979554ftaLusSiN7Z1WKsmp/k1niA8b6AD2jmlfJ9FSwFd7yfcIexrNiXHNlp/qHq8vWs7jeknb2lrrLPejrwfLc4ZG6nwF6QUju69nC3ywjKfDM2UpDfqOYKL9jVM4kh2yKcNzS17DhaHQIDAQABoAAwDQYJKoZIhvcNAQEFBQADggEBAFJxj8AiDAL1Vda/N5eGNP3ZZ382Y8YwXcAlcvID8eQlUz7IjJLRgMRYURZBc9dsN04gyLDvGZapAvyQpQ0s8UHwTJpYhqEIuCOHJCcq4aVMHZFs/92r6I+tpo6VkpkyLR22tOPV+XJMKvYRoE1MZpP4suFpPRo+oCAQOl0i2/t+sHRzqig/JqRLC3DxypNmh3YnF3Q4W9jIoaNhmeMaeq815GMZj5hUFKHZdXdRGib2xi4i2Kv8gyExqrFw8B7WbYrlokC8ab+nWr+4VundLsetAq44TVoFZwty69i7RcXhpjzDpGqaF0CWIgj1YpjKvqXZtcTS8YabfcQVkaLXczQ=-----END CERTIFICATE request-----", "dns_names":["test2.nocsr.com"], "signature_hash":"sha256", "server_platform":{"id":-1}}}
    result = create_duplicate('00687308', properties)
    print result




# {
#    u'certificates':[
#       {
#          u'status':u'approved',
#          u'valid_till':u'2016-05-24',
#          u'valid_from':u'2015-05-20',
#          u'key_size':2048,
#          u'sub_id':u'001',
#          u'signature_hash':u'sha256',
#          u'server_platform':{
#             u'csr_url':            u'http://www.digicert.com/csr-creation.htm',
#             u'install_url':            u'http://www.digicert.com/SSL-certificate-installation.htm',
#             u'id':u'-1',
#             u'name':u'OTHER'
#          },
#          u'thumbprint':u'BBDAFC532FDAA4E42CFADE1C74759EA89621D68B',
#          u'date_created':         u'2015-06-02T20:42:19+00:00         ', u'         ca_cert_id':u'68',
#          u'dns_names':[
#             u'*.nocsr.com',
#             u'nocsr.com'
#          ],
#          u'common_name':u'*.nocsr.com',
#          u'serial_number':u'0511CED6848DD49E02CBB8CE0D40C9E5',
#          u'csr':u'"""-----BEGIN CERTIFICATE REQUEST-----MIICnjCCAYYCAQAwWTELMAkGA1UEBhMCVVMxDTALBgNVBAgMBFV0YWgxDjAMBgNVBAcMBXByb3ZvMRUwEwYDVQQKDAxkaWdpY2VydCBpbmMxFDASBgNVBAMMC3lvdS5tYXguY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Y+FJGm4VrgVc1JUbVWiooM20TrqS+dmkabh80BPWFEfXUHbXeLAjXOgLworMnEFSLJiCSuZQndleHCUHW/3+hyDsSwhEmpdjUXHEqVhVEmSBLc478PMKGQNi2snpf3VSBdpNbnrADsZOfQxbkPnh7yy5yQYiLGv4ibFPT3rVKd2XzbHwz49mhAT8yF261/Kge7ES/N979554ftaLusSiN7Z1WKsmp/k1niA8b6AD2jmlfJ9FSwFd7yfcIexrNiXHNlp/qHq8vWs7jeknb2lrrLPejrwfLc4ZG6nwF6QUju69nC3ywjKfDM2UpDfqOYKL9jVM4kh2yKcNzS17DhaHQIDAQABoAAwDQYJKoZIhvcNAQEFBQADggEBAFJxj8AiDAL1Vda/N5eGNP3ZZ382Y8YwXcAlcvID8eQlUz7IjJLRgMRYURZBc9dsN04gyLDvGZapAvyQpQ0s8UHwTJpYhqEIuCOHJCcq4aVMHZFs/92r6I+tpo6VkpkyLR22tOPV+XJMKvYRoE1MZpP4suFpPRo+oCAQOl0i2/t+sHRzqig/JqRLC3DxypNmh3YnF3Q4W9jIoaNhmeMaeq815GMZj5hUFKHZdXdRGib2xi4i2Kv8gyExqrFw8B7WbYrlokC8ab+nWr+4VundLsetAq44TVoFZwty69i7RcXhpjzDpGqaF0CWIgj1YpjKvqXZtcTS8YabfcQVkaLXczQ=-----END CERTIFICATE yrequest-----"""'
#       }
#    ]
# }
#
#
#     {u'certificates': [{u'status': u'approved', u'valid_till': u'2016-05-24', u'valid_from': u'2015-05-20', u'key_size': 2048, u'sub_id': u'001', u'signature_hash': u'sha256', u'server_platform': {u'csr_url': u'http://www.digicert.com/csr-creation.htm', u'install_url': u'http://www.digicert.com/SSL-certificate-installation.htm', u'id': u'-1', u'name': u'OTHER'}, u'thumbprint': u'BBDAFC532FDAA4E42CFADE1C74759EA89621D68B', u'date_created': u'2015-06-02T20:42:19+00:00', u'ca_cert_id': u'68', u'dns_names': [u'*.nocsr.com', u'nocsr.com'], u'common_name': u'*.nocsr.com', u'serial_number': u'0511CED6848DD49E02CBB8CE0D40C9E5', u'csr': u'"""-----BEGIN CERTIFICATE REQUEST-----MIICnjCCAYYCAQAwWTELMAkGA1UEBhMCVVMxDTALBgNVBAgMBFV0YWgxDjAMBgNVBAcMBXByb3ZvMRUwEwYDVQQKDAxkaWdpY2VydCBpbmMxFDASBgNVBAMMC3lvdS5tYXguY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Y+FJGm4VrgVc1JUbVWiooM20TrqS+dmkabh80BPWFEfXUHbXeLAjXOgLworMnEFSLJiCSuZQndleHCUHW/3+hyDsSwhEmpdjUXHEqVhVEmSBLc478PMKGQNi2snpf3VSBdpNbnrADsZOfQxbkPnh7yy5yQYiLGv4ibFPT3rVKd2XzbHwz49mhAT8yF261/Kge7ES/N979554ftaLusSiN7Z1WKsmp/k1niA8b6AD2jmlfJ9FSwFd7yfcIexrNiXHNlp/qHq8vWs7jeknb2lrrLPejrwfLc4ZG6nwF6QUju69nC3ywjKfDM2UpDfqOYKL9jVM4kh2yKcNzS17DhaHQIDAQABoAAwDQYJKoZIhvcNAQEFBQADggEBAFJxj8AiDAL1Vda/N5eGNP3ZZ382Y8YwXcAlcvID8eQlUz7IjJLRgMRYURZBc9dsN04gyLDvGZapAvyQpQ0s8UHwTJpYhqEIuCOHJCcq4aVMHZFs/92r6I+tpo6VkpkyLR22tOPV+XJMKvYRoE1MZpP4suFpPRo+oCAQOl0i2/t+sHRzqig/JqRLC3DxypNmh3YnF3Q4W9jIoaNhmeMaeq815GMZj5hUFKHZdXdRGib2xi4i2Kv8gyExqrFw8B7WbYrlokC8ab+nWr+4VundLsetAq44TVoFZwty69i7RcXhpjzDpGqaF0CWIgj1YpjKvqXZtcTS8YabfcQVkaLXczQ=-----END CERTIFICATE yrequest-----"""'}]}
# None
# None