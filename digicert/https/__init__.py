#!/usr/bin/env python

import socket
import ssl
import os
from httplib import HTTPSConnection


class VerifiedHTTPSConnection(HTTPSConnection):
    """
    VerifiedHTTPSConnection - an HTTPSConnection that performs name and server cert verification
    when a connection is created.
    """

    # This code is based very closely on https://gist.github.com/Caligatio/3399114.

    ca_file = None

    def __init__(self,
                 host,
                 port=None,
                 ca_file=None,
                 **kwargs):
        HTTPSConnection.__init__(self,
                                 host=host,
                                 port=port,
                                 **kwargs)

        if ca_file:
            self.ca_file = ca_file
        else:
            self.ca_file = os.path.join(os.path.dirname(__file__), 'DigiCertRoots.pem')

    def connect(self):
        if self.ca_file and os.path.exists(self.ca_file):
            sock = socket.create_connection(
                (self.host, self.port),
                self.timeout, self.source_address
            )

            if self._tunnel_host:
                self.sock = sock
                self._tunnel()

            # Wrap the socket using verification with the root certs, note the hardcoded path
            self.sock = ssl.wrap_socket(sock,
                                        self.key_file,
                                        self.cert_file,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=self.ca_file)
            self.check_hostname()
        else:
            raise RuntimeError('No CA file configured for VerifiedHTTPSConnection')

    def check_hostname(self):
        """
        check_hostname()

        Checks the hostname being accessed against the various hostnames present
        in the remote certificate
        """
        hostnames = set()
        cert = self.sock.getpeercert()

        for subject in cert['subject']:
            if 'commonName' == subject[0][0]:
                hostnames.add(subject[0][1].encode('utf-8'))

        # Get the subject alternative names out of the certificate
        try:
            sans = (x for x in cert['subjectAltName'] if x[0] == 'DNS')
            for san in sans:
                hostnames.add(san[1])
        except KeyError:
            pass

        if self.host not in hostnames:
            raise ssl.SSLError("hostname '%s' doesn't match certificate name(s) '%s'" %
                               (self.host, ', '.join(hostnames)))

if __name__ == '__main__':
    pass
